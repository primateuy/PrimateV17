from odoo import models, fields, api, _
from typing import Any, Dict, List, Tuple

ACCOUNT_PAYMENT_MOVE_LINE_FIELDS: List[str] = [
    "account_id",
    "amount_currency",
    "balance",
    "company_id",
    "company_currency_id",
    "currency_id",
    "debit",
    "credit",
    "id",
    "name",
    "move_id",
    "payment_id",
    "price_unit",
    "product_id",
    "quantity",
]


class Company(models.Model):
    _inherit = "res.company"

    old_id = fields.Integer(string="Old ID", copy=False)


class ResCountry(models.Model):
    _inherit = "res.country"

    old_id = fields.Integer(string="Old ID", copy=False)


class ResCountryState(models.Model):
    _inherit = "res.country.state"

    old_id = fields.Integer(string="Old ID", copy=False)


class ResPartner(models.Model):
    _inherit = "res.partner"

    old_id = fields.Integer(string="Old ID", copy=False)


class ResPartnerTitle(models.Model):
    _inherit = "res.partner.title"

    old_id = fields.Integer(string="Old ID", copy=False)


class ResUsers(models.Model):
    _inherit = "res.users"

    old_id = fields.Integer(string="Old ID", copy=False)


class ResCurrency(models.Model):
    _inherit = "res.currency"

    old_id = fields.Integer(string="Old ID", copy=False)


class ResCurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    old_id = fields.Integer(string="Old ID", copy=False)


class AccountAccount(models.Model):
    _inherit = "account.account"

    old_id = fields.Integer(string="Old ID", copy=False)


class AccountJournal(models.Model):
    _inherit = "account.journal"

    old_id = fields.Integer(string="Old ID", copy=False)


class ProductCategory(models.Model):
    _inherit = "product.category"

    old_id = fields.Integer(string="Old ID", copy=False)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    old_id = fields.Integer(string="Old ID", copy=False)


class ProductProduct(models.Model):
    _inherit = "product.product"

    old_id = fields.Integer(string="Old ID", copy=False)


class AccountMove(models.Model):
    _inherit = "account.move"

    old_id = fields.Integer(string="Old ID", copy=False)
    old_name = fields.Char(string="Name", copy=False)
    old_full_reconcile_ids = fields.Char(string="Full reconcile IDs on old DB", copy=False)
    old_state = fields.Selection(selection=[("draft", "Draft"), ("open", "Posted"), ("cancel", "Cancelled"), ("paid", "Pago"), ("posted", "Publicado"), ("reconciled", "Reconcilado")], copy=False)
    migration_error = fields.Boolean(string="Migration Error", copy=False)
    no_post_migrator = fields.Boolean(string="No post move in migration", copy=False)

    def _must_check_constrains_date_sequence(self):
        ctx = self.env.context.copy()
        if ctx.get('dont_check_constrains_date_sequence', False):
            return False
        return super()._must_check_constrains_date_sequence()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    invoice_old_id = fields.Integer(string="Invoice Line Old ID", copy=False)
    old_id = fields.Integer(string="Old ID", copy=False)
    move_version = fields.Selection(selection=[("old_move", "Old Move"), ("new_move", "New Move")], default="old_move", copy=False)

    @api.constrains('account_id', 'display_type')
    def _check_payable_receivable(self):
        if self._context.get('check_move_validity', True):
            super(AccountMoveLine, self)._check_payable_receivable()

    def _check_constrains_account_id_journal_id(self):
        if not self._context.get('from_migrator', False):
            super(AccountMoveLine, self)._check_constrains_account_id_journal_id()


