# models/referral_commission.py
from odoo import models, fields, api, _

class ReferralCommission(models.Model):
    _name = 'referral.commission'
    _description = 'Referral Commission'
    _order = 'id desc'

    sale_order_id = fields.Many2one('sale.order', required=True, ondelete='cascade')
    source_member_id = fields.Many2one('referral.member', required=True, help='Member that generated the commission (downline)')
    beneficiary_member_id = fields.Many2one('referral.member', required=True, help='Member that receives the commission (upline)')
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
    ], default='pending', required=True)

    _sql_constraints = [
        ('uniq_so_beneficiary_level', 'unique(sale_order_id, beneficiary_member_id, level_depth)',
         'Commission for this sale/member/level already exists.')
    ]