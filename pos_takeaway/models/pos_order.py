from odoo import api, fields, models

class PosOrder(models.Model):
    _inherit = 'pos.order'

    is_takeaway = fields.Boolean(default=False, string="Is a Takeaway Order", help="Is a Takeaway Order")
    is_delivery = fields.Boolean(default=False, string="Is a Delivery Order", help="Is a Delivery Order")
    is_order_phone = fields.Boolean(default=False, string="Is an Order Phone", help="Is an Order Phone")
    is_pos_talabat = fields.Boolean(default=False, string="Is an Order Talabat", help="Is an Order Phone")

    @api.model
    def token_generate(self, uid):
        uid = "Order " + uid[0]
        order = self.env['pos.order'].search([
            ('pos_reference', 'ilike', uid)], limit=1)
        if order:
            if order.is_takeaway or order.is_delivery or order.is_order_phone:
                order.is_takeaway = True if order.is_takeaway else False
                order.is_delivery = True if order.is_delivery else False
                order.is_order_phone = True if order.is_order_phone else False
                order.is_pos_talabat = True if order.is_pos_talabat else False
                if order.config_id and order.config_id.is_generate_token:
                    order.config_id.pos_token += 1
                    return order.config_id.pos_token
