from odoo import models, fields,api
from datetime import datetime, timedelta


class LogisticProviders(models.Model):
    _name = 'logistic.providers'
    _description = 'Logistic Providers'
    _order = "sequence"

    sequence = fields.Integer('Sequence')
    name = fields.Char(string='Providers Name', required=True)
    contact = fields.Char(string='Contact')
    phone = fields.Char(string='Phone')
    service_type = fields.Selection([('truck', 'Truck'), ('ship', 'Ship'), ('air', 'Air')], string='Type of Service')
    lead_time = fields.Integer(string='Lead Time (Days)')
    shipping_cost = fields.Float(string='Shipping Cost')
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', ondelete='cascade')

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    logistic_provider_ids = fields.Many2many('logistic.providers',  string='Logistic Providers')

    @api.onchange('logistic_provider_ids')
    def _compute_date_planned(self):
        if self.logistic_provider_ids:
            # Take the maximum lead time from the selected logistic providers
            max_lead_time = max(provider.lead_time for provider in self.logistic_provider_ids)
            self.date_planned = self.date_order + timedelta(days=max_lead_time)
