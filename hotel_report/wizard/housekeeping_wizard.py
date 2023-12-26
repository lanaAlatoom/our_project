# from odoo import models, fields, api, exceptions, _
# from odoo.exceptions import ValidationError, AccessError, UserError
# from datetime import date, timedelta
# import time

# class WaelHotelWizard(models.TransientModel):
#     _name = "housekeeping.report.wizard"
#     _description = "housekeeping Hotel Wizard"
#
#     name_id = fields.Many2one('res.users', string='Name', default=lambda self: self.env.user, readonly=True)
#     date_from = fields.Date('From Date', default=lambda *a: time.strftime('%Y-%m-%d'), required=True, readonly=True)

    # def check_report(self):
    #     data = {}
    #
    #     return self.env.ref(
    #         'hotel_report.action_wael_hotel_report').report_action(self, data=data)

    # def print_report(self):
    #     mm_ids = self.env['hotel.housekeeping'].search([('state', 'in', ['dirty', 'clean'])])
    #     liss_line_ids = []
    #     for line in mm_ids:
    #         liss_line_ids.append({
    #             'Room No': line.room_no.name,
    #             'State': line.state,
    #
    #         })
    #     data = {
    #         'model': self._name,
    #         'name_id': self.name_id.name,
    #         'lis_line_ids': liss_line_ids,
    #         'date_from': self.date_from,
    #
    #     }
    #     return self.env.ref('hotel_report.action_mmm_housekeeping_report').report_action(self, data=data)
