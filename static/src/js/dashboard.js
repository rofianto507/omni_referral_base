/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart, onWillUpdateProps } from "@odoo/owl";

class ReferralDashboard extends Component {
    static template = "omni_referral_base.ReferralDashboard";
    static components = {};

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            period: "this_month",
            data: null,
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        this.state.loading = true;
        try {
            const result = await this.orm.call(
                "referral.dashboard",
                "get_dashboard_data",
                [this.state.period]
            );
            this.state.data = result;
        } finally {
            this.state.loading = false;
        }
    }

    async onPeriodChange(ev) {
        this.state.period = ev.target.value;
        await this.loadData();
    }

    get periodLabel() {
        const labels = {
            this_month: "This Month",
            last_3_months: "Last 3 Months",
            last_6_months: "Last 6 Months",
            this_year: "This Year",
        };
        return labels[this.state.period] || "";
    }

    formatCurrency(amount) {
        if (!this.state.data) return "0";
        const { currency_symbol, currency_position } = this.state.data;
        const formatted = new Intl.NumberFormat("id-ID", {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(amount || 0);
        return currency_position === "before"
            ? `${currency_symbol} ${formatted}`
            : `${formatted} ${currency_symbol}`;
    }

    formatNumber(val) {
        return new Intl.NumberFormat("id-ID").format(val || 0);
    }
}

registry.category("actions").add("referral_dashboard_action", ReferralDashboard);