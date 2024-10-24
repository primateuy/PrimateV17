/** @odoo-module **/

import { registry } from "@web/core/registry";
import { AnalyticDistribution } from "@analytic/components/analytic_distribution/analytic_distribution";

class AnalyticDistributionExtension extends AnalyticDistribution {
    setup() {
        super.setup()
        console.log('AnalyticDistributionExtension setup');
    }

    allowSave() {
        super.allowSave();
        console.log('AnalyticDistributionExtension planTotals');

    }
}

AnalyticDistributionExtension.supportedTypes = ['char'];



registry.category("fields").add("analytic_distribution_extension", AnalyticDistributionExtension);