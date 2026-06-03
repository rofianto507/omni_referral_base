from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    referral_member_ids = fields.One2many(
        "referral.member",
        "partner_id",
        string="Referral Members",
    )

    is_referral_member = fields.Boolean(
        string="Is Referral Member",
        compute="_compute_referral_member_info",
        store=False,
    )
    referral_member_id = fields.Many2one(
        "referral.member",
        string="Referral Member",
        compute="_compute_referral_member_info",
        store=False,
    )
    referral_member_code = fields.Char(
        string="Member Code",
        compute="_compute_referral_member_info",
        store=False,
    )
    referral_join_date = fields.Date(
        string="Join Date",
        compute="_compute_referral_member_info",
        store=False,
    )
    referral_sponsor_id = fields.Many2one(
        "referral.member",
        string="Sponsor",
        compute="_compute_referral_member_info",
        store=False,
    )

    @api.depends(
        "referral_member_ids",
        "referral_member_ids.member_code",
        "referral_member_ids.join_date",
        "referral_member_ids.sponsor_id",
    )
    def _compute_referral_member_info(self):
        for partner in self:
            member = partner.referral_member_ids[:1]
            if member:
                partner.is_referral_member = True
                partner.referral_member_id = member.id
                partner.referral_member_code = member.member_code
                partner.referral_join_date = member.join_date
                partner.referral_sponsor_id = member.sponsor_id.id
            else:
                partner.is_referral_member = False
                partner.referral_member_id = False
                partner.referral_member_code = False
                partner.referral_join_date = False
                partner.referral_sponsor_id = False