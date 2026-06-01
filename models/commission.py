from odoo import models, fields, api, _
from odoo.exceptions import UserError


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
    commission_pct = fields.Float(required=True)
    commission_amount = fields.Monetary(required=True)
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