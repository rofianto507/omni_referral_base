from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CommissionRule(models.Model):
    _name = 'commission.rule'
    _description = 'Commission Level Rule'
    _order = 'level_depth asc'

    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=True,
        readonly=True,
    )
    level_depth = fields.Integer(
        string='Depth Level', 
        required=True, 
        default=1,
        help='Referral depth level (e.g., 1 = Direct Sponsor / Upline)'
    )
    commission_pct = fields.Float(
        string='Commission (%)', 
        required=True,
        help='The percentage of commission granted from the transaction amount'
    )
    
    @api.depends('level_depth')
    def _compute_name(self):
        for rec in self:
            rec.name = f'Level {rec.level_depth}'

    @api.constrains('commission_pct')
    def _check_commission_pct(self):
        for rec in self:
            if rec.commission_pct < 0 or rec.commission_pct > 100:
                raise ValidationError(_("Commission must be between 0 and 100."))
    # Prevent users from creating duplicate rules for the same depth level
    _sql_constraints = [
        (
            'unique_level_depth', 
            'UNIQUE(level_depth)', 
            'A rule for this depth level already exists! Please define a unique level depth.'
        )
    ]