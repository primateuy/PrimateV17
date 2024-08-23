from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    always_internal_transfer = fields.Boolean()
    counter_part_internal_transfer = fields.Boolean()
    check_rate = fields.Boolean()
    rate_exchange = fields.Float()
    local_currency_price = fields.Monetary()
    lines_count = fields.Integer(compute='_get_lines_count')
    aux_payment_type = fields.Selection([('outbound', 'Send'), ('inbound', 'Receive'), ], string='Aux Payment Type')
    aux_l10n_latam_check_number = fields.Char(string='Aux Check Number')
    aux_l10n_latam_check_bank_id = fields.Many2one(comodel_name='res.bank', string='Aux Check Bank')
    aux_l10n_latam_check_issuer_vat = fields.Char(string='Aux Check Issuer VAT')
    aux_l10n_latam_check_payment_date = fields.Date(string='Aux Check Cash-In Date')
    amount_company_currency = fields.Monetary(
        string='Amount on Company Currency',
        compute='_compute_amount_company_currency',
        inverse='_inverse_amount_company_currency',
        currency_field='company_currency_id',
    )
    force_amount_company_currency = fields.Monetary(
        string='Forced Amount on Company Currency',
        currency_field='company_currency_id',
        copy=False,
    )
    exchange_rate = fields.Float(
        string='Exchange Rate',
        compute='_compute_exchange_rate',
        # readonly=False,
        # inverse='_inverse_exchange_rate',
        digits=(16, 4),
    )

    @api.depends('amount', 'other_currency', 'amount_company_currency')
    def _compute_exchange_rate(self):
        for rec in self:
            if rec.other_currency:
                rec.exchange_rate = rec.amount and (
                    rec.amount_company_currency / rec.amount) or 0.0
            else:
                rec.exchange_rate = False

    @api.depends('amount', 'other_currency', 'force_amount_company_currency')
    def _compute_amount_company_currency(self):
        """
        * Si las monedas son iguales devuelve 1
        * si no, si hay force_amount_company_currency, devuelve ese valor
        * sino, devuelve el amount convertido a la moneda de la cia
        """
        for rec in self:
            if not rec.other_currency:
                amount_company_currency = rec.amount
            elif rec.force_amount_company_currency:
                amount_company_currency = rec.force_amount_company_currency
            else:
                amount_company_currency = rec.currency_id._convert(
                    rec.amount, rec.company_id.currency_id,
                    rec.company_id, rec.date)
            rec.amount_company_currency = amount_company_currency

    @api.onchange('amount_company_currency')
    def _inverse_amount_company_currency(self):

        for rec in self:
            if rec.other_currency and rec.amount_company_currency != \
                    rec.currency_id._convert(
                        rec.amount, rec.company_id.currency_id,
                        rec.company_id, rec.date):
                force_amount_company_currency = rec.amount_company_currency
            else:
                force_amount_company_currency = False
            rec.force_amount_company_currency = force_amount_company_currency


    def _get_payment_method_codes_to_exclude(self):
        res = super()._get_payment_method_codes_to_exclude()
        if 'new_third_party_checks' in res:
            res.remove('new_third_party_checks')
        return res

    @api.depends('move_id', 'paired_internal_transfer_payment_id')
    def _get_lines_count(self):
        self.ensure_one()
        if self.is_internal_transfer:
            line_ids = self.move_id.line_ids
            if self.paired_internal_transfer_payment_id:
                line_ids += self.paired_internal_transfer_payment_id.move_id.line_ids
            self.lines_count = len(line_ids)
        else:
            self.lines_count = len(self.move_id.line_ids)

    def action_open_move_lines(self):
        ''' Redirect the user to this payment journal.
                :return:    An action on account.move.
                '''
        self.ensure_one()
        if self.is_internal_transfer:
            line_ids = self.move_id.line_ids
            if self.paired_internal_transfer_payment_id:
                line_ids += self.paired_internal_transfer_payment_id.move_id.line_ids
            return {
                'name': _("Journal Entries"),
                'type': 'ir.actions.act_window',
                'res_model': 'account.move.line',
                'context': {'create': False},
                'view_mode': 'tree,form',
                'domain': [('id', 'in', line_ids.ids)],
            }
        else:
            return {
                'name': _("Journal Entries"),
                'type': 'ir.actions.act_window',
                'res_model': 'account.move.line',
                'context': {'create': False},
                'view_mode': 'tree,form',
                'domain': [('id', 'in', self.move_id.line_ids.ids)],
            }

    @api.onchange('amount', 'rate_exchange', 'check_rate')
    def currency_price(self):
        self.ensure_one()
        if self.check_rate:
            if self.rate_exchange:
                if not self.get_current_invoice_currency():
                    self.local_currency_price = None
                else:
                    self.local_currency_price = self.rate_exchange * self.amount
        else:
            self.local_currency_price = None

    @api.onchange('currency_id')
    def onchange_currency_id(self):
        self.ensure_one()
        if self.check_rate and self.rate_exchange:
            if not self.get_current_invoice_currency():
                self.local_currency_price = None
            else:
                self.local_currency_price = self.rate_exchange * self.amount
        else:
            if not self.get_current_invoice_currency():
                self.local_currency_price = None

    # - obtener la moneda que esta trabajando el invoice, saber si es diferente a la que tiene por defecto la empresa
    def get_current_invoice_currency(self):
        self.ensure_one()
        other_currency = False
        if self.company_id.currency_id.id != self.currency_id.id:
            other_currency = True
        return other_currency

    def action_post(self):
        ''' draft -> posted '''
        move_ids = []
        for rec in self:
            if rec.is_internal_transfer:
                move_values = {'line_ids': []}
                if self.env['ir.module.module'].search([('name', '=', 'account_payment_group_extension'), ('state', '=', 'installed')]):
                    partner_type = rec.payment_group_id.partner_type if rec.payment_group_id else rec.partner_type
                    if rec.payment_group_id:
                        rec.date = rec.payment_group_id.payment_date
                else:
                    partner_type = rec.partner_type
                normal_payment = (partner_type == 'customer' and rec.payment_type == 'inbound') or (partner_type == 'supplier' and rec.payment_type == 'outbound')
                currency_id = rec.journal_id.currency_id or rec.journal_id.company_id.currency_id
                company_currency_id = rec.company_currency_id
                if rec.currency_id != company_currency_id:
                    if rec.check_rate and rec.rate_exchange:
                        local_currency = rec.amount * rec.rate_exchange
                    else:
                        local_currency = rec.amount_company_currency
                    foreign_amount = rec.amount
                else:
                    local_currency = rec.amount
                    if rec.check_rate and rec.rate_exchange:
                        foreign_amount = rec.amount / rec.rate_exchange
                    else:
                        if company_currency_id != currency_id:
                            foreign_currency = currency_id
                        elif rec.destination_journal_id.currency_id != currency_id:
                            foreign_currency = rec.destination_journal_id.currency_id
                        else:
                            foreign_currency = rec.currency_id
                        foreign_amount = company_currency_id._convert(rec.amount, foreign_currency,
                                                                      rec.company_id, rec.date)
                if company_currency_id != currency_id:
                    amount_company_currency = local_currency
                    amount = foreign_amount
                else:
                    amount_company_currency = local_currency
                    amount = local_currency

                for line in rec.move_id.line_ids:
                    value = {}
                    if line == rec.move_id.line_ids[0]:
                        if currency_id != rec.company_currency_id:
                            value['amount_currency'] = -amount
                            value['currency_id'] = currency_id.id
                        else:
                            value['amount_currency'] = -amount_company_currency
                            value['currency_id'] = rec.company_currency_id.id
                        if self.env['ir.module.module'].search([('name', '=', 'account_payment_group_extension'), ('state', '=', 'installed')]) and (
                                rec.payment_group_id.partner_type == 'supplier' or not rec.payment_group_id):
                            journal_id = rec.journal_id
                            payment_method = rec.payment_method_line_id
                            if rec.journal_id == rec.currency_id.multiple_payments_journal_id:
                                apml_obj = self.env['account.payment.method.line']
                                journal_id = rec.destination_journal_id
                                payment_method = apml_obj.search(
                                    [('payment_method_id', '=', rec.payment_method_id.id),
                                     ('journal_id', '=', rec.destination_journal_id.id)])
                            payment_method_account = payment_method.payment_account_id if payment_method else False
                            if rec.payment_group_id or rec.payment_type == 'outbound':
                                payment_account = payment_method_account or journal_id.company_id.account_journal_payment_credit_account_id
                            else:
                                payment_account = payment_method_account or journal_id.company_id.account_journal_payment_debit_account_id
                            value['account_id'] = payment_account.id
                        else:
                            value['account_id'] = rec.journal_id.default_account_id.id
                        value['check_rate'] = rec.check_rate
                        value['rate_exchange'] = rec.rate_exchange
                        if normal_payment:
                            value['debit'] = 0
                            value['credit'] = amount_company_currency
                        else:
                            value['debit'] = amount_company_currency
                            value['credit'] = 0
                            value['amount_currency'] = -value['amount_currency']
                    else:
                        transfer_account_id = rec.journal_id.company_id.transfer_account_id
                        if not transfer_account_id:
                            raise ValidationError(_('No se encontró cuenta de transferencia interna en la compañía.'))
                        if currency_id != rec.company_currency_id:
                            value['amount_currency'] = amount
                            value['currency_id'] = currency_id.id
                        else:
                            value['amount_currency'] = amount_company_currency
                            value['currency_id'] = rec.company_currency_id.id
                        value['account_id'] = transfer_account_id.id
                        value['check_rate'] = rec.check_rate
                        value['rate_exchange'] = rec.rate_exchange
                        if normal_payment:
                            value['debit'] = amount_company_currency
                            value['credit'] = 0
                        else:
                            value['debit'] = 0
                            value['credit'] = amount_company_currency
                            value['amount_currency'] = -value['amount_currency']

                    move_values['line_ids'].append((1, line.id, value))
                rec.aux_payment_type = rec.payment_type
                rec.move_id.write(move_values)
                move_ids = rec.move_id
        res = super(AccountPayment, self).action_post()

        for rec in self:
            if rec.is_internal_transfer:
                if rec.paired_internal_transfer_payment_id:
                    move_ids += rec.paired_internal_transfer_payment_id.move_id
                move_ids.write({'transfer_move': 1})
        return res

    def _create_paired_internal_transfer_payment(self):
        ''' When an internal transfer is posted, a paired payment is created
        with opposite payment_type and swapped journal_id & destination_journal_id.
        Both payments liquidity transfer lines are then reconciled.
        '''
        for payment in self:
            group_extension_installed = self.env['ir.module.module'].search([('name', '=', 'account_payment_group_extension'), ('state', '=', 'installed')])
            if payment.journal_id.currency_id != payment.destination_journal_id.currency_id:
                if payment.currency_id != payment.company_currency_id:
                    if payment.check_rate:
                        amount = payment.amount * payment.rate_exchange
                    else:
                        amount = payment.currency_id._convert(payment.amount, payment.company_currency_id,payment.company_id, payment.date)
                else:
                    amount = payment.company_currency_id._convert(payment.amount,payment.destination_journal_id.currency_id,payment.company_id, payment.date)
                    if group_extension_installed and payment.payment_group_id and payment.aux_amount:
                        amount = payment.aux_amount
                # Si es transferencia interna recalculo precio local por si hay cotizacion especifica
                if not payment.payment_group_id:
                    amount = payment.amount_company_currency
            else:
                amount = payment.amount
            payment_destination_currency_id = payment.destination_journal_id.currency_id or payment.destination_journal_id.company_id.currency_id
            paired_payment = payment.copy({
                'journal_id': payment.destination_journal_id.id,
                'destination_journal_id': payment.journal_id.id,
                'currency_id': payment_destination_currency_id.id,
                'amount': amount,
                'payment_type': payment.aux_payment_type == 'outbound' and 'inbound' or 'outbound',
                'move_id': False,
                'ref': payment.ref,
                'paired_internal_transfer_payment_id': payment.id,
                'date': payment.date,
            })
            move_values = {'line_ids': []}
            currency_id = paired_payment.journal_id.currency_id or paired_payment.journal_id.company_id.currency_id
            company_currency_id = paired_payment.company_currency_id
            local_currency = abs(payment.move_id.line_ids[0].balance)
            if group_extension_installed and payment.payment_group_id:
                normal_payment = (payment.payment_group_id.partner_type == 'customer' and payment.aux_payment_type == 'inbound') or (payment.payment_group_id.partner_type == 'supplier' and payment.aux_payment_type == 'outbound')
            else:
                normal_payment = payment.payment_type == 'outbound'
            if paired_payment.currency_id != company_currency_id:
                foreign_amount = paired_payment.amount
            else:
                if payment._fields.get('payment_group_id', False) and not payment.payment_group_id:
                    foreign_amount = payment.amount
                else:
                    if paired_payment.check_rate and paired_payment.rate_exchange:
                        foreign_amount = paired_payment.amount / paired_payment.rate_exchange
                    else:
                        foreign_amount = company_currency_id._convert(paired_payment.amount,
                                                                      paired_payment.destination_journal_id.currency_id,
                                                                      paired_payment.company_id,
                                                                      paired_payment.date)
            if company_currency_id != currency_id:
                amount_company_currency = local_currency
                amount = foreign_amount
            else:
                amount_company_currency = local_currency
                amount = local_currency
            for line in paired_payment.move_id.line_ids:
                value = {}
                if line == paired_payment.move_id.line_ids[0]:
                    if paired_payment.journal_id.currency_id != paired_payment.destination_journal_id.currency_id:
                        if currency_id != paired_payment.company_currency_id:
                            value['amount_currency'] = amount
                            value['currency_id'] = currency_id.id
                        else:
                            value['amount_currency'] = amount_company_currency
                            value['currency_id'] = paired_payment.company_currency_id.id
                    else:
                        value['amount_currency'] = paired_payment.amount
                        value['currency_id'] = paired_payment.currency_id.id
                        if paired_payment.currency_id != paired_payment.company_currency_id:
                            amount_company_currency = paired_payment.currency_id._convert(paired_payment.amount,
                                                                                          company_currency_id,
                                                                                          paired_payment.company_id,
                                                                                          paired_payment.date)
                    payment_method_account = False
                    journal_id = paired_payment.journal_id
                    if group_extension_installed:
                        payment_method = paired_payment.payment_method_line_id
                        if paired_payment.journal_id == paired_payment.currency_id.multiple_payments_journal_id:
                            apml_obj = self.env['account.payment.method.line']
                            journal_id = paired_payment.destination_journal_id
                            payment_method = apml_obj.search([('payment_method_id', '=', paired_payment.payment_method_id.id),
                                                              ('journal_id', '=', paired_payment.destination_journal_id.id)])
                        payment_method_account = payment_method.payment_account_id if payment_method else False
                        if not paired_payment.payment_group_id:
                            if payment.payment_type == 'outbound':
                                payment_account = payment_method_account or journal_id.company_id.account_journal_payment_debit_account_id
                            else:
                                payment_account = payment_method_account or journal_id.company_id.account_journal_payment_credit_account_id
                        elif paired_payment.payment_group_id.partner_type == 'customer':
                            payment_account = payment_method_account or journal_id.company_id.account_journal_payment_debit_account_id
                        else:
                            journal_id = paired_payment.journal_id
                            payment_account = journal_id.default_account_id

                        value['account_id'] = payment_account.id
                        if normal_payment:
                            value['debit'] = amount_company_currency
                            value['credit'] = 0
                        else:
                            value['debit'] = 0
                            value['credit'] = amount_company_currency
                            value['amount_currency'] = -value['amount_currency']
                    else:
                        payment_account = paired_payment.move_id.line_ids[0].account_id
                        value['debit'] = amount_company_currency
                        value['credit'] = 0
                    value['account_id'] = payment_account.id
                    value['check_rate'] = paired_payment.check_rate
                    value['rate_exchange'] = paired_payment.rate_exchange
                else:
                    transfer_account_id = paired_payment.journal_id.company_id.transfer_account_id
                    if not transfer_account_id:
                        raise ValidationError(_('No se encontró cuenta de transferencia interna en la compañía.'))
                    if paired_payment.journal_id.currency_id != paired_payment.destination_journal_id.currency_id:
                        if currency_id != paired_payment.company_currency_id:
                            value['amount_currency'] = -amount
                            value['currency_id'] = currency_id.id
                        else:
                            value['amount_currency'] = -amount_company_currency
                            value['currency_id'] = paired_payment.company_currency_id.id
                    else:
                        value['amount_currency'] = -paired_payment.amount
                        value['currency_id'] = paired_payment.currency_id.id
                        if paired_payment.currency_id != paired_payment.company_currency_id:
                            amount_company_currency = paired_payment.currency_id._convert(paired_payment.amount,
                                                                                          company_currency_id,
                                                                                          paired_payment.company_id,
                                                                                          paired_payment.date)
                    value['account_id'] = transfer_account_id.id
                    value['check_rate'] = paired_payment.check_rate
                    value['rate_exchange'] = paired_payment.rate_exchange
                    if group_extension_installed:
                        if normal_payment:
                            value['debit'] = 0
                            value['credit'] = amount_company_currency
                        else:
                            value['debit'] = amount_company_currency
                            value['credit'] = 0
                            value['amount_currency'] = -value['amount_currency']
                    else:
                        value['debit'] = 0
                        value['credit'] = amount_company_currency
                move_values['line_ids'].append((1, line.id, value))
            paired_payment.move_id.write(move_values)
            paired_payment.move_id._post(soft=False)
            payment.paired_internal_transfer_payment_id = paired_payment
            partner_type = paired_payment.payment_group_id.partner_type if paired_payment._fields.get('payment_group_id', False) else paired_payment.partner_type
            if partner_type == 'customer' and paired_payment.payment_method_code == 'new_third_party_checks':
                paired_payment.l10n_latam_check_number = payment.aux_l10n_latam_check_number
                paired_payment.l10n_latam_check_bank_id = payment.aux_l10n_latam_check_bank_id.id
                paired_payment.l10n_latam_check_issuer_vat = payment.aux_l10n_latam_check_issuer_vat
                paired_payment.l10n_latam_check_payment_date = payment.aux_l10n_latam_check_payment_date

            payment.paired_internal_transfer_payment_id = paired_payment
            body = _("This payment has been created from: ") + payment._get_html_link()
            paired_payment.message_post(body=body)
            body = _("A second payment has been created: ") + paired_payment._get_html_link()
            payment.message_post(body=body)

            lines = (payment.move_id.line_ids + paired_payment.move_id.line_ids).filtered(lambda l: l.account_id == payment.destination_account_id and not l.reconciled)
            lines.reconcile()
            payment.paired_internal_transfer_payment_id.counter_part_internal_transfer = True
            payment.paired_internal_transfer_payment_id.state = 'posted'

    def action_draft(self):
        ''' posted -> draft '''
        for rec in self:
            rec = rec.with_context(force_delete=True)
            if rec.is_internal_transfer and rec.paired_internal_transfer_payment_id and not rec.counter_part_internal_transfer:
                rec.paired_internal_transfer_payment_id.action_draft()
                rec.paired_internal_transfer_payment_id.unlink()
                rec.payment_type = rec.aux_payment_type
                if self.env['ir.module.module'].search([('name', '=', 'account_payment_group_extension'), ('state', '=', 'installed')]) and rec.payment_group_id:
                    rec.partner_type = rec.payment_group_id.partner_type
        res = super(AccountPayment, self).action_draft()
        return res

    def button_open_journal_entry(self):
        ''' Redirect the user to this payment journal.
        :return:    An action on account.move.
        '''
        self.ensure_one()
        if self.is_internal_transfer:
            move_ids = self.move_id
            if self.paired_internal_transfer_payment_id:
                move_ids += self.paired_internal_transfer_payment_id.move_id
            return {
                'name': _("Journal Entry"),
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'context': {'create': False},
                'view_mode': 'tree,form',
                'domain': [('id', 'in', move_ids.ids)],
            }
        else:
            return {
                'name': _("Journal Entry"),
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'context': {'create': False},
                'view_mode': 'form',
                'res_id': self.move_id.id,
            }

    @api.depends('partner_id', 'journal_id', 'destination_journal_id', 'always_internal_transfer')
    def _compute_is_internal_transfer(self):
        for payment in self:
            payment.is_internal_transfer = (payment.partner_id and payment.partner_id == payment.journal_id.company_id.partner_id and payment.destination_journal_id) or payment.always_internal_transfer