class AccountPayment(models.Model):
    _inherit = "account.payment"

    old_id = fields.Integer(string="Old ID", copy=False)
    old_name = fields.Char(string="Name", copy=False)
    old_full_reconcile_ids = fields.Char(string="Full reconcile IDs on old DB", copy=False)

    def action_post(self):
        ctx = self.env.context.copy()
        from_migrator = ctx.get('from_migrator', False)
        print(self)
        if from_migrator:
            """
            aca hacemos la magia
            """
            self.ensure_one()
            self.name = self.old_name
            model_name = "account.move.line"
            migrator = ctx.get('migrator')
            move_line_datas = migrator._run_remote_command_for(
                model_name=model_name,
                operation_params_list=[("payment_id", "=", self.old_id), ("journal_id", "=", self.journal_id.old_id)],
                command_params_dict={
                    "fields": ACCOUNT_PAYMENT_MOVE_LINE_FIELDS,
                },
            )
            move_id = False
            move_values = {'line_ids': []}
            for move_line in move_line_datas:
                value = {}
                transfer_line = self.move_id.line_ids.filtered(lambda line: line.credit if move_line.get('balance') < 0 else line.debit)
                if not transfer_line:
                    import ipdb
                    ipdb.set_trace()
                    print('Problemaaas')
                move_id = move_line.get('move_id')[0]
                value['old_id'] = move_line.get('id')
                old_account_id = move_line.get('account_id', False)
                account_id = transfer_line.account_id.search([('old_id', '=', old_account_id[0])]) if old_account_id else False
                if account_id:
                    value['account_id'] = account_id.id
                debit = move_line.get('debit')
                credit = move_line.get('credit')
                amount_currency = move_line.get('amount_currency')
                if debit != transfer_line.debit or credit != transfer_line.credit:
                    value['debit'] = debit
                    value['credit'] = credit
                if amount_currency and amount_currency != transfer_line.amount_currency and self.currency_id != self.company_currency_id:
                    value['amount_currency'] = amount_currency
                move_values['line_ids'].append((1, transfer_line.id, value))

            if move_values != {'line_ids': []}:
                self.move_id.write(move_values)
            if move_id:
                self.move_id.old_id = move_id

        return super(AccountPayment, self).action_post()

    def _create_paired_internal_transfer_payment(self):
        for payment in self:
            ctx = self.env.context.copy()
            from_migrator = ctx.get('from_migrator', False)
            if from_migrator:
                # NATIVO
                paired_payment = payment.copy({
                    'journal_id': payment.destination_journal_id.id,
                    'destination_journal_id': payment.journal_id.id,
                    'payment_type': payment.payment_type == 'outbound' and 'inbound' or 'outbound',
                    'move_id': None,
                    'ref': payment.ref,
                    'paired_internal_transfer_payment_id': payment.id,
                    'date': payment.date,
                })
                paired_payment.name = payment.old_name + '/PAIRED'
                # SOLUCION MIGRADOR
                model_name = "account.move.line"
                migrator = ctx.get('migrator')
                move_line_datas = migrator._run_remote_command_for(
                    model_name=model_name,
                    operation_params_list=[("payment_id", "=", payment.old_id),
                                           ("journal_id", "=", paired_payment.journal_id.old_id)],
                    command_params_dict={
                        "fields": ACCOUNT_PAYMENT_MOVE_LINE_FIELDS,
                    },
                )
                move_id = False
                move_values = {'line_ids': []}
                change_values = False
                new_amount_currency = 0
                new_debit = 0
                new_credit = 0
                new_currency_id = 0
                for move_line in move_line_datas:
                    value = {}
                    transfer_line = paired_payment.move_id.line_ids.filtered(lambda line: line.credit if move_line.get('balance') < 0 else line.debit)
                    if not transfer_line:
                        import ipdb
                        ipdb.set_trace()
                        print('Problemaaas')
                    move_id = move_line.get('move_id')[0]
                    value['old_id'] = move_line.get('id')
                    old_account_id = move_line.get('account_id', False)
                    account_id = transfer_line.account_id.search(
                        [('old_id', '=', old_account_id[0])]) if old_account_id else False
                    if account_id:
                        value['account_id'] = account_id.id
                    debit = move_line.get('debit')
                    credit = move_line.get('credit')
                    amount_currency = move_line.get('amount_currency')
                    if debit != transfer_line.debit or credit != transfer_line.credit:
                        value['debit'] = debit
                        value['credit'] = credit
                    if amount_currency and amount_currency != transfer_line.amount_currency and paired_payment.currency_id != paired_payment.company_currency_id:
                        value['amount_currency'] = amount_currency
                        move_currency = paired_payment.currency_id.search([('old_id', '=', move_line.get('currency_id')[0])])
                        if move_currency and move_currency != paired_payment.currency_id:
                            value['currency_id'] = move_currency.id
                            value['debit'] = debit
                            value['credit'] = credit
                            change_values = True
                            new_amount_currency = amount_currency
                            new_currency_id = move_currency.id
                            new_debit = debit
                            new_credit = credit
                    move_values['line_ids'].append((1, transfer_line.id, value))

                if change_values:
                    for line in move_values['line_ids']:
                        data_line = line[2]
                        if data_line.get('amount_currency', 0) != new_amount_currency and data_line.get('currency_id', False) != new_currency_id:
                            data_line['currency_id'] = new_currency_id
                            data_line['amount_currency'] = -new_amount_currency
                            data_line['debit'] = new_credit
                            data_line['credit'] = new_debit
                if move_values != {'line_ids': []}:
                    paired_payment.move_id.write(move_values)
                if move_id:
                    paired_payment.move_id.old_id = move_id

                # CONTINUA NATIVO
                paired_payment.move_id._post(soft=False)
                payment.paired_internal_transfer_payment_id = paired_payment
                body = _("This payment has been created from:") + payment._get_html_link()
                paired_payment.message_post(body=body)
                body = _("A second payment has been created:") + paired_payment._get_html_link()
                payment.message_post(body=body)

                lines = (payment.move_id.line_ids + paired_payment.move_id.line_ids).filtered(
                    lambda l: l.account_id == payment.destination_account_id and not l.reconciled)
                lines.reconcile()
            else:
                return super(AccountPayment, self)._create_paired_internal_transfer_payment()

class AccountFullReconcile(models.Model):
    _inherit = "account.full.reconcile"

    old_id = fields.Integer(string="Old ID", copy=False)


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    old_id = fields.Integer(string="Old ID", copy=False)


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    old_id = fields.Integer(string="Old ID", copy=False)


class AccountTax(models.Model):
    _inherit = "account.tax"

    old_id = fields.Integer(string="Old ID", copy=False)


class AccountTaxGroup(models.Model):
    _inherit = "account.tax.group"

    old_id = fields.Integer(string="Old ID", copy=False)

class AccountAnalyticTag(models.Model):
    _inherit = "account.analytic.tag"

    old_id = fields.Integer(string="Old ID", copy=False)
