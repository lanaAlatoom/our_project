from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import date, timedelta
import time



class WaelCrmWizard(models.TransientModel):
    _name = "daily.report.wizard"
    _description = "daily Hotel Wizard"

    date_form = fields.Date('From Date', default=lambda *a: time.strftime('%Y-%m-%d'), required=True)

    @api.model
    def _default_date_to(self):
        default_date = fields.Date.today() + timedelta(days=1)
        return default_date

    date_to = fields.Date(string='Date To', default=_default_date_to)




    # def check_report(self):
    #     data = {}
    #
    #     return self.env.ref(
    #         'police_report.action_wael_hotel_report').report_action(self, data=data)

    def print_report(self):
        linne_ids = self.env['hotel.folio'].search([('create_date', '>=', self.date_form), ('create_date', '<=', self.date_to)])
        lisst_line_ids = []
        for line in linne_ids:
            lisst_line_ids.append({
                'Guest Name': line.partner_id.name,
                'Room Number': line.rooms_ref,
                'Taxes': line.amount_tax,
                'Total': line.amount_total,
                'chickin': line.checkin_date_id,
                'chickout': line.checkout_date_id,
                'Created by': line.create_uid.name,


            })

        data = {
            'model': self._name,
            'date_form': self.date_form,
            'date_to': self.date_to,
            'lisst_line_ids': lisst_line_ids,

               }
        return self.env.ref('hotel_report.action_ewe_hotel_report').report_action(self, data=data)
