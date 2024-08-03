from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import logging
import re

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    product_id = fields.Many2one('product.product', string='Product')
    is_orderd = fields.Boolean(string='Ordered')


class YearManufacture(models.Model):
    _name = 'year.manufacture'
    _description = 'Year of Manufacture'

    name = fields.Char(string='Year', required=True)


class EngineSizeCylinder(models.Model):
    _name = 'engine.size.cylinder'
    _description = 'Engine Size (Cylinder)'

    name = fields.Char(string='Engine Size (Cylinder)', required=True)


class EngineSizeLiter(models.Model):
    _name = 'engine.size.liter'
    _description = 'Engine Size (Liter)'

    name = fields.Char(string='Engine Size (Liter)', required=True)


class CarModels(models.Model):
    _name = 'car.models'
    _description = 'Car Models'
    _rec_name = 'model_name'

    model_name = fields.Char(string='Model Name', required=True)


class CarBrands(models.Model):
    _name = 'car.brands'
    _description = 'Car Brands'

    name = fields.Char(string='Brand Name', required=True)
    model_id = fields.Many2many('car.models', string='Models')


class ChevyNumber(models.Model):
    _name = 'chevy.number'
    _description = 'Chassis Number'

    partner_id = fields.Many2one('res.partner', string='Customer Name')
    name = fields.Char(string='Chassis Number', required=True)
    helpdesk_ticket_id = fields.Many2one('technician.car', string='Technician car')
    car_brands_id = fields.Many2one('car.brands', string='Car Brand', store=True, readonly=True)
    car_model_ids = fields.Many2many('car.models', string='Car Models', store=True, readonly=False)
    year_manufacture_id = fields.Many2one('year.manufacture', string='Year of Manufacture', store=True)
    engine_size_cylinder_id = fields.Many2one('engine.size.cylinder', string='Engine Size (Cylinder)', store=True, )
    engine_size_liter_id = fields.Many2one('engine.size.liter', string='Engine Size (Liter)', store=True, )
    _sql_constraints = [
        ('name_refs_unique', 'unique(name)', 'The chassis number must be unique!')
    ]

    @api.model
    def create(self, vals):
        if 'name' in vals:
            vals['name'] = vals['name'].upper()
        return super(ChevyNumber, self).create(vals)

    def write(self, vals):
        if 'name' in vals:
            vals['name'] = vals['name'].upper()
        return super(ChevyNumber, self).write(vals)

    @api.constrains('name')
    def _check_chevy_number(self):
        arabic_letters_pattern = re.compile(r'[\u0600-\u06FF]')
        for record in self:
            if len(record.name) != 17:
                raise ValidationError("Chassis Number must be exactly 17 characters long.")
            if not (record.name.isdigit() or record.name.isalnum()):
                raise ValidationError("Chassis Number must be 17 continuous numbers or 17 uppercase characters.")
            if arabic_letters_pattern.search(record.name):
                raise ValidationError("Chassis Number must not contain Arabic letters.")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    chevy_number_id = fields.Many2one('chevy.number', string='Chevy Number')
    chevy_number = fields.Char(string="Chassis Number", readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=False)
    partner_invoice_id = fields.Many2one('res.partner', required=False)
    partner_shipping_id = fields.Many2one('res.partner', required=False)
    helpdesk_order_ids = fields.One2many('sale.order.from.helpdesk', 'sale_order_id', string='Technician Orders')

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()

        for order in self:
            helpdesk_entries = self.env['sale.order.from.helpdesk'].search([('sale_order_id', '=', order.id)])
            sale_order_lines = self.env['sale.order.line'].search([('order_id', '=', order.id)])

            # Create opportunities for products from helpdesk entries
            for entry in helpdesk_entries:
                opportunity_vals = {
                    'name': f'Opportunity: {entry.product_id.name}',
                    'partner_id': order.partner_id.id,
                    'product_id': entry.product_id.id,
                }
                self.env['crm.lead'].create(opportunity_vals)

            # Create opportunities for products from sale order lines
            for line in sale_order_lines:
                opportunity_vals = {
                    'name': f'Opportunity: {line.product_id.name}',
                    'partner_id': order.partner_id.id,
                    'product_id': line.product_id.id,
                    'is_orderd': True

                }
                self.env['crm.lead'].create(opportunity_vals)

        return res


class SaleOrderFromTechnician(models.Model):
    _name = 'sale.order.from.helpdesk'
    _description = 'Sale Order from Technician'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity', default=1)
    price_unit = fields.Float(string='Price', default=0.0)
    order_line = fields.One2many(
        comodel_name='sale.order.line',
        inverse_name='order_id',
        string="Order Lines", )

    def button_add_product(self):
        self.ensure_one()
        if not self.product_id:
            raise UserError("Please select a product.")

        sale_order_line_vals = {
            'order_id': self.sale_order_id.id,
            'product_id': self.product_id.id,
            'product_uom_qty': self.quantity,
            'price_unit': self.price_unit,
        }

        self.env['sale.order.line'].create(sale_order_line_vals)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        helpdesk_order = self.env['sale.order.from.helpdesk'].search(
            [('product_id', '=', vals.get('product_id')), ('sale_order_id', '=', vals.get('order_id'))], limit=1)
        if helpdesk_order:
            helpdesk_order.unlink()
        return res


class TechnicianMember(models.Model):
    _name = 'technician.member'
    _description = 'Technician Member'

    name = fields.Char(string='Member Name', required=True)
    email = fields.Char(string='Email', required=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    ticket_count = fields.Integer(string='Tickets Count', compute='_compute_ticket_count')
    show_timesheet_button = fields.Boolean(string='Show Timesheet Button')

    @api.depends('user_id')
    def _compute_ticket_count(self):
        for member in self:
            member.ticket_count = self.env['technician.car'].search_count([('member_id', '=', member.id)])

    def action_view_ticket_car_user(self):
        self.ensure_one()
        action = self.env.ref("vehicle_repair.action_car_technician").read()[0]
        action['display_name'] = self.name
        action['domain'] = [('member_id', '=', self.id)]
        return action


class ProductTag(models.Model):
    _inherit = 'product.tag'
    _order = "sequence"

    sequence = fields.Integer('Sequence')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    chassis_number_ids = fields.Many2many('chevy.number', )

    chevy_number_ids = fields.One2many('chevy.number', 'partner_id', string='Chevy Numbers',
                                       compute='_compute_chevy_number_ids')
    # property_product_pricelist = fields.Many2one('product.pricelist', store=True)

    price_list_id = fields.Many2one('product.pricelist', string="Price List", compute='_compute_price_list', store=True)


    @api.depends('property_product_pricelist')
    def _compute_price_list(self):
        for partner in self:
            partner.price_list_id = partner.property_product_pricelist
    
    
    @api.depends('sale_order_ids.chevy_number_id')
    def _compute_chevy_number_ids(self):
        for partner in self:
            sale_orders = self.env['sale.order'].search([('partner_id', '=', partner.id)])
            chevy_numbers = sale_orders.mapped('chevy_number_id')
            partner.chevy_number_ids = [(6, 0, chevy_numbers.ids)]
    
    
    @api.constrains('name')
    def _check_name_sections(self):
        for record in self:
            if record.name:
                name_sections = record.name.split()
                if len(name_sections) != 3:
                    raise ValidationError("The name must consist of exactly three sections.")
