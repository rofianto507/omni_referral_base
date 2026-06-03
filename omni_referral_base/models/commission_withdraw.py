from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class CommissionWithdraw(models.Model):
    _name = 'commission.withdraw'
    _description = 'Commission Withdrawal'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Reference',
        readonly=True,
        default='/',
        copy=False,
    )
    member_id = fields.Many2one(
        'referral.member',
        string='Member',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='member_id.currency_id',
        store=True,
    )
    amount = fields.Monetary(
        string='Withdraw Amount',
        required=True,
        tracking=True,
    )
    commission_balance_before = fields.Monetary(
        string='Balance Before',
        readonly=True,
    )
    commission_balance_after = fields.Monetary(
        string='Balance After',
        readonly=True,
        compute='_compute_balance_after',
        store=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
    ], default='draft', required=True, tracking=True)
    note = fields.Text(string='Note')
    date_request = fields.Date(
        string='Request Date',
        default=fields.Date.context_today,
        readonly=True,
    )
    date_paid = fields.Date(string='Paid Date', readonly=True)

    @api.depends('commission_balance_before', 'amount')
    def _compute_balance_after(self):
        for rec in self:
            rec.commission_balance_after = rec.commission_balance_before - rec.amount

    @api.constrains('amount', 'member_id')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(_("Withdraw amount must be greater than 0."))
            if rec.amount > rec.member_id.commission_balance:
                raise ValidationError(_(
                    "Withdraw amount (%(amount)s) cannot exceed commission balance (%(balance)s).",
                    amount=rec.amount,
                    balance=rec.member_id.commission_balance,
                ))

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == '/':
                vals['name'] = seq.next_by_code('omni.referral.commission.withdraw') or '/'
            # save current balance in the record for reference, so it won't be affected by concurrent transactions after creation
            if vals.get('member_id'):
                member = self.env['referral.member'].browse(vals['member_id'])
                vals['commission_balance_before'] = member.commission_balance
        return super().create(vals_list)

    def action_submit(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only draft withdrawals can be submitted."))
            rec.state = 'submitted'

    def action_approve(self):
        for rec in self:
            if rec.state != 'submitted':
                raise UserError(_("Only submitted withdrawals can be approved."))
            # validate balance again at approval
            if rec.amount > rec.member_id.commission_balance:
                raise ValidationError(_(
                    "Insufficient commission balance at time of approval."
                ))
            rec.state = 'approved'

    def action_paid(self):
        for rec in self:
            if rec.state != 'approved':
                raise UserError(_("Only approved withdrawals can be marked as paid."))
            rec.state = 'paid'
            rec.date_paid = fields.Date.today()
            # reduce member's commission balance
            rec.member_id.commission_withdrawn += rec.amount

    def action_reject(self):
        for rec in self:
            if rec.state in ('paid',):
                raise UserError(_("Paid withdrawal cannot be rejected."))
            rec.state = 'rejected'

    def action_reset_draft(self):
        for rec in self:
            if rec.state != 'rejected':
                raise UserError(_("Only rejected withdrawals can be reset to draft."))
            rec.state = 'draft'