from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import date, timedelta
import time
import requests
import base64


class WaelCrmWizard(models.TransientModel):
    _name = "police.report.wizard"
    _description = "Police Hotel Wizard"

    name_id = fields.Many2one('res.users', string='Name', default=lambda self: self.env.user, readonly=True)
    date_form = fields.Date('From Date', default=lambda *a: time.strftime('%Y-%m-%d'), required=True)

    @api.model
    def _default_date_to(self):
        default_date = fields.Date.today() + timedelta(days=1)
        return default_date

    date_to = fields.Date(string='Date To', default=_default_date_to)
    nationality_id = fields.Many2one('res.country', string='Nationality')
    report_binary = fields.Binary('Report Binary', readonly=True)

    selection_field = fields.Selection([
        ('occupied', 'Occupied'),
        ('history', 'History')],
        string='Selection Condition',
        default='occupied')

    def print_report_one(self):
        if self.selection_field == 'occupied':
            folio_domain = [('state', '=', 'draft')]
            folio_ids = self.env['hotel.folio'].search(folio_domain)
            line_ids = self.env['hotel.resv.id.details'].search([
                ('folio_id', 'in', folio_ids.ids),
            ])
        elif self.selection_field == 'history':
            if self.date_to <= fields.Date.today():
                folio_domain = [
                    ('checkin_date_id', '>=', self.date_form),
                    ('checkout_date_id', '<=', self.date_to)
                ]
                folio_ids = self.env['hotel.folio'].search(folio_domain)
                line_ids = self.env['hotel.resv.id.details'].search([
                    ('folio_id', 'in', folio_ids.ids),
                ])
            else:
                raise UserError('Date checkout error: Date To should be less than or equal to today.')

        list_line_ids = []
        for line in line_ids:
            if (not self.nationality_id or line.country_id == self.nationality_id):
                list_line_ids.append({
                    'guset name': line.partner_name.name,
                    'hotel rooom': line.hotel_rooom_id,
                    'document type': line.client_id.name,
                    'id card number': line.name,
                    'Checkin Date': line.checkin_date.date(),
                    'gender': line.gender,
                    'date of birth': line.date_birth,
                    'Nationality': line.country_id.name,
                })

        data = {
            'model': self._name,
            'date_form': self.date_form,
            'date_to': self.date_to,
            'name_id': self.name_id.name,
            'selection_field': self.selection_field,
            'list_line_ids': list_line_ids,
        }
        return self.env.ref('hotel_report.action_wael_hotel_report').report_action(self, data=data)

    def print_report(self):
        folio_domain = [('state', '=', 'draft')]
        folio_ids = self.env['hotel.folio'].search(folio_domain)
        line_ids = self.env['hotel.resv.id.details'].search([('folio_id', 'in', folio_ids.ids)])
        list_line_ids = []
        for line in line_ids:
            list_line_ids.append({
                'guset name': line.partner_name.name,
                'hotel rooom': line.hotel_rooom_id,
                'document type': line.client_id.name,
                'id card number': line.name,
                'Checkin Date': line.checkin_date.date(),
                'gender': line.gender,
                'date of birth': line.date_birth,
                'Nationality': line.country_id.name,

            })
        data = {
            'model': self._name,
            'date_from': self.date_from,
            'nationality_id': self.nationality_id.name,
            'name_id': self.name_id.name,
            'list_line_ids': list_line_ids,

        }

        pdf = self.env['ir.actions.report'].sudo().with_context()._render_qweb_pdf(
            "hotel_report.action_wael_hotel_report", data=data)[0]

        report_binary = base64.b64encode(pdf).decode()
        return report_binary

    def share_in_whatsapp(self):
        try:
            report_binary = self.print_report()
            url = "https://api.ultramsg.com/instance60998/messages/document"
            payload = {
                'token': '7csyp9hatqw98593',
                'to': '+962791790092',
                'filename': 'police_report.pdf',
                'document': report_binary,
            }
            headers = {'content-type': 'application/x-www-form-urlencoded'}

            response = requests.post(url, data=payload, headers=headers)

            if response.status_code == 200:
                print("Document sent successfully.")
            else:
                print(f"Failed to send document. Status code: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
