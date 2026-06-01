/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart, onMounted, onPatched, useRef } from "@odoo/owl";

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

        this.chartCommissionRef = useRef("chartCommission");
        this.chartMemberRef = useRef("chartMember");
        this._chartCommission = null;
        this._chartMember = null;

        onWillStart(async () => {
            await this._loadECharts();
            await this.loadData();
        });

        onMounted(() => {
            this._renderCharts();
        });

        onPatched(() => {
            this._renderCharts();
        });
    }

    async _loadECharts() {
        if (window.echarts) return;
        return new Promise((resolve, reject) => {
            const script = document.createElement("script");
            script.src = "https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js";
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
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

    _renderCharts() {
        if (!this.state.data || this.state.loading || !window.echarts) return;
        this._renderCommissionChart();
        this._renderMemberGrowthChart();
    }

    _renderCommissionChart() {
        const el = this.chartCommissionRef.el;
        if (!el) return;

        if (this._chartCommission) {
            this._chartCommission.dispose();
        }
        this._chartCommission = echarts.init(el);

        const { labels, values } = this.state.data.chart_commission;
        const { currency_symbol } = this.state.data;

        this._chartCommission.setOption({
            tooltip: {
                trigger: "axis",
                formatter: (params) => {
                    const p = params[0];
                    return `${p.name}<br/><b>${currency_symbol} ${this._fmt(p.value)}</b>`;
                },
                backgroundColor: "#1f2937",
                borderColor: "#1f2937",
                textStyle: { color: "#fff" },
            },
            grid: { left: 60, right: 20, top: 20, bottom: 40 },
            xAxis: {
                type: "category",
                data: labels,
                axisLine: { lineStyle: { color: "#e5e7eb" } },
                axisLabel: { color: "#6b7280", fontSize: 11 },
            },
            yAxis: {
                type: "value",
                axisLabel: {
                    color: "#6b7280",
                    fontSize: 11,
                    formatter: (val) => `${currency_symbol}${this._fmtShort(val)}`,
                },
                splitLine: { lineStyle: { color: "#f3f4f6" } },
            },
            series: [{
                type: "bar",
                data: values,
                barMaxWidth: 48,
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: "#71639e" },
                        { offset: 1, color: "#a78bfa" },
                    ]),
                    borderRadius: [6, 6, 0, 0],
                },
                emphasis: {
                    itemStyle: { color: "#71639e" },
                },
                label: {
                    show: values.length <= 6,
                    position: "top",
                    formatter: (p) => p.value > 0 ? `${currency_symbol}${this._fmtShort(p.value)}` : "",
                    color: "#6b7280",
                    fontSize: 10,
                },
            }],
        });
    }

    _renderMemberGrowthChart() {
        const el = this.chartMemberRef.el;
        if (!el) return;

        if (this._chartMember) {
            this._chartMember.dispose();
        }
        this._chartMember = echarts.init(el);

        const { labels, values } = this.state.data.chart_member_growth;

        this._chartMember.setOption({
            tooltip: {
                trigger: "axis",
                formatter: (params) => {
                    const p = params[0];
                    return `${p.name}<br/><b>${p.value} new member(s)</b>`;
                },
                backgroundColor: "#1f2937",
                borderColor: "#1f2937",
                textStyle: { color: "#fff" },
            },
            grid: { left: 40, right: 20, top: 20, bottom: 40 },
            xAxis: {
                type: "category",
                data: labels,
                axisLine: { lineStyle: { color: "#e5e7eb" } },
                axisLabel: { color: "#6b7280", fontSize: 11 },
                boundaryGap: false,
            },
            yAxis: {
                type: "value",
                minInterval: 1,
                axisLabel: { color: "#6b7280", fontSize: 11 },
                splitLine: { lineStyle: { color: "#f3f4f6" } },
            },
            series: [{
                type: "line",
                data: values,
                smooth: true,
                symbol: "circle",
                symbolSize: 8,
                lineStyle: { color: "#059669", width: 3 },
                itemStyle: { color: "#059669", borderWidth: 2, borderColor: "#fff" },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: "rgba(5,150,105,0.25)" },
                        { offset: 1, color: "rgba(5,150,105,0.02)" },
                    ]),
                },
                label: {
                    show: values.length <= 12,
                    position: "top",
                    formatter: (p) => p.value > 0 ? p.value : "",
                    color: "#6b7280",
                    fontSize: 10,
                },
            }],
        });
    }
    
    // ── Actions ──────────────────────────────────────────────────────────────
    openMember(memberId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "referral.member",
            res_id: memberId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    async approveCommission(commissionId) {
        await this.orm.call("referral.dashboard", "action_approve_commission", [commissionId]);
        await this.loadData();
    }

    async rejectCommission(commissionId) {
        await this.orm.call("referral.dashboard", "action_reject_commission", [commissionId]);
        await this.loadData();
    }

    _fmt(val) {
        return new Intl.NumberFormat("id-ID", { minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(val || 0);
    }

    _fmtShort(val) {
        if (val >= 1_000_000) return (val / 1_000_000).toFixed(1) + "M";
        if (val >= 1_000) return (val / 1_000).toFixed(0) + "K";
        return val;
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
        const formatted = this._fmt(amount);
        return currency_position === "before"
            ? `${currency_symbol} ${formatted}`
            : `${formatted} ${currency_symbol}`;
    }

    formatNumber(val) {
        return new Intl.NumberFormat("id-ID").format(val || 0);
    }
}

registry.category("actions").add("referral_dashboard_action", ReferralDashboard);