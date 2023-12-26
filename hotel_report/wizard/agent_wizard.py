from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import date, timedelta
import time
import requests
import base64

class hotel_folio(models.Model):
    _inherit = "hotel.folio"
    _description = "Hotel Folio"


    nigth = fields.Float(string='nigths', related='order_line_id.product_uom_qty')

class WaelCrmWizard(models.TransientModel):
    _name = "agent.report.wizard"
    _description = "agent Hotel Wizard"

    date_form = fields.Date('From Date', default=lambda *a: time.strftime('%Y-%m-%d'), required=True)

    @api.model
    def _default_date_to(self):
        default_date = fields.Date.today() + timedelta(days=1)
        return default_date

    date_to = fields.Date(string='Date To', default=_default_date_to)
    agenta_id = fields.Many2one('res.partner', string='Agent', )

    def print_report(self):
        folio_domain = [('via', '=', 'agent')]
        folio_ids = self.env['hotel.reservation'].search(folio_domain)
        line_ids = self.env['hotel.folio'].search([
            ('reservation_id', 'in', folio_ids.ids),
            ('create_date', '>=', self.date_form),
            ('create_date', '<=', self.date_to),
            ('state', '=', 'done')
        ])

        lisstw_line_ids = []
        for line in line_ids:
            if (not self.agenta_id or line.agent_id == self.agenta_id):
                lisstw_line_ids.append({
                    'Guest Name': line.partner_id.name,
                    'Room Number': line.rooms_ref,
                    'agent': line.agent_id.name,
                    'nigh': line.nigth,
                    'chickin': line.checkin_date_id.date(),
                    'chickout': line.checkout_date_id.date(),
                    'Total': line.amount_total,
                    'Created by': line.create_uid.name,

                })

        data = {
            'model': self._name,
            'date_form': self.date_form,
            'date_to': self.date_to,
            'lisstw_line_ids': lisstw_line_ids,

        }
        return self.env.ref('hotel_report.action_agg_hotel_report').report_action(self, data=data)
