from odoo import fields, models

class PosConfiguration(models.Model):
    _inherit = 'pos.config'

    is_pos_takeaway = fields.Boolean(
        string='POS TakeAway',
        help='TakeAway, Dine-in on Restaurant',
    )
    is_pos_delivery = fields.Boolean(
        string='POS Delivery',
        help='Delivery, Dine-in on Restaurant',
    )
    is_pos_order_phone = fields.Boolean(
        string='POS Order Phone',
        help='Order Phone, Dine-in on Restaurant',
    )
    is_pos_talabat = fields.Boolean(
        string='POS Order Talabat',
        help='Order Talabat, POS Talabat Notes',
    )
    is_generate_token = fields.Boolean(
        string='Generate Token',
        help='Generate Token Number',
    )
    pos_token = fields.Integer(
        string="Token Number",
        help="Token number starts from 1",
    )

    allow_open_cash_d = fields.Boolean('Open Cash Drawer',default=True)



