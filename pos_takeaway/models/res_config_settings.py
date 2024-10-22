from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_takeaway = fields.Boolean(
        string='POS TakeAway',
        related="pos_config_id.is_pos_takeaway",
        help="TakeAway, Dine-in on Restaurant",
        readonly=False,
    )
    is_delivery = fields.Boolean(
        string='POS Delivery',
        related="pos_config_id.is_pos_delivery",
        help="Delivery, Dine-in on Restaurant",
        readonly=False,
    )
    is_talabat = fields.Boolean(
        string='POS Talabat',
        related="pos_config_id.is_pos_talabat",
        help="post order note talabat app",
        readonly=False,
    )
    is_order_phone = fields.Boolean(
        string='POS Order Phone',
        related="pos_config_id.is_pos_order_phone",
        help="Order Phone, Dine-in on Restaurant",
        readonly=False,
    )
    is_generate_token = fields.Boolean(
        string='Generate Token',
        related="pos_config_id.is_generate_token",
        help="This Token number starts from 1",
        readonly=False,
    )
    pos_token = fields.Integer(
        string="Token",
        help="The token will start from 1.",
        related="pos_config_id.pos_token"
    )

    allow_open_cash_d = fields.Boolean(related='pos_config_id.allow_open_cash_d', readonly=False)

