/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart, onMounted, onPatched,onWillUnmount, useRef } from "@odoo/owl";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

class ReferralDashboard extends Component {
    static template = "omni_referral_base.ReferralDashboard";
    static components = {};

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.dialogService = useService("dialog");
        this.state = useState({
            loading: true,
            period: "this_month",
            data: null,
        });

        this.chartCommissionRef = useRef("chartCommission");
        this.chartMemberRef = useRef("chartMember");
        this._chartCommission = null;
        this._chartMember = null;
        this._resizeObserver = null;

        onWillStart(async () => {
            await this._loadECharts();
            await this.loadData();
        });

        onMounted(() => {
            this._renderCharts();
            this._initResizeObserver();
        });

        onPatched(() => {
            this._renderCharts();
            if(!this._resizeObserver) {
                this._initResizeObserver();
            }
        });
        onWillUnmount(() => {
            if (this._resizeObserver) {
                this._resizeObserver.disconnect();
                this._resizeObserver = null;
            }
            if (this._chartCommission) {
                this._chartCommission.dispose();
                this._chartCommission = null;
            }
            if (this._chartMember) {
                this._chartMember.dispose();
                this._chartMember = null;
            }
        });
    }
     _initResizeObserver() {
        const container = this.chartCommissionRef.el?.closest(".o_referral_dashboard");
        if (!container || !window.ResizeObserver) return;

        this._resizeObserver = new ResizeObserver(() => {
            this._resizeCharts();
        });
        this._resizeObserver.observe(container);
    }

    _resizeCharts() {
        if (this._chartCommission) this._chartCommission.resize();
        if (this._chartMember) this._chartMember.resize();
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
                backgroundColor: "#1f2937cc",
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
                backgroundColor: "#1f2937cc",
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
                lineStyle: { color: "#71639e", width: 3 },
                itemStyle: { color: "#a78bfa", borderWidth: 2, borderColor: "#fff" },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: "rgba(97, 5, 150, 0.25)" },
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
    onClickMember(ev) {
        const memberId = parseInt(ev.currentTarget.dataset.memberId);
        if (!memberId) return;
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "referral.member",
            res_id: memberId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    onClickApprove(ev) {
        const id = parseInt(ev.currentTarget.dataset.commissionId);
        const member = ev.currentTarget.dataset.memberName || "";
        const amount = ev.currentTarget.dataset.amount || "";
        if (!id) return;
        this.dialogService.add(ConfirmationDialog, {
            title: "Approve Commission",
            body: `Approve commission ${amount} for ${member}? This action cannot be undone.`,
            confirmLabel: "Approve",
            cancelLabel: "Cancel",
            confirm: async () => {
                await this.orm.call("referral.dashboard", "action_approve_commission", [id]);
                await this.loadData();
            },
            cancel: () => {},
        });
    }

    onClickReject(ev) {
        const id = parseInt(ev.currentTarget.dataset.commissionId);
        const member = ev.currentTarget.dataset.memberName || "";
        const amount = ev.currentTarget.dataset.amount || "";
        if (!id) return;
        this.dialogService.add(ConfirmationDialog, {
            title: "Reject Commission",
            body: `Reject commission ${amount} for ${member}? This action cannot be undone.`,
            confirmLabel: "Reject",
            cancelLabel: "Cancel",
            confirmClass: "btn-danger",
            confirm: async () => {
                await this.orm.call("referral.dashboard", "action_reject_commission", [id]);
                await this.loadData();
            },
            cancel: () => {},
        });
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