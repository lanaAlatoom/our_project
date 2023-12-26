from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import date, timedelta
import time

class WaelHotelWizard(models.TransientModel):
    _name = "mael.report.wizard"
    _description = "mael Hotel Wizard"

    name_id = fields.Many2one('res.users', string='Name', default=lambda self: self.env.user, readonly=True)
    date_from = fields.Date('From Date', default=lambda *a: time.strftime('%Y-%m-%d'), required=True, readonly=True)

    def print_report(self):
        today = date.today()

        mm_ids = self.env['hotel.reservation'].search([])
        liss_line_ids = []
        for line in mm_ids:
            checkin_date = line.checking_date.strftime('%Y-%m-%d') if line.checking_date else ''
            checkout_date = line.checking_out_date.strftime('%Y-%m-%d') if line.checking_out_date else ''

            liss_line_ids.append({
                'Meal type': line.meal_id,
                'Adults': line.adults,
                'children': line.childs,
                'Room number': line.room_number_id.name,
                'Checkin Date': checkin_date,
                'Checkout Date': checkout_date,
                'Nationality': line.country_name.name,

            })



        data = {
            'model': self._name,
            'name_id': self.name_id.name,
            'lis_line_ids': liss_line_ids,
            'date_from': self.date_from,
        }

        return self.env.ref('hotel_report.action_mae_mael_report').report_action(self, data=data)
