from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import date, timedelta
import time

class WaelHotelWizard(models.TransientModel):
    _name = "remaining.report.wizard"
    _description = "remaining Hotel Wizard"

    name_id = fields.Many2one('res.users', string='Name', default=lambda self: self.env.user, readonly=True)
    date_from = fields.Date('From Date', default=lambda *a: time.strftime('%Y-%m-%d'), required=True, readonly=True)

    # def check_report(self):
    #     data = {}
    #
    #     return self.env.ref(
    #         'hotel_report.action_wael_hotel_report').report_action(self, data=data)

    def print_report(self):
        wael_ids = self.env['hotel.folio'].search([('state', '=', 'draft')])
        lis_line_ids = []
        for line in wael_ids:
            lis_line_ids.append({
                'Guest_Name': line.partner_id.name,
                'total_Remaining': line.remaining_amt,
                'room_number': line.rooms_ref,
                'Reservation_ref': line.reservation_id.name,

            })
        data = {
            'model': self._name,
            'name_id': self.name_id.name,
            'lis_line_ids': lis_line_ids,
            'date_from': self.date_from,

        }
        return self.env.ref('hotel_report.action_wael_remaining_report').report_action(self, data=data)
