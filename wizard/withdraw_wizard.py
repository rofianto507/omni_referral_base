from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class WithdrawWizard(models.TransientModel):
    _name = 'withdraw.wizard'
    _description = 'Commission Withdraw Wizard'

    member_id = fields.Many2one(
        'referral.member',
        string='Member',
        required=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='member_id.currency_id',
    )
    commission_balance = fields.Monetary(
        string='Available Balance',
        related='member_id.commission_balance',
    )
    amount = fields.Monetary(
        string='Withdraw Amount',
        required=True,
    )
    note = fields.Text(string='Note')

    @api.constrains('amount', 'member_id')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(_("Withdraw amount must be greater than 0."))
            if rec.amount > rec.member_id.commission_balance:
                raise ValidationError(_(
                    "Withdraw amount cannot exceed commission balance (%(balance)s).",
                    balance=rec.member_id.commission_balance,
                ))

    def action_confirm(self):
        self.ensure_one()
        withdraw = self.env['commission.withdraw'].create({
            'member_id': self.member_id.id,
            'amount': self.amount,
            'note': self.note,
        })
        # langsung buka form withdraw yang baru dibuat
        return {
            'type': 'ir.actions.act_window',
            'name': _('Withdrawal'),
            'res_model': 'commission.withdraw',
            'res_id': withdraw.id,
            'view_mode': 'form',
            'target': 'current',
        }