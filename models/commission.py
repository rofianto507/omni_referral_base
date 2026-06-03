from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ReferralCommission(models.Model):
    _name = 'referral.commission'
    _description = 'Referral Commission'
    _order = 'id desc'
    _rec_name = 'sale_order_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sale_order_id = fields.Many2one('sale.order', required=True, ondelete='cascade', tracking=True)
    source_member_id = fields.Many2one('referral.member', required=True,
                                       help='Member that made the purchase (downline)')
    beneficiary_member_id = fields.Many2one('referral.member', required=True,
                                            help='Member that receives the commission (upline)', tracking=True)
    beneficiary_partner_id = fields.Many2one('res.partner', related='beneficiary_member_id.partner_id', store=True)
    level_depth = fields.Integer(required=True)
    rule_id = fields.Many2one('commission.rule', required=True)
    base_amount = fields.Monetary(required=True)
    gross_profit_amount = fields.Monetary(
        string='Gross Profit Amount',
        required=True,
        help='Gross profit (Unit Price - Cost Price) × Quantity. This is the actual base for commission calculation.'
    )
    commission_pct = fields.Float(required=True)
    commission_amount = fields.Monetary(required=True)
    profit_margin_percent = fields.Float(
        string='Profit Margin %',
        compute='_compute_profit_margin_percent',
        store=True,
        help='(Gross Profit / Base Amount) × 100'
    )
    net_profit_after_commission = fields.Monetary(
        string='Net Profit After Commission',
        compute='_compute_net_profit_after_commission',
        store=True,
        help='Gross Profit - Commission Amount'
    )
    currency_id = fields.Many2one('res.currency', required=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], default='pending', required=True, tracking=True)
    
    _sql_constraints = [
        ('uniq_so_beneficiary_level', 'unique(sale_order_id, beneficiary_member_id, level_depth)',
         'Commission for this sale/member/level already exists.')
    ]
    @api.depends('base_amount', 'gross_profit_amount')
    def _compute_profit_margin_percent(self):
        """Calculate profit margin percentage: (Gross Profit / Base Amount) × 100"""
        for rec in self:
            if rec.base_amount > 0:
                rec.profit_margin_percent = (rec.gross_profit_amount / rec.base_amount) * 100
            else:
                rec.profit_margin_percent = 0.0

    @api.depends('gross_profit_amount', 'commission_amount')
    def _compute_net_profit_after_commission(self):
        """Calculate net profit after commission: Gross Profit - Commission"""
        for rec in self:
            rec.net_profit_after_commission = rec.gross_profit_amount - rec.commission_amount

    def action_approve(self):
        for rec in self:
            if rec.state != 'pending':
                raise UserError(_("Only pending commissions can be approved."))
            rec.state = 'approved'
            # trigger recompute balance on beneficiary member when commission is approved
            rec.beneficiary_member_id._compute_commission_balance()

    def action_reject(self):
        for rec in self:
            if rec.state != 'pending':
                raise UserError(_("Only pending commissions can be rejected."))
            rec.state = 'rejected'
            rec.beneficiary_member_id._compute_commission_balance()

    def action_cancel(self):
        for rec in self:
            if rec.state == 'pending':
                rec.state = 'cancelled'

    @api.constrains('gross_profit_amount', 'commission_amount')
    def _check_minimum_net_profit(self):
        """Ensure net profit doesn't go negative"""
        for rec in self:
            net_profit = rec.gross_profit_amount - rec.commission_amount
            if net_profit < 0:
                raise ValidationError(
                    _("Commission amount (Rp %.2f) cannot exceed gross profit (Rp %.2f)") 
                    % (rec.commission_amount, rec.gross_profit_amount)
                )