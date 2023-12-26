from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import datetime, timedelta, time



class hotel_folio(models.Model):
    _inherit = "hotel.folio"
    _description = "Hotel Folio"

    Discou = fields.Float(string='discound', related='order_line_id.discount_amount')
    trans = fields.Char(string='lebel', related='journal_entry_ids.name')
    deb = fields.Monetary(string='debt', related='journal_entry_ids.debit')
    crd = fields.Monetary(string='crad', related='journal_entry_ids.credit')

class AccountsPayments(models.Model):
    _inherit = 'account.payment'

    discount_amount1 = fields.Char(string='dascount', compute='_compute_desc_number')
    name23 = fields.Char(string='descrb', compute='_compute_doo_number')
    deeb = fields.Char(string='was', compute='_compute_tran_number')
    crrd = fields.Char(string='wel', compute='_compute_cred_number')

    def _compute_desc_number(self):
        for payment in self:
            if payment.ref:
                reservation = self.env['hotel.folio'].search([('reservation_id', '=', payment.ref)], limit=1)
                if reservation:
                    payment.discount_amount1 = reservation.Discou
                else:
                    payment.discount_amount1 = False
            else:
                payment.discount_amount1 = False

    def _compute_doo_number(self):
        for payment in self:
            if payment.ref:
                reservation = self.env['hotel.folio'].search([('reservation_id', '=', payment.ref)], limit=1)
                if reservation:
                    payment.name23 = reservation.trans
                else:
                    payment.name23 = False
            else:
                payment.name23 = False

    def _compute_tran_number(self):
        for payment in self:
            if payment.ref:
                reservation = self.env['hotel.folio'].search([('reservation_id', '=', payment.ref)], limit=1)
                if reservation:
                    payment.deeb = reservation.deb
                else:
                    payment.deeb = False
            else:
                payment.deeb = False

    def _compute_cred_number(self):
        for payment in self:
            if payment.ref:
                reservation = self.env['hotel.folio'].search([('reservation_id', '=', payment.ref)], limit=1)
                if reservation:
                    payment.crrd = reservation.crd
                else:
                    payment.crrd = False
            else:
                payment.crrd = False


class WaelHotelWizard(models.TransientModel):
    _name = "cashier.report.wizard"
    _description = "Cashier Hotel Wizard"

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

    # @api.onchange('date_form')
    # def _onchange_date_from(self):
    #     if self.date_form:
    #         default_datetime = datetime.combine(self.date_form, time(6, 0, 0)) + timedelta(days=1)
    #         self.date_to = default_datetime

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
                'discount': line.discount_amount1,
                'lebels': line.name23,
                'debit': line.deeb,
                'credit': line.crrd,
            })

        for line in visa_line_ids:
            visa_lisst_line_ids.append({
                'date': line.date,
                'rooms_ref': line.room_number,
                'journal': line.journal_id.name,
                'Amount': line.amount_company_currency_signed,
                'customer': line.partner_id.name,
                'Created by': line.create_uid.name,
                'discount': line.discount_amount1,
                'lebels': line.name23,
                'debit': line.deeb,
                'credit': line.crrd,
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

        return self.env.ref('hotel_report.action_maan_chart_report').report_action(self, data=data)
