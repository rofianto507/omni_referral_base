from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class ReferralMember(models.Model):
    _name = "referral.member"
    _description = "Referral Member"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"
    _rec_name = "display_name"

    partner_id = fields.Many2one(
        "res.partner",
        string="Contact",
        required=True,
        ondelete="restrict",
        domain=[("referral_member_ids", "=", False),("is_company", "=", False)],
        tracking=True,
    )
    phone = fields.Char(
        string="Mobile",
        related="partner_id.phone",
        readonly=False,
        store=True,
    )
    email = fields.Char(
        string="Email",
        related="partner_id.email",
        readonly=False,
        store=True,
    )
    partner_image = fields.Image(
        string='Photo',
        compute='_compute_partner_image',
        inverse='_inverse_partner_image',
        readonly=False,
        store=False,
    )
    member_code = fields.Char(
        string="Member Code",
        required=True,
        copy=False,
        index=True,
        readonly=True,
        default="/",
    )
    sponsor_id = fields.Many2one(
        "referral.member",
        string="Sponsor",
        ondelete="restrict",
        index=True,
        tracking=True,
        domain="[('state', '=', 'active'), ('id', '!=', id)]",
    )
    join_date = fields.Date(
        string="Join Date",
        required=True,
        default=fields.Date.context_today,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("suspended", "Suspended"),
            ("terminated", "Terminated"),
        ],
        string="Status",
        required=True,
        default="draft",
        index=True,
            tracking=True,
    )

    display_name = fields.Char(
        string="Name",
        compute="_compute_display_name",
        store=True,
    )

    downline_ids = fields.One2many(
        "referral.member",
        "sponsor_id",
        string="Direct Downlines",
    )
    downline_count = fields.Integer(
        string="Direct Downlines",
        compute="_compute_downline_count",
    )
    commission_ids = fields.One2many(
        'referral.commission',
        'beneficiary_member_id',
        string='Commissions',
    )
    activated_at = fields.Datetime(readonly=True, tracking=True)
    suspended_at = fields.Datetime(readonly=True, tracking=True)
    terminated_at = fields.Datetime(readonly=True, tracking=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    commission_withdrawn = fields.Monetary(
        string='Total Withdrawn',
        currency_field='currency_id',
        default=0.0,
        readonly=True,
        help='Commission amount that has been withdrawn by the member. This is used for reference and does not affect the current balance directly, as balance is computed based on approved commissions minus withdrawn amounts.',
    )
    commission_balance = fields.Monetary(
        string='Commission Balance',
        currency_field='currency_id',
        compute='_compute_commission_balance',
        store=True,
        help='Current commission balance available for withdrawal. Computed as the sum of approved commissions minus total withdrawn amount. This field is read-only and updated automatically when commissions are approved or withdrawn.',
    )
    withdraw_ids = fields.One2many(
        'commission.withdraw',
        'member_id',
        string='Withdrawals',
    )
    sale_order_ids = fields.One2many(
        'sale.order',
        'referral_member_id',
        string='Sales Orders',
    )
    sale_order_count = fields.Integer(
        string='Sales Orders',
        compute='_compute_sale_order_count',
    )
    commission_count = fields.Integer(
        string='Total Commissions',
        compute='_compute_commission_count',
    )
    withdraw_count = fields.Integer(
        string='Total Withdrawals',
        compute='_compute_withdraw_count',
    )
    commission_total_earned = fields.Monetary(
        string='Total Earned',
        currency_field='currency_id',
        compute='_compute_commission_summary',
        store=True,
        help='Commission total earned by the member. This includes all commissions regardless of their approval status.',
    )
    commission_total_pending = fields.Monetary(
        string='Total Pending',
        currency_field='currency_id',
        compute='_compute_commission_summary',
        store=True,
        help='Commission total that is currently pending approval. This amount is not yet available for withdrawal.',
    )
    _sql_constraints = [
        ("uniq_member_code", "unique(member_code)", "Member Code must be unique."),
        ("uniq_partner_member", "unique(partner_id)", "Contact is already registered as a member."),
    ]

    def _compute_partner_image(self):
        for rec in self:
            rec.partner_image = rec.partner_id.image_128 if rec.partner_id else False

    def _inverse_partner_image(self):
        for rec in self:
            if rec.partner_id:
                rec.partner_id.image_128 = rec.partner_image
    
    @api.depends('downline_ids')
    def _compute_downline_count(self):
        for rec in self:
            rec.downline_count = len(rec.downline_ids)

    def _compute_sale_order_count(self):
        for rec in self:
            rec.sale_order_count = len(rec.sale_order_ids)

    def _compute_commission_count(self):
        for rec in self:
            rec.commission_count = len(rec.commission_ids)

    def _compute_withdraw_count(self):
        for rec in self:
            rec.withdraw_count = len(rec.withdraw_ids)

    @api.depends(
        'commission_ids.state',
        'commission_ids.commission_amount',
        'commission_ids.currency_id',
    )
    def _compute_commission_summary(self):
        for rec in self:
            approved = rec.commission_ids.filtered(lambda c: c.state == 'approved')
            pending = rec.commission_ids.filtered(lambda c: c.state == 'pending')
            rec.commission_total_earned = sum(
                c.currency_id._convert(
                    c.commission_amount, rec.currency_id,
                    rec.env.company, fields.Date.today(),
                ) for c in approved
            )
            rec.commission_total_pending = sum(
                c.currency_id._convert(
                    c.commission_amount, rec.currency_id,
                    rec.env.company, fields.Date.today(),
                ) for c in pending
            )
    @api.depends(
        'commission_ids.state',
        'commission_ids.commission_amount',
        'commission_ids.currency_id',
        'commission_withdrawn',
    )
    def _compute_commission_balance(self):
        for rec in self:
            approved = rec.commission_ids.filtered(lambda c: c.state == 'approved')
            total_approved = sum(
                c.currency_id._convert(
                    c.commission_amount,
                    rec.currency_id,
                    rec.env.company,
                    fields.Date.today(),
                ) for c in approved
            )
            rec.commission_balance = total_approved - rec.commission_withdrawn

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env["ir.sequence"]
        for vals in vals_list:
            if not vals.get("member_code") or vals.get("member_code") == "/":
                vals["member_code"] = seq.next_by_code("omni.referral.member.code") or "/"
        return super().create(vals_list)

    @api.depends("member_code", "partner_id.name")
    def _compute_display_name(self):
        for rec in self:
            partner_name = rec.partner_id.name or ""
            code = rec.member_code or "-"
            rec.display_name = f"[{code}] {partner_name}"

    @api.depends("downline_ids")
    def _compute_downline_count(self):
        for rec in self:
            rec.downline_count = len(rec.downline_ids)

    @api.constrains("sponsor_id")
    def _check_no_self_sponsor(self):
        for rec in self:
            if rec.sponsor_id and rec.sponsor_id == rec:
                raise ValidationError(_("A member cannot sponsor themselves."))
    @api.constrains("sponsor_id")
    def _check_sponsor_must_be_active(self):
        for rec in self:
            if rec.sponsor_id and rec.sponsor_id.state != "active":
                raise ValidationError(_("Sponsor must be in Active status."))
    @api.constrains("sponsor_id")
    def _check_no_circular_sponsor(self):
        for rec in self:
            visited = set()
            current = rec.sponsor_id
            while current:
                if current.id in visited:
                    break
                if current == rec:
                    raise ValidationError(_("Circular sponsor hierarchy is not allowed."))
                visited.add(current.id)
                current = current.sponsor_id
    def action_activate(self):
        for rec in self:
            if rec.state == "terminated":
                raise UserError(_("Terminated member cannot be activated again."))
            rec.state = "active"
            rec.activated_at = fields.Datetime.now()

    def action_suspend(self):
        for rec in self:
            if rec.state != "active":
                raise UserError(_("Only active members can be suspended."))
            rec.state = "suspended"
            rec.suspended_at = fields.Datetime.now()

    def action_reactivate(self):
        for rec in self:
            if rec.state != "suspended":
                raise UserError(_("Only suspended members can be reactivated."))
            rec.state = "active"

    def action_terminate(self):
        for rec in self:
            if rec.state == "terminated":
                continue
            rec.state = "terminated"
            rec.terminated_at = fields.Datetime.now()

    def action_print_member_card(self):
        self.ensure_one()
        url = '/report/html/omni_referral_base.report_member_card/%s' % self.id       
        return {
            'type': 'ir.actions.act_url',
            'name': 'Print Member Card',
            'url': url,
            'target': 'new',
        }
    
    def action_withdraw(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Request Withdrawal'),
            'res_model': 'withdraw.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_member_id': self.id,
            },
        }

    def action_view_sale_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sales Orders'),
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('referral_member_id', '=', self.id)],
        }

    def action_view_commissions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commissions'),
            'res_model': 'referral.commission',
            'view_mode': 'list,form',
            'domain': [('beneficiary_member_id', '=', self.id)],
        }

    def action_view_withdrawals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Withdrawals'),
            'res_model': 'commission.withdraw',
            'view_mode': 'list,form',
            'domain': [('member_id', '=', self.id)],
        }
    
    @api.model
    def get_referral_tree(self, member_id):
        """Return referral tree data as nested dict, depth = max commission rule level."""
        max_depth = self.env['commission.rule'].search_count([])
        if max_depth == 0:
            max_depth = 3  # fallback default

        member = self.browse(member_id)
        if not member.exists():
            return {}

        def build_node(m, current_depth):
            node = {
                'id': m.id,
                'name': m.partner_id.name or '-',
                'member_code': m.member_code or '-',
                'state': m.state,
                'commission_balance': m.commission_balance,
                'downline_count': m.downline_count,
                'avatar_url': '/web/image/res.partner/%d/image_128' % m.partner_id.id if m.partner_id else False,
                'children': [],
            }
            if current_depth < max_depth:
                for child in m.downline_ids:
                    node['children'].append(build_node(child, current_depth + 1))
            return node

        return build_node(member, 0)