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
    activated_at = fields.Datetime(readonly=True, tracking=True)
    suspended_at = fields.Datetime(readonly=True, tracking=True)
    terminated_at = fields.Datetime(readonly=True, tracking=True)

    _sql_constraints = [
        ("uniq_member_code", "unique(member_code)", "Member Code must be unique."),
        ("uniq_partner_member", "unique(partner_id)", "Contact is already registered as a member."),
    ]
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