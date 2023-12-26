from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import datetime, timedelta, date
import calendar
import base64


class HotelFolio(models.Model):
    _inherit = "hotel.folio"
    _description = "Hotel Folio"

    # night_folio = fields.Float(related="order_line_id.product_uom_qty", string="Nights/Qty")
    # price_folio = fields.Float(related="order_line_id.price_unit", string="Price")
    # name_lable = fields.Char(string='lebel', related='journal_entry_ids.name')
    # debit = fields.Monetary(string='debit', related='journal_entry_ids.debit')
    # credit = fields.Monetary(string='credit', related='journal_entry_ids.credit')


class HotelFolio(models.Model):
    _inherit = "hotel_folio.line"
    _description = "Hotel Folio line"

    partner_id = fields.Many2one(related="folio_id.partner_id", string="Partner")


class DailyHotelWizard(models.TransientModel):
    _name = "managment.report.wizard"
    _description = "daily managment Hotel Wizard"

    date_from = fields.Datetime('From Date', required=True,
                                default=lambda *a: (datetime.now() - timedelta(days=1)).replace(hour=6, minute=0,
                                                                                                second=0))
    date_to = fields.Datetime('To Date', required=True,
                              default=lambda *a: datetime.now().replace(hour=6, minute=0, second=0))

    days_in_current_month = fields.Integer(
        string="Days in current month",
        compute="_compute_days_in_current_month"
    )

    @api.depends('date_from', 'date_to')
    def _compute_days_in_current_month(self):
        for wizard in self:
            search_year = wizard.date_to.year
            search_month = wizard.date_to.month

            days_in_current_month = calendar.monthrange(search_year, search_month)[1]

            wizard.days_in_current_month = days_in_current_month


    def print_report(self):
        global service_lisst_line_ids, food_lisst_line_ids
        search_date_from = (datetime.now() - timedelta(days=1)).replace(hour=6, minute=0, second=0)
        search_date_to = datetime.now().replace(hour=6, minute=0, second=0)

        total_room = len(self.env['hotel.room'].search([]))

        cash_line_ids = self.env['account.payment'].search([
            ('create_date', '>=', self.date_from), ('create_date', '<=', self.date_to)])

        cash_lisst_line_ids = []

        for line in cash_line_ids:
            cash_lisst_line_ids.append({
                'date': line.create_date,
                'rooms_ref': line.room_number,
                'journal': line.journal_id.name,
                'Amount': line.amount_company_currency_signed,
                'customer': line.partner_id.name,
                'Created by': line.create_uid.name,
            })

        transfer_line_ids = self.env['hotel.folio'].search([
            ('journal_entry_ids.create_date', '>=', self.date_from),
            ('checkout_date_id', '>=', self.date_from)])

        transfer_lisst_line_ids = []

        for line in transfer_line_ids:
            for lines in line.journal_entry_ids:
                transfer_lisst_line_ids.append({
                    'create_date': lines.create_date,
                    'rooms_ref': line.rooms_ref1,
                    'customer': line.partner_id.name,
                    'Created by': lines.create_uid.name,
                    'lebels': lines.name,
                    'debit': lines.debit,
                    'credit': lines.credit,
                })

        timesheet_line_ids = self.env['hr.attendance'].search([
            ('check_in', '>=', self.date_from), ('check_out', '<=', self.date_to)])
        timesheet_lisst_line_ids = []
        for line in timesheet_line_ids:
            if timesheet_line_ids:
                timesheet_lisst_line_ids.append({
                    'Employee': line.employee_id.name,
                    'Check in': line.check_in,
                    'Check out': line.check_out,
                    'Work hours': line.worked_hours,
                })

        housekeeping_line_ids = self.env['hotel.housekeeping'].search([
            ('create_date', '>=', self.date_from), ('create_date', '<=', self.date_to)])

        housekeeping_lisst_line_ids = []
        total_room_maintenance = 0
        total_room_checkin_dirty = 0
        total_room_checkout_dirty = 0
        for line in housekeeping_line_ids:
            housekeeping_lisst_line_ids.append({
                'Room Number': line.room_no.name,
                'Housekeeper': line.housekeeper.name,
                'Inspector': line.inspector.name,
                'Note': line.note,
                'Clean Type': line.clean_type,
                'Housekeeping Type': line.quality,

            })
            if line.quality == 'maintenance' and line.state == 'done':
                total_room_maintenance += 1

            if line.quality == 'cleaning' and line.clean_type == 'checkin' and line.state == 'done':
                total_room_checkin_dirty += 1

            if line.quality == 'cleaning' and line.clean_type == 'checkout' and line.state == 'done':
                total_room_checkout_dirty += 1


        balance_line_ids = self.env['hotel.folio'].search([
            ('checkout_date_id', '>=', self.date_to),
            ('checkin_date_id', '<=', self.date_to)
             ])

        balance_lisst_line_ids = []

        for line in balance_line_ids:
            for lines in line.room_lines:
                balance_lisst_line_ids.append({
                    'Room Number': lines.product_id.name,
                    'customer': lines.folio_id.partner_id.name,
                    'price': lines.price_unit,
                    'night': lines.product_uom_qty,
                    'check in': lines.checkin_date,
                    'check out': lines.checkout_date,
                    'discounts': lines.discount_amount,
                    'remaining amount': line.remaining_amt})

        current_date = date.today()

        # search_date_start = current_date.strftime('%Y-%m-%d 00:00:00')
        # search_date_end = current_date.strftime('%Y-%m-%d 23:59:59')
        # ota_line_ids = self.env['available.rooms'].search([
        #     ('date', '>=', search_date_start), ('date', '<=', search_date_end)])
        #
        # ota_lisst_line_ids = []
        #
        # for line in ota_line_ids:
        #     ota_lisst_line_ids.append({
        #         'Room Type': line.room_type_id.name,
        #         'Quantity In OTA': line.quantity,
        #         'price In OTA': line.price, })

        service_line_ids = self.env['hotel_service.line'].search([
            ('create_date', '>=', self.date_from), ('create_date', '<=', self.date_to)])

        service_lisst_line_ids = []
        for line in service_line_ids:
            service_lisst_line_ids.append({
                'Description': line.name,
                'Product': line.product_id.name,
                'price': line.price_unit,
                'Total': line.price_total, })

        food_line_ids = self.env['hotel_food.line'].search([
            ('create_date', '>=', self.date_from), ('create_date', '<=', self.date_to)])

        food_lisst_line_ids = []
        for line in food_line_ids:
            food_lisst_line_ids.append({
                'QTY': line.product_uom_qty,
                'Product': line.product_id.name,
                'price': line.price_unit,
                'Total': line.price_total, })

        laundry_line_ids = self.env['hotel_folio_laundry.line'].search([
            ('create_date', '>=', self.date_from), ('create_date', '<=', self.date_to)])

        laundry_lisst_line_ids = []
        for line in laundry_line_ids:
            laundry_lisst_line_ids.append({
                'QTY': line.product_uom_qty,
                'Product': line.product_id.name,
                'price': line.price_unit,
                'Total': line.price_total, })

        ledger_lisst_line_ids = []
        ledger_line_ids = self.env['account.move.line'].search([
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('amount_residual', '!=', 0),
            ('account_id.reconcile', '=', True),
            ('partner_id.agent', '=', True),
        ])

        ledger_data = {}
        for line in ledger_line_ids:
            partner_id = line.partner_id.id
            if partner_id not in ledger_data:
                ledger_data[partner_id] = {
                    'partner': line.partner_id.name,
                    'Debit': 0.0,
                    'Balance': 0.0,
                    'lines': [],
                }
            ledger_data[partner_id]['Debit'] += line.debit
            ledger_data[partner_id]['Balance'] += line.balance
            ledger_data[partner_id]['lines'].append({
                'Debit': line.debit,
                'label': line.name,
                'Balance': line.balance,
            })

        ledger_lisst_line_ids = list(ledger_data.values())

        # folio_line_ids = self.env['hotel_folio.line'].search([('create_date', '>=', self.date_from),
        #                                                       ('create_date', '<=', self.date_to)])
        #
        new_price = 0
        new_total = 0
        new_room = 0
        partner = ""
        # for folio_line in folio_line_ids:
        #     new_price = folio_line.price_unit
        #     new_total = folio_line.price_total
        #     new_room = folio_line.product_id.name
        #     partner = folio_line.partner_id.name

        move_lisst_line_ids = []

        move_lines = self.env['hotel.folio'].search([
            ('state', '!=', 'cancel'),
            ('moves_lines.create_date', '>=', self.date_from),
            ('moves_lines.create_date', '<=', self.date_to)
        ])
        unique_combinations = set()

        for line in move_lines:
            for move_line in line.moves_lines:
                for room_line in line.room_lines:
                    if move_line.name != 'Checkout':  # Check if trans_type is not 'Checkout'
                        # Define a unique key based on the relevant fields
                        unique_key = (
                            move_line.folio_id, move_line.create_date, line.partner_id.name, move_line.product_id.name,
                            move_line.name, move_line.price_unit, line.rooms_ref1, room_line.price_unit)

                        if unique_key not in unique_combinations:
                            move_line_data = {
                                'folio_id': move_line.folio_id,
                                'create_date': move_line.create_date,
                                'partner_name': line.partner_id.name,
                                'oldest_room': move_line.product_id.name,
                                'trans_type': move_line.name,
                                'oldest_price': move_line.price_unit,
                                'rooms_new': room_line.product_id.name,
                                'new_rate': room_line.price_unit,
                                'discounts': room_line.discount_amount,
                            }
                            move_lisst_line_ids.append(move_line_data)

                            unique_combinations.add(unique_key)

        print(move_lisst_line_ids)

        checkoutin_line_ids = self.env['hotel.room.booking.history'].search([])

        checkout_room_count = 0
        checkin_room_count = 0
        checkin_room_for_6am = 0

        for line in checkoutin_line_ids:
            if line.check_out >= self.date_from and line.check_out <= self.date_to and line.folio_state == 'sale':
                checkout_room_count += 1
            if line.check_in >= self.date_from and line.check_in <= self.date_to and line.folio_state == 'draft':
                checkin_room_count += 1
            if line.check_in <= self.date_to and line.folio_state == 'draft':
                checkin_room_for_6am += 1

        confirm_line_ids = self.env['hotel.reservation'].search([])

        confirm_room_count = 0
        confirm_room_count_fut = 0

        for line in confirm_line_ids:
            if isinstance(line.checking_date, datetime) and isinstance(self.date_from, datetime) and isinstance(
                    self.date_to, datetime):
                if self.date_from <= line.checking_date <= self.date_to and line.state == 'confirm':
                    confirm_room_count += 1

                if self.date_from <= line.checking_date and line.state == 'confirm':
                    confirm_room_count_fut += 1

        data = {
            'model': self._name,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'cash_lisst_line_ids': cash_lisst_line_ids,
            'timesheet_lisst_line_ids': timesheet_lisst_line_ids,
            'housekeeping_lisst_line_ids': housekeeping_lisst_line_ids,
            'transfer_lisst_line_ids': transfer_lisst_line_ids,
            'balance_lisst_line_ids': balance_lisst_line_ids,
            # 'ota_lisst_line_ids': ota_lisst_line_ids,
            'service_lisst_line_ids': service_lisst_line_ids,
            'food_lisst_line_ids': food_lisst_line_ids,
            'laundry_lisst_line_ids': laundry_lisst_line_ids,
            'ledger_lisst_line_ids': ledger_lisst_line_ids,
            'move_lisst_line_ids': move_lisst_line_ids,
            'checkout_room_count': checkout_room_count,
            'checkin_room_count': checkin_room_count,
            'checkin_room_for_6am': checkin_room_for_6am,
            'confirm_room_count_fut': confirm_room_count_fut,
            'confirm_room_count': confirm_room_count,
            'total_room_maintenance': total_room_maintenance,
            'total_room_checkin_dirty': total_room_checkin_dirty,
            'total_room_checkout_dirty': total_room_checkout_dirty,
            'New price': new_price,
            'New total': new_total,
            'Guast Name': partner,
            'total_room': total_room,
            'days_in_current_month': self.days_in_current_month,


        }

        return self.env.ref('hotel_report.action_management_daily_report').report_action(self, data=data)
    def send_by_email(self):
            global service_lisst_line_ids, food_lisst_line_ids
            search_date_from = (datetime.now() - timedelta(days=1)).replace(hour=6, minute=0, second=0)
            search_date_to = datetime.now().replace(hour=6, minute=0, second=0)

            total_room = len(self.env['hotel.room'].search([]))

            cash_line_ids = self.env['account.payment'].search([
                ('create_date', '>=', self.date_from), ('create_date', '<=', self.date_to)])

            cash_lisst_line_ids = []

            for line in cash_line_ids:
                cash_lisst_line_ids.append({
                    'date': line.create_date,
                    'rooms_ref': line.room_number,
                    'journal': line.journal_id.name,
                    'Amount': line.amount_company_currency_signed,
                    'customer': line.partner_id.name,
                    'Created by': line.create_uid.name,
                })

            transfer_line_ids = self.env['hotel.folio'].search([
                ('journal_entry_ids.create_date', '>=', self.date_from),
                ('checkout_date_id', '>=', self.date_from)])

            transfer_lisst_line_ids = []

            for line in transfer_line_ids:
                for lines in line.journal_entry_ids:
                    transfer_lisst_line_ids.append({
                        'create_date': lines.create_date,
                        'rooms_ref': line.rooms_ref1,
                        'customer': line.partner_id.name,
                        'Created by': lines.create_uid.name,
                        'lebels': lines.name,
                        'debit': lines.debit,
                        'credit': lines.credit,
                    })

            timesheet_line_ids = self.env['hr.attendance'].search([
                ('check_in', '>=', self.date_from), ('check_out', '<=', self.date_to)])
            timesheet_lisst_line_ids = []
            for line in timesheet_line_ids:
                if timesheet_line_ids:
                    timesheet_lisst_line_ids.append({
                        'Employee': line.employee_id.name,
                        'Check in': line.check_in,
                        'Check out': line.check_out,
                        'Work hours': line.worked_hours,
                    })

            housekeeping_line_ids = self.env['hotel.housekeeping'].search([
                ('create_date', '>=', self.date_from), ('create_date', '<=', self.date_to)])

            housekeeping_lisst_line_ids = []
            total_room_maintenance = 0
            total_room_checkin_dirty = 0
            total_room_checkout_dirty = 0
            for line in housekeeping_line_ids:
                housekeeping_lisst_line_ids.append({
                    'Room Number': line.room_no.name,
                    'Housekeeper': line.housekeeper.name,
                    'Inspector': line.inspector.name,
                    'Note': line.note,
                    'Clean Type': line.clean_type,
                    'Housekeeping Type': line.quality,

                })
                if line.quality == 'maintenance' and line.state == 'done':
                    total_room_maintenance += 1

                if line.quality == 'cleaning' and line.clean_type == 'checkin' and line.state == 'done':
                    total_room_checkin_dirty += 1

                if line.quality == 'cleaning' and line.clean_type == 'checkout' and line.state == 'done':
                    total_room_checkout_dirty += 1


            balance_line_ids = self.env['hotel.folio'].search([
                ('checkout_date_id', '>=', self.date_from),
                ('checkin_date_id', '<=', self.date_to)
                 ])

            balance_lisst_line_ids = []

            for line in balance_line_ids:
                for lines in line.room_lines:
                    balance_lisst_line_ids.append({
                        'Room Number': lines.product_id.name,
                        'customer': lines.folio_id.partner_id.name,
                        'price': lines.price_unit,
                        'night': lines.product_uom_qty,
                        'check in': lines.checkin_date,
                        'check out': lines.checkout_date,
                        'discounts': lines.discount_amount,
                        'remaining amount': line.remaining_amt})

            current_date = date.today()

            search_date_start = current_date.strftime('%Y-%m-%d 00:00:00')
            search_date_end = current_date.strftime('%Y-%m-%d 23:59:59')
            # ota_line_ids = self.env['available.rooms'].search([
            #     ('date', '>=', search_date_start), ('date', '<=', search_date_end)])
            #
            # ota_lisst_line_ids = []
            #
            # for line in ota_line_ids:
            #     ota_lisst_line_ids.append({
            #         'Room Type': line.name,
            #         'Quantity In OTA': line.quantity,
            #         'price In OTA': line.price, })

            service_line_ids = self.env['hotel_service.line'].search([
                ('create_date', '>=', self.date_from), ('create_date', '<=', self.date_to)])

            service_lisst_line_ids = []
            for line in service_line_ids:
                service_lisst_line_ids.append({
                    'Description': line.name,
                    'Product': line.product_id.name,
                    'price': line.price_unit,
                    'Total': line.price_total, })

            food_line_ids = self.env['hotel_food.line'].search([
                ('create_date', '>=', self.date_from), ('create_date', '<=', self.date_to)])

            food_lisst_line_ids = []
            for line in food_line_ids:
                food_lisst_line_ids.append({
                    'QTY': line.product_uom_qty,
                    'Product': line.product_id.name,
                    'price': line.price_unit,
                    'Total': line.price_total, })

            laundry_line_ids = self.env['hotel_folio_laundry.line'].search([
                ('create_date', '>=', self.date_from), ('create_date', '<=', self.date_to)])

            laundry_lisst_line_ids = []
            for line in laundry_line_ids:
                laundry_lisst_line_ids.append({
                    'QTY': line.product_uom_qty,
                    'Product': line.product_id.name,
                    'price': line.price_unit,
                    'Total': line.price_total, })

            ledger_lisst_line_ids = []
            ledger_line_ids = self.env['account.move.line'].search([
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('amount_residual', '!=', 0),
                ('account_id.reconcile', '=', True),
                ('partner_id.agent', '=', True),
            ])

            ledger_data = {}
            for line in ledger_line_ids:
                partner_id = line.partner_id.id
                if partner_id not in ledger_data:
                    ledger_data[partner_id] = {
                        'partner': line.partner_id.name,
                        'Debit': 0.0,
                        'Balance': 0.0,
                        'lines': [],
                    }
                ledger_data[partner_id]['Debit'] += line.debit
                ledger_data[partner_id]['Balance'] += line.balance
                ledger_data[partner_id]['lines'].append({
                    'Debit': line.debit,
                    'label': line.name,
                    'Balance': line.balance,
                })

            ledger_lisst_line_ids = list(ledger_data.values())

            # folio_line_ids = self.env['hotel_folio.line'].search([('create_date', '>=', self.date_from),
            #                                                       ('create_date', '<=', self.date_to)])
            #
            new_price = 0
            new_total = 0
            new_room = 0
            partner = ""
            # for folio_line in folio_line_ids:
            #     new_price = folio_line.price_unit
            #     new_total = folio_line.price_total
            #     new_room = folio_line.product_id.name
            #     partner = folio_line.partner_id.name

            move_lisst_line_ids = []

            move_lines = self.env['hotel.folio'].search([
                ('state', '!=', 'cancel'),
                ('moves_lines.create_date', '>=', self.date_from),
                ('moves_lines.create_date', '<=', self.date_to)
            ])
            unique_combinations = set()

            for line in move_lines:
                for move_line in line.moves_lines:
                    for room_line in line.room_lines:
                        if move_line.name != 'Checkout':  # Check if trans_type is not 'Checkout'
                            # Define a unique key based on the relevant fields
                            unique_key = (
                                move_line.folio_id, move_line.create_date, line.partner_id.name, move_line.product_id.name,
                                move_line.name, move_line.price_unit, line.rooms_ref1, room_line.price_unit)

                            if unique_key not in unique_combinations:
                                move_line_data = {
                                    'folio_id': move_line.folio_id,
                                    'create_date': move_line.create_date,
                                    'partner_name': line.partner_id.name,
                                    'oldest_room': move_line.product_id.name,
                                    'trans_type': move_line.name,
                                    'oldest_price': move_line.price_unit,
                                    'rooms_new': room_line.product_id.name,
                                    'new_rate': room_line.price_unit,
                                    'discounts': room_line.discount_amount,
                                }
                                move_lisst_line_ids.append(move_line_data)

                                unique_combinations.add(unique_key)

            print(move_lisst_line_ids)


            checkoutin_line_ids = self.env['hotel.room.booking.history'].search([])

            checkout_room_count = 0
            checkin_room_count = 0
            checkin_room_for_6am = 0

            for line in checkoutin_line_ids:
                if isinstance(line.check_out, datetime) and isinstance(self.date_from, datetime) and isinstance(
                        self.date_to, datetime):
                    if self.date_from <= line.check_out <= self.date_to and line.folio_state == 'sale':
                        checkout_room_count += 1
                if isinstance(line.check_in, datetime) and isinstance(self.date_from, datetime) and isinstance(
                        self.date_to, datetime):
                    if self.date_from <= line.check_in <= self.date_to and line.folio_state == 'draft':
                        checkin_room_count += 1
                if isinstance(line.check_in, datetime) and line.folio_state == 'draft':
                    checkin_room_for_6am += 1

            confirm_line_ids = self.env['hotel.reservation'].search([])

            confirm_room_count = 0
            confirm_room_count_fut = 0

            for line in confirm_line_ids:
                if isinstance(line.checking_date, datetime) and isinstance(self.date_from, datetime) and isinstance(
                        self.date_to, datetime):
                    if self.date_from <= line.checking_date <= self.date_to and line.state == 'confirm':
                        confirm_room_count += 1

                if isinstance(line.checking_date, datetime) and isinstance(self.date_from, datetime):
                    if self.date_from <= line.checking_date and line.state == 'confirm':
                        confirm_room_count_fut += 1

            data = {
                'model': self._name,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'cash_lisst_line_ids': cash_lisst_line_ids,
                'timesheet_lisst_line_ids': timesheet_lisst_line_ids,
                'housekeeping_lisst_line_ids': housekeeping_lisst_line_ids,
                'transfer_lisst_line_ids': transfer_lisst_line_ids,
                'balance_lisst_line_ids': balance_lisst_line_ids,
                # 'ota_lisst_line_ids': ota_lisst_line_ids,
                'service_lisst_line_ids': service_lisst_line_ids,
                'food_lisst_line_ids': food_lisst_line_ids,
                'laundry_lisst_line_ids': laundry_lisst_line_ids,
                'ledger_lisst_line_ids': ledger_lisst_line_ids,
                'move_lisst_line_ids': move_lisst_line_ids,
                'checkout_room_count': checkout_room_count,
                'checkin_room_count': checkin_room_count,
                'checkin_room_for_6am': checkin_room_for_6am,
                'confirm_room_count_fut': confirm_room_count_fut,
                'confirm_room_count': confirm_room_count,
                'total_room_maintenance': total_room_maintenance,
                'total_room_checkin_dirty': total_room_checkin_dirty,
                'total_room_checkout_dirty': total_room_checkout_dirty,
                'New price': new_price,
                'New total': new_total,
                'Guast Name': partner,
                'total_room': total_room,
                'days_in_current_month': self.days_in_current_month,


            }

            generated_report = self.env['ir.actions.report'].sudo().with_context()._render_qweb_pdf(
                "hotel_report.action_management_daily_report", data=data)[0]
            data_record = base64.b64encode(generated_report).decode()
            ir_values = {
                'name': 'Daily Management Report',
                'type': 'binary',
                'datas': data_record,
                'store_fname': data_record,
                'mimetype': 'application/pdf',
                'res_model': 'managment.report.wizard',
            }

            report_attachment = self.env['ir.attachment'].sudo().create(ir_values)
            self.env['mail.mail'].sudo().create({
                'model': self._name,
                'subject': 'Daily Management Report',
                'email_to': 'alatoomlana@gmail.com',
                'email_cc': 'lanaabedalmajeed@gmail.com',
                'email_from': 'lana@midaad.com',
                'attachment_ids': [(4, report_attachment.id)],
            }).send()

