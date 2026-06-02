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

    def _is_upline_active_seller(self, upline):
        """
        Check if the upline has any confirmed sales orders in the past month.
        This is used to determine whether to auto-approve the commission or set it to pending for manual review.
        """
        one_month_ago = date.today() - relativedelta(months=1)
        partner = upline.partner_id
        if not partner:
            return False
        confirmed_so = self.env['sale.order'].search_count([
            ('referral_member_id', '=', upline.id), 
            ('state', 'in', ['sale', 'done']),
            ('date_order', '>=', one_month_ago),
            ('id', '!=', self.id),  # exclude current order to prevent self-counting when confirming the same order again
        ])
        return confirmed_so > 0
    
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

        #remove existing pending commissions for this order to avoid duplicates if order is confirmed again
        self.referral_commission_ids.filtered(
            lambda x: x.state == 'pending'
        ).unlink()

        rules = self.env['commission.rule'].search([], order='level_depth asc')
        if not rules:
            return

        base_amount = self.amount_untaxed
        if base_amount <= 0:
            return

        current_member = self.referral_member_id
        for rule in rules:
            upline = current_member.sponsor_id
            if not upline:
                break
            #skip if upline is not active, but continue to check next upline in the hierarchy
            if upline.state != 'active':
                current_member = upline
                continue

            commission_amount = base_amount * rule.commission_pct / 100.0
            if commission_amount > 0:
                # if upline has confirmed sales in the past month, auto-approve the commission; otherwise, set to pending for manual review
                auto_approved = self._is_upline_active_seller(upline)
                commission_state = 'approved' if auto_approved else 'pending'
                self.env['referral.commission'].create({
                    'sale_order_id': self.id,
                    'source_member_id': self.referral_member_id.id,
                    'beneficiary_member_id': upline.id,
                    'level_depth': rule.level_depth,
                    'rule_id': rule.id,
                    'base_amount': base_amount,
                    'commission_pct': rule.commission_pct,
                    'commission_amount': commission_amount,
                    'currency_id': self.currency_id.id,
                    'state': commission_state,
                })
                if auto_approved:
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
    