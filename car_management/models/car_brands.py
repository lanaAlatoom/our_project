from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


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
    _description = 'Chevy Number'

    name = fields.Char(string='Chevy Number', required=True)
    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket', string='Helpdesk Ticket')
    car_brands_id = fields.Many2one('car.brands', string='Car Brand', store=True, readonly=False)
    car_model_ids = fields.Many2many('car.models', string='Car Models', store=True, readonly=False)

    @api.constrains('name')
    def _check_chevy_number(self):
        for record in self:
            if not record.name:
                raise ValidationError("Chevy Number cannot be empty.")
            if len(record.name) != 17:
                raise ValidationError("Chevy Number must be exactly 17 characters long.")
            if not all(char.isdigit() or 'A' <= char <= 'Z' for char in record.name):
                raise ValidationError("Chevy Number must be in uppercase English letters and digits.")
            if not (record.name.isdigit() or record.name.isalnum()):
                raise ValidationError("Chevy Number must be 17 continuous numbers or 17 uppercase characters.")

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    chevy_number_id = fields.Many2one('chevy.number', string='Chevy Number', domain="[('car_brands_id', '=', car_brands_id)]" ,required=True)
    car_brands_id = fields.Many2one('car.brands', string='Car Brand',required=True)
    car_model_ids = fields.Many2many('car.models', string='Car Models',required=True)

    odometer = fields.Float(string='Odometer',required=True)
    odometer_unit = fields.Selection([('KM', 'KM'), ('mile', 'Mile')], string='Odometer Unit',required=True, default='KM')
    year_manufacture = fields.Char(string='Year of Manufacture',required=True)
    engine_size_cylinder = fields.Char(string='Engine Size (Cylinder)',required=True)
    engine_size_liter = fields.Char(string='Engine Size (Liter)',required=True)

    # Fields for الفحوصات الأولية
    engine_oil = fields.Boolean(string='زيت محرك')
    power_oil = fields.Boolean(string='زيت البور')
    brake_oil = fields.Boolean(string='زيت البريك')
    air_filter = fields.Boolean(string='فلتر هواء')
    oil_filter = fields.Boolean(string='فلتر زيت')
    fuel_filter = fields.Boolean(string='فلتر بنزين')
    cooling_water = fields.Boolean(string='ماء الراديتر')
    wiper_water = fields.Boolean(string='ماء المساحات')
    water_filter = fields.Boolean(string='فلتر ماء')
    front_brakes = fields.Boolean(string='بريكات امامية')
    rear_brakes = fields.Boolean(string='بريكات خلفية')
    electrical_services = fields.Boolean(string='خدمات كهرباء')
    mechanical_services = fields.Boolean(string='خدمات ميكانيك')
    spark_plugs = fields.Boolean(string='شمعات الاحتراق')
    ignition_system = fields.Boolean(string='منظومة الاحتراق')
    car_model_one_ids = fields.Many2many('car.models', string='Car Models', required=True)
    car_model_ids = fields.Many2many('car.models' ,'car_model_ref', string='Car Models',)


    @api.onchange('car_brands_id')
    def _onchange_car_brands_id(self):
        if self.car_brands_id:
            car_models = self.car_brands_id.model_id
            self.car_model_one_ids = [(6, 0, car_models.ids)]
        else:
            self.car_model_one_ids = [(5, 0, 0)]


    @api.model
    def create(self, vals):
        ticket = super(HelpdeskTicket, self).create(vals)
        if ticket.chevy_number_id:
            ticket.chevy_number_id.write({
                'car_brands_id': ticket.car_brands_id.id,
                'car_model_ids': [(6, 0, ticket.car_model_ids.ids)]
            })
        return ticket

    def write(self, vals):
        res = super(HelpdeskTicket, self).write(vals)
        for ticket in self:
            if ticket.chevy_number_id:
                ticket.chevy_number_id.write({
                    'car_brands_id': ticket.car_brands_id.id,
                    'car_model_ids': [(6, 0, ticket.car_model_ids.ids)]
                })
        return res

    def action_create_sale_order(self):
        for ticket in self:
            if self.engine_oil == True :
                tag_name = 'زيت محرك'  # Replace this with your field value
                product = self.env['product.product'].search([('product_tag_ids.name', '=', tag_name)], limit=1)
                if not product:
                    raise UserError(f"No product found with the tag '{tag_name}'")

                # Create sale order
                sale_order = self.env['sale.order'].create({
                    'partner_id': ticket.partner_id.id,
                    'chevy_number': ticket.chevy_number_id.name,
                    'origin': ticket.name,
                })

                self.env['sale.order.line'].create({
                    'order_id': sale_order.id,
                    'product_id': product.id,
                    'product_uom_qty': 1,
                    'price_unit': product.list_price,
                })
                # return {
                #     'type': 'ir.actions.act_window',
                #     'name': 'Sale Order',
                #     'view_mode': 'form',
                #     'res_model': 'sale.order',
                #     'res_id': sale_order.id,
                # }








class SaleOrder(models.Model):
    _inherit = 'sale.order'

    chevy_number = fields.Char(string="Chevy Number")



