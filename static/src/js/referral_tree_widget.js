/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart } from "@odoo/owl";

// ── Node Component ─────────────────────────────────────────────────────────────
class ReferralNode extends Component {
    static props = {
        node: Object,
        depth: { type: Number, default: 0 },
        onOpenMember: Function,
    };
    static template = "omni_referral_base.ReferralNode";
    // ↓ wajib ada agar bisa rekursif render dirinya sendiri
    static components = {};

    setup() {
        this.state = useState({ expanded: this.props.depth === 0 });
    }

    toggle() {
        if (this.props.node.children && this.props.node.children.length) {
            this.state.expanded = !this.state.expanded;
        }
    }

    get stateClass() {
        const map = {
            active: "badge-active",
            draft: "badge-draft",
            suspended: "badge-suspended",
            terminated: "badge-terminated",
        };
        return map[this.props.node.state] || "badge-draft";
    }

    get stateLabel() {
        const map = {
            active: "Active",
            draft: "Draft",
            suspended: "Suspended",
            terminated: "Terminated",
        };
        return map[this.props.node.state] || this.props.node.state;
    }

    get hasChildren() {
        return this.props.node.children && this.props.node.children.length > 0;
    }

    openMember() {
        this.props.onOpenMember(this.props.node.id);
    }
}

// daftarkan dirinya sendiri setelah class terdefinisi
ReferralNode.components = { ReferralNode };

// ── Main Tree View ─────────────────────────────────────────────────────────────
class ReferralTreeView extends Component {
    static template = "omni_referral_base.ReferralTreeView";
    static components = { ReferralNode };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ tree: null, loading: true, error: null });

        onWillStart(async () => {
            const memberId = this.props.action?.context?.active_id;
            if (!memberId) {
                this.state.error = "No member selected.";
                this.state.loading = false;
                return;
            }
            try {
                const result = await this.orm.call(
                    "referral.member",
                    "get_referral_tree",
                    [memberId]
                );
                this.state.tree = result;
            } catch (e) {
                this.state.error = "Failed to load referral tree.";
            } finally {
                this.state.loading = false;
            }
        });
    }

    openMember(memberId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "referral.member",
            res_id: memberId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("referral_tree_action", ReferralTreeView);