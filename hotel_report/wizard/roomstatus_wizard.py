from dateutil.utils import today
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import date, timedelta

from datetime import date


class WaelHotelWizard(models.TransientModel):
    _name = "roomstatus.report.wizard"
    _description = "Room Status Hotel Wizard"

    name_id = fields.Many2one('res.users', string='Name', default=lambda self: self.env.user, readonly=True)
    date_from = fields.Date(string='Date', default=fields.Date.today(), readonly=True)

    def print_report(self):
        today = date.today()

        mm_ids = self.env['hotel.room'].search([])
        liss_line_ids = []
        for line in mm_ids:


            liss_line_ids.append({
                'Room No': line.name,
                'Folio Status': line.state_folio,
                'State': line.status_housekeeping,
            })
        data = {
            'model': self._name,
            'name_id': self.name_id.name,
            'lis_line_ids': liss_line_ids,
            'date_from': self.date_from,
        }
        return self.env.ref('hotel_report.action_msm_roomstatus_report').report_action(self, data=data)
