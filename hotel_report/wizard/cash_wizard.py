from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import datetime, timedelta, time
import base64


class WaelCrmWizard(models.TransientModel):
    _name = "cash.report.wizard"
    _description = "cash Hotel Wizard"

    partner_id = fields.Many2one('res.partner', string='Partner')

    @api.model
    def _default_date_form(self):
        today = fields.Date.context_today(self)
        default_datetime = datetime.combine(today, time(6, 0, 0))
        return fields.Date.to_string(default_datetime.date())

    @api.model
    def _default_date_to(self):
        today = fields.Date.context_today(self)
        tomorrow_datetime = datetime.combine(today, time(6, 0, 0)) + timedelta(days=1)
        return fields.Date.to_string(tomorrow_datetime.date())

    date_form = fields.Date(string='Date from', default=_default_date_form)
    date_to = fields.Date(string='Date To', default=_default_date_to)

    @api.onchange('date_form')
    def _onchange_date_from(self):
        if self.date_form:
            default_datetime = datetime.combine(self.date_form, time(6, 0, 0)) + timedelta(days=1)
            self.date_to = default_datetime

    def print_report(self):
        cash_journal = self.env['account.journal'].search([('type', 'in', ['cash', 'bank']), ('name', '=', 'Cash')])
        refund_journal = self.env['account.journal'].search([('type', 'in', ['cash', 'bank']), ('name', '=', 'Refund')])
        visa_journal = self.env['account.journal'].search([('name', '=', 'Visa')])

        start_datetime = datetime.combine(self.date_form, time(hour=6))
        end_datetime = datetime.combine(self.date_to, time(hour=6))

        cash_line_ids = self.env['account.payment'].search([
            ('create_date', '>=', start_datetime),
            ('create_date', '<', end_datetime),
            ('journal_id', 'in', [cash_journal.id, refund_journal.id])
        ])

        visa_line_ids = self.env['account.payment'].search([
            ('create_date', '>=', start_datetime),
            ('create_date', '<', end_datetime),
            ('journal_id', '=', visa_journal.id)
        ])

        cash_lisst_line_ids = []
        visa_lisst_line_ids = []

        for line in cash_line_ids:
            cash_lisst_line_ids.append({
                'date': line.date,
                'rooms_ref': line.room_number,
                'journal': line.journal_id.name,
                'Amount': line.amount_company_currency_signed,
                'customer': line.partner_id.name,
                'Created by': line.create_uid.name,
            })

        for line in visa_line_ids:
            visa_lisst_line_ids.append({
                'date': line.date,
                'rooms_ref': line.room_number,
                'journal': line.journal_id.name,
                'Amount': line.amount_company_currency_signed,
                'customer': line.partner_id.name,
                'Created by': line.create_uid.name,
            })

        cash_total_amount = sum(line['Amount'] for line in cash_lisst_line_ids)
        visa_total_amount = sum(line['Amount'] for line in visa_lisst_line_ids)

        data = {
            'model': self._name,
            'date_form': self.date_form,
            'date_to': self.date_to,
            'cash_lisst_line_ids': cash_lisst_line_ids,
            'visa_lisst_line_ids': visa_lisst_line_ids,
            'cash_total_amount': cash_total_amount,
            'visa_total_amount': visa_total_amount,
        }

        return self.env.ref('hotel_report.action_eee_hotel_report').report_action(self, data=data)

    def send_email_with_pdf_attach(self):
        cash_journal = self.env['account.journal'].search([('type', 'in', ['cash', 'bank']), ('name', '=', 'Cash')])
        refund_journal = self.env['account.journal'].search([('type', 'in', ['cash', 'bank']), ('name', '=', 'Refund')])
        visa_journal = self.env['account.journal'].search([('name', '=', 'Visa')])

        start_datetime = datetime.combine(self.date_form, time(hour=6))
        end_datetime = datetime.combine(self.date_to, time(hour=6))

        cash_line_ids = self.env['account.payment'].search([
            ('create_date', '>=', start_datetime),
            ('create_date', '<', end_datetime),
            ('journal_id', 'in', [cash_journal.id, refund_journal.id])
        ])

        visa_line_ids = self.env['account.payment'].search([
            ('create_date', '>=', start_datetime),
            ('create_date', '<', end_datetime),
            ('journal_id', '=', visa_journal.id)
        ])

        cash_lisst_line_ids = []
        visa_lisst_line_ids = []

        for line in cash_line_ids:
            cash_lisst_line_ids.append({
                'date': line.date,
                'rooms_ref': line.room_number,
                'journal': line.journal_id.name,
                'Amount': line.amount_company_currency_signed,
                'customer': line.partner_id.name,
                'Created by': line.create_uid.name,
            })

        for line in visa_line_ids:
            visa_lisst_line_ids.append({
                'date': line.date,
                'rooms_ref': line.room_number,
                'journal': line.journal_id.name,
                'Amount': line.amount_company_currency_signed,
                'customer': line.partner_id.name,
                'Created by': line.create_uid.name,
            })

        cash_total_amount = sum(line['Amount'] for line in cash_lisst_line_ids)
        visa_total_amount = sum(line['Amount'] for line in visa_lisst_line_ids)

        data = {
            'model': self._name,
            'date_form': self.date_form,
            'date_to': self.date_to,
            'cash_lisst_line_ids': cash_lisst_line_ids,
            'visa_lisst_line_ids': visa_lisst_line_ids,
            'cash_total_amount': cash_total_amount,
            'visa_total_amount': visa_total_amount,
        }

        generated_report = self.env['ir.actions.report'].sudo().with_context()._render_qweb_pdf(
            "hotel_report.action_eee_hotel_report", data=data)[0]
        data_record = base64.b64encode(generated_report).decode()
        ir_values = {
            'name': 'Cash Report',
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/pdf',
            'res_model': 'cash.report.wizard',
        }

        report_attachment = self.env['ir.attachment'].sudo().create(ir_values)
        self.env['mail.mail'].sudo().create({
            'model': self._name,
            'subject': 'Cash Report',
            'email_to': 'alatoomlana@gmail.com',
            'email_from': 'lanaabedalmajeed@gmail.com',
            'attachment_ids': [(4, report_attachment.id)],
        }).send()















  # كووووود شغال


        #
        #
        # cash_journal = self.env['account.journal'].search([('type', 'in', ['cash', 'bank']), ('name', '=', 'Cash')])
        # refund_journal = self.env['account.journal'].search([('type', 'in', ['cash', 'bank']), ('name', '=', 'Refund')])
        # visa_journal = self.env['account.journal'].search([('name', '=', 'Visa')])
        #
        # start_datetime = datetime.combine(self.date_form, time(hour=6))
        # end_datetime = datetime.combine(self.date_to, time(hour=6))
        #
        # cash_line_ids = self.env['account.payment'].search([
        #     ('create_date', '>=', start_datetime),
        #     ('create_date', '<', end_datetime),
        #     ('journal_id', 'in', [cash_journal.id, refund_journal.id])
        # ])
        #
        # visa_line_ids = self.env['account.payment'].search([
        #     ('create_date', '>=', start_datetime),
        #     ('create_date', '<', end_datetime),
        #     ('journal_id', '=', visa_journal.id)
        # ])
        #
        # cash_lisst_line_ids = []
        # visa_lisst_line_ids = []
        #
        # for line in cash_line_ids:
        #     cash_lisst_line_ids.append({
        #         'date': line.date,
        #         'rooms_ref': line.room_number,
        #         'journal': line.journal_id.name,
        #         'Amount': line.amount_company_currency_signed,
        #         'customer': line.partner_id.name,
        #         'Created by': line.create_uid.name,
        #     })
        #
        # for line in visa_line_ids:
        #     visa_lisst_line_ids.append({
        #         'date': line.date,
        #         'rooms_ref': line.room_number,
        #         'journal': line.journal_id.name,
        #         'Amount': line.amount_company_currency_signed,
        #         'customer': line.partner_id.name,
        #         'Created by': line.create_uid.name,
        #     })
        #
        # cash_total_amount = sum(line['Amount'] for line in cash_lisst_line_ids)
        # visa_total_amount = sum(line['Amount'] for line in visa_lisst_line_ids)
        #
        # data = {
        #     'model': self._name,
        #     'date_form': self.date_form,
        #     'date_to': self.date_to,
        #     'cash_lisst_line_ids': cash_lisst_line_ids,
        #     'visa_lisst_line_ids': visa_lisst_line_ids,
        #     'cash_total_amount': cash_total_amount,
        #     'visa_total_amount': visa_total_amount,
        # }
        #
        # generated_report = self.env['ir.actions.report'].sudo().with_context()._render_qweb_pdf(
        #     "hotel_report.action_eee_hotel_report", data=data)[0]
        # data_record = base64.b64encode(generated_report).decode()
        # ir_values = {
        #     'name': 'Cash Report',
        #     'type': 'binary',
        #     'datas': data_record,
        #     'store_fname': data_record,
        #     'mimetype': 'application/pdf',
        #     'res_model': 'cash.report.wizard',
        # }
        # report_attachment = self.env['ir.attachment'].sudo().create(ir_values)
        # email_template = self.env.ref('hotel_report.mail_template_cash_report')
        # email_values = {
        #     'email_to': 'alatoomlana@gmail.com',
        #     'email_from': 'lanaabedalmajeed@gmail.com'
        # }
        #
        # email_template.attachment_ids = [(4, report_attachment.id)]
        # email_template.send_mail(self.id, email_values=email_values,
        #                         )
        # email_template.attachment_ids = [(5, 0, 0)]
        #
        #





        # self.env.ref('hotel_report.mail_template_cash_report').send_mail(self.id)

