from odoo import models, api, fields
from datetime import date
from dateutil.relativedelta import relativedelta


class ReferralDashboard(models.AbstractModel):
    _name = 'referral.dashboard'
    _description = 'Referral Dashboard'

    @api.model
    def get_dashboard_data(self, period='this_month'):
        today = date.today()

        # Tentukan date range berdasarkan filter
        if period == 'this_month':
            date_from = today.replace(day=1)
            date_to = today
        elif period == 'last_3_months':
            date_from = (today - relativedelta(months=3)).replace(day=1)
            date_to = today
        elif period == 'last_6_months':
            date_from = (today - relativedelta(months=6)).replace(day=1)
            date_to = today
        elif period == 'this_year':
            date_from = today.replace(month=1, day=1)
            date_to = today
        else:
            date_from = today.replace(day=1)
            date_to = today

        Member = self.env['referral.member']
        Commission = self.env['referral.commission']
        Withdraw = self.env['commission.withdraw']

        # KPI 1 — Total Members (all time)
        total_members = Member.search_count([])

        # KPI 2 — Active Members (all time)
        active_members = Member.search_count([('state', '=', 'active')])

        # KPI 3 — Total Commission Approved dalam period
        approved_commissions = Commission.search([
            ('state', '=', 'approved'),
            ('create_date', '>=', fields.Datetime.to_datetime(date_from)),
            ('create_date', '<=', fields.Datetime.to_datetime(date_to)),
        ])
        total_commission = sum(approved_commissions.mapped('commission_amount'))

        # KPI 4 — Total Withdrawal Paid dalam period
        paid_withdrawals = Withdraw.search([
            ('state', '=', 'paid'),
            ('date_paid', '>=', date_from),
            ('date_paid', '<=', date_to),
        ])
        total_withdrawal = sum(paid_withdrawals.mapped('amount'))

        # Currency symbol
        currency = self.env.company.currency_id

        return {
            'period': period,
            'date_from': str(date_from),
            'date_to': str(date_to),
            'currency_symbol': currency.symbol,
            'currency_position': currency.position,
            'kpi': {
                'total_members': total_members,
                'active_members': active_members,
                'total_commission': total_commission,
                'total_withdrawal': total_withdrawal,
            },
        }