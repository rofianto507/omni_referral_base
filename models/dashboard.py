from odoo import models, api, fields
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import pytz


class ReferralDashboard(models.AbstractModel):
    _name = 'referral.dashboard'
    _description = 'Referral Dashboard'

    def _local_date_to_utc_range(self, d_from, d_to):
        """
       Convert local date range (d_from, d_to) to UTC datetime range for querying create_date fields.
        d_from : date — start (00:00:00 local)
        d_to   : date — end (23:59:59 local)
        Return : (datetime_utc_start, datetime_utc_end)
        """
        tz_name = self.env.company.partner_id.tz or self.env.user.tz or 'UTC'
        local_tz = pytz.timezone(tz_name)

        # Batas awal: 00:00:00 local → UTC
        dt_from_local = local_tz.localize(datetime(d_from.year, d_from.month, d_from.day, 0, 0, 0))
        dt_from_utc = dt_from_local.astimezone(pytz.utc).replace(tzinfo=None)

        # Batas akhir: 23:59:59 local → UTC
        dt_to_local = local_tz.localize(datetime(d_to.year, d_to.month, d_to.day, 23, 59, 59))
        dt_to_utc = dt_to_local.astimezone(pytz.utc).replace(tzinfo=None)

        return dt_from_utc, dt_to_utc

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

        # convert local date range to UTC datetime range for accurate querying of create_date fields
        dt_from_utc, dt_to_utc = self._local_date_to_utc_range(date_from, date_to)

        # ── KPI ──────────────────────────────────────────────
        total_members = Member.search_count([])
        active_members = Member.search_count([('state', '=', 'active')])

        approved_commissions = Commission.search([
            ('state', '=', 'approved'),
            ('create_date', '>=', dt_from_utc),
            ('create_date', '<=', dt_to_utc),
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
            m_utc_start, m_utc_end = self._local_date_to_utc_range(m, m_end)
            label = m.strftime('%b %Y')
            comms = Commission.search([
                ('state', '=', 'approved'),
                ('create_date', '>=', m_utc_start),
                ('create_date', '<=', m_utc_end),
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
         # ── Top 5 Members by commission_balance ──────────────
        top_members_rec = Member.search(
            [('state', '=', 'active'), ('commission_balance', '>', 0)],
            order='commission_balance desc',
            limit=5,
        )
        top_members = []
        for m in top_members_rec:
            top_members.append({
                'id': m.id,
                'name': m.partner_id.name or '-',
                'member_code': m.member_code or '-',
                'avatar_url': '/web/image/res.partner/%d/image_128' % m.partner_id.id,
                'commission_balance': m.commission_balance,
                'downline_count': m.downline_count,
                'state': m.state,
            })

        # ── Recent Pending Commissions (10 newest) ───────────
        pending_commissions = Commission.search(
            [('state', '=', 'pending')],
            order='create_date desc',
            limit=10,
        )
        pending_list = []
        for c in pending_commissions:
            pending_list.append({
                'id': c.id,
                'beneficiary': c.beneficiary_member_id.partner_id.name or '-',
                'beneficiary_code': c.beneficiary_member_id.member_code or '-',
                'source_member': c.source_member_id.partner_id.name or '-',
                'sale_order': c.sale_order_id.name or '-',
                'level_depth': c.level_depth,
                'commission_pct': c.commission_pct,
                'commission_amount': c.commission_amount,
                'create_date': c.create_date.strftime('%d %b %Y') if c.create_date else '-',
            })
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
            'top_members': top_members,
            'pending_commissions': pending_list,
        }
    @api.model
    def action_approve_commission(self, commission_id):
        commission = self.env['referral.commission'].browse(commission_id)
        commission.action_approve()
        return True

    @api.model
    def action_reject_commission(self, commission_id):
        commission = self.env['referral.commission'].browse(commission_id)
        commission.action_reject()
        return True