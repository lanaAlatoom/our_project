import base64
from importlib.resources import _
from odoo import api, models, fields
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    van_number =fields.Many2many('stock.lot')



class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    attachment_image = fields.Image(string='Attachment')
    customer_bank = fields.Char(string='Customer Bank')
    date_commitments = fields.Date('Date Commitments')
    partner_waiver = fields.Char('Waiver')
    name = fields.Char("Journal", related="journal_id.name")
    van_number = fields.Many2many('stock.lot', string='Van Number')

    @api.model
    def default_get(self, fields_list):
        res = super(AccountPaymentRegister, self).default_get(fields_list)
        if self._context.get('active_model') == 'account.move':
            active_id = self._context.get('active_id')
            if active_id:
                account_move = self.env['account.move'].browse(active_id)
                res['van_number'] = [(6, 0, account_move.van_number.ids)]
        return res

    @api.onchange('van_number')
    def _onchange_van_number(self):
        if self._context.get('active_model') == 'account.move':
            active_id = self._context.get('active_id')
            if active_id:
                account_move = self.env['account.move'].browse(active_id)
                return {'domain': {'van_number': [('id', 'in', account_move.van_number.ids)]}}

    def action_create_paymentsss(self):
        move_vals = {
            'date_of_bank_commitments': fields.Date.today(),
            'name_of_customer': self.partner_id.id,
            'journal_id': self.journal_id.id,
            'customer_bank': self.customer_bank,
            'date_commitments': self.date_commitments,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'van_number': self.van_number,
            'partner_waiver': self.partner_waiver,
            'state': 'deposit',
        }

        move = self.env['bank.commitments'].create(move_vals)
        if self.attachment_image:
            attachment = {
                'name': 'Attachment',
                'mimetype': 'image/png',
                'datas': self.attachment_image,
                'res_model': 'bank.commitments',
                'res_id': move.id,
            }
            self.env['ir.attachment'].create(attachment)

            move.message_post(body="Attachment added")

        self.action_create_payments()


class BankCommitments(models.Model):
    _name = 'bank.commitments'
    _description = 'Bank Commitments'
    _inherit = ['mail.thread']

    date_of_bank_commitments = fields.Date(string='Date of Bank Commitments')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments', help="Attachments related to this record")

    journal_id = fields.Many2one(
        'account.journal', "Journal", domain="[('type','=',('cash','bank'))]")
    name = fields.Char(
        "Journal", related="journal_id.name" )
    name_of_customer = fields.Many2one('res.partner', string='Name of Customer')
    customer_bank = fields.Char( string='Customer Bank')
    deposit_bank_id = fields.Many2one('account.journal', string='Deposit Bank' , domain="[('type','=',('cash','bank'))]")
    attachment_image = fields.Image(string='Attachment')
    amount =fields.Monetary('Amount')
    currency_id = fields.Many2one('res.currency',)
    date_commitments =fields.Date('Date Commitments')
    state = fields.Selection([
        ('deposit', 'Deposit'),
        ('received', 'Received'),], 'Status', default='deposit')

    van_number = fields.Many2many('stock.lot')
    partner_waiver = fields.Char('waiver')
    account_move_id = fields.Many2one('account.move', string='Account Move', readonly=True, copy=False)



    def action_received(self):
        move_date = fields.Date.today()
        move_ref = f"Van Number: {', '.join(van.name for van in self.van_number)}"
        journal = self.env['account.journal'].search([('code', '=', 'TB')], limit=1)

        if not journal:
            raise UserError("Bank journal not found.")

        move = self.env['account.move'].create({
                'ref': move_ref,
                'partner_id': self.name_of_customer.id,
                'date': move_date,
                'journal_id': journal.id,
            })

        move_lines = []
        print(move_lines)
        for bank_commitment in self:
            income_account_line = {
                'name': f"Waiver: {bank_commitment.partner_waiver}",
                'account_id': bank_commitment.deposit_bank_id.outbound_payment_method_line_ids.payment_account_id.id,
                'partner_id': bank_commitment.name_of_customer.id,
                'debit': bank_commitment.amount,
                'credit': 0.0,
                'move_id': move.id,
            }
            move_lines.append(income_account_line)
            print(move_lines)

            credit_account_line = {
                'name': f"Waiver: {bank_commitment.partner_waiver}",
                'account_id': bank_commitment.journal_id.outbound_payment_method_line_ids.payment_account_id.id,
                'partner_id': bank_commitment.name_of_customer.id,
                'debit': 0.0,
                'credit': bank_commitment.amount,
                'move_id': move.id,
            }
            move_lines.append(credit_account_line)

            self.env['account.move.line'].create(move_lines)
            move.action_post()
            self.write({'state': 'received', 'account_move_id': move.id})  # Update here

