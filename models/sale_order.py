from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
from dateutil.relativedelta import relativedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    referral_member_id = fields.Many2one(
        'referral.member',
        string='Referral Member',
        help='Auto-filled referral member based on the selected customer. Commissions will be generated for this member and their uplines upon order confirmation.',
        domain="[('state', '=', 'active')]",
        tracking=True,
        readonly=True,
        store=True,
        compute='_compute_referral_member_id',
    )
    referral_commission_ids = fields.One2many(
        'referral.commission',
        'sale_order_id',
        string='Referral Commissions',
    )
    referral_commission_count = fields.Integer(
        string='Commission Count',
        compute='_compute_referral_commission_count',
    )

    @api.depends('partner_id')
    def _compute_referral_member_id(self):
        for order in self:
            if order.partner_id and order.partner_id.referral_member_id:
                order.referral_member_id = order.partner_id.referral_member_id
            else:
                order.referral_member_id = False

    def _compute_referral_commission_count(self):
        for rec in self:
            rec.referral_commission_count = len(rec.referral_commission_ids)

    def _get_referral_config(self):
        ICP = self.env['ir.config_parameter'].sudo()
        return {
            'auto_approve' : ICP.get_param('omni_referral_base.auto_approve_active_upline', 'True') == 'True',
            'skip_inactive': ICP.get_param('omni_referral_base.skip_inactive_upline', 'False') == 'True',
            'active_days'  : int(ICP.get_param('omni_referral_base.active_upline_days', 30)),
        }
    def _is_upline_active_seller(self, upline, active_days=30):
        """
        Check if the upline has any confirmed sales orders in the past `active_days` days. This is used to determine if the commission can be auto-approved.
        """
        from datetime import date, timedelta
        cutoff = date.today() - timedelta(days=active_days)
        return self.env['sale.order'].search_count([
            ('referral_member_id', '=', upline.id),
            ('state', 'in', ['sale', 'done']),
            ('date_order', '>=', cutoff),
            ('id', '!=', self.id),
        ]) > 0
    
    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            order._generate_referral_commissions()
        return res
    
    def action_cancel(self):
        res = super().action_cancel()
        for order in self:
            order.referral_commission_ids.filtered(
                lambda x: x.state == 'pending'
            ).action_cancel()
        return res
    
    def _generate_referral_commissions(self):
        self.ensure_one()
        if not self.referral_member_id:
            return

        self.referral_commission_ids.filtered(
            lambda x: x.state == 'pending'
        ).unlink()

        rules = self.env['commission.rule'].search([], order='level_depth asc')
        if not rules:
            return

        base_amount = self.amount_untaxed
        if base_amount <= 0:
            return

        # Baca config sekali saja
        cfg = self._get_referral_config()

        current_member = self.referral_member_id
        for rule in rules:
            upline = current_member.sponsor_id
            if not upline:
                break

            if upline.state != 'active':
                current_member = upline
                continue

            # Cek aktivitas upline jika fitur aktif
            if cfg['auto_approve']:
                upline_active = self._is_upline_active_seller(upline, cfg['active_days'])

                # Skip: tidak buat record komisi sama sekali
                if not upline_active and cfg['skip_inactive']:
                    current_member = upline
                    continue

                commission_state = 'approved' if upline_active else 'pending'
            else:
                # Fitur mati → semua pending seperti biasa
                commission_state = 'pending'

            commission_amount = base_amount * rule.commission_pct / 100.0
            if commission_amount > 0:
                self.env['referral.commission'].create({
                    'sale_order_id'         : self.id,
                    'source_member_id'      : self.referral_member_id.id,
                    'beneficiary_member_id' : upline.id,
                    'level_depth'           : rule.level_depth,
                    'rule_id'               : rule.id,
                    'base_amount'           : base_amount,
                    'commission_pct'        : rule.commission_pct,
                    'commission_amount'     : commission_amount,
                    'currency_id'           : self.currency_id.id,
                    'state'                 : commission_state,
                })
                if commission_state == 'approved':
                    upline._compute_commission_balance()

            current_member = upline

    def action_view_referral_commissions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Referral Commissions'),
            'res_model': 'referral.commission',
            'view_mode': 'list,form',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {'default_sale_order_id': self.id},
        }
    