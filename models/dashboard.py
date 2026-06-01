from odoo import models, api, fields
from datetime import date
from dateutil.relativedelta import relativedelta


class ReferralDashboard(models.AbstractModel):
    _name = 'referral.dashboard'
    _description = 'Referral Dashboard'

    @api.model
    def get_dashboard_data(self, period='this_month'):
        today = date.today()

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
        currency = self.env.company.currency_id

        # ── KPI ──────────────────────────────────────────────
        total_members = Member.search_count([])
        active_members = Member.search_count([('state', '=', 'active')])

        approved_commissions = Commission.search([
            ('state', '=', 'approved'),
            ('create_date', '>=', fields.Datetime.to_datetime(date_from)),
            ('create_date', '<=', fields.Datetime.to_datetime(date_to)),
        ])
        total_commission = sum(approved_commissions.mapped('commission_amount'))

        paid_withdrawals = Withdraw.search([
            ('state', '=', 'paid'),
            ('date_paid', '>=', date_from),
            ('date_paid', '<=', date_to),
        ])
        total_withdrawal = sum(paid_withdrawals.mapped('amount'))

        # ── Build month range ─────────────────────────────────
        months = []
        cursor = date_from.replace(day=1)
        while cursor <= date_to:
            months.append(cursor)
            cursor = (cursor + relativedelta(months=1)).replace(day=1)

        # ── Chart 1: Commission Trend (bar) ───────────────────
        chart_commission_labels = []
        chart_commission_values = []
        for m in months:
            m_end = (m + relativedelta(months=1)).replace(day=1) - relativedelta(days=1)
            label = m.strftime('%b %Y')
            comms = Commission.search([
                ('state', '=', 'approved'),
                ('create_date', '>=', fields.Datetime.to_datetime(m)),
                ('create_date', '<=', fields.Datetime.to_datetime(m_end)),
            ])
            total = sum(comms.mapped('commission_amount'))
            chart_commission_labels.append(label)
            chart_commission_values.append(round(total, 2))

        # ── Chart 2: Member Growth (line) ─────────────────────
        chart_member_labels = []
        chart_member_values = []
        for m in months:
            m_end = (m + relativedelta(months=1)).replace(day=1) - relativedelta(days=1)
            label = m.strftime('%b %Y')
            count = Member.search_count([
                ('join_date', '>=', m),
                ('join_date', '<=', m_end),
            ])
            chart_member_labels.append(label)
            chart_member_values.append(count)

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
            'chart_commission': {
                'labels': chart_commission_labels,
                'values': chart_commission_values,
            },
            'chart_member_growth': {
                'labels': chart_member_labels,
                'values': chart_member_values,
            },
        }