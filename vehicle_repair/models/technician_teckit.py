from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import re



class TechnicianTicket(models.Model):
    _name = 'technician.car'

    product_tag_lines = fields.One2many('technician.tag', 'ticket_id', string="Product Tag Lines")
    name = fields.Char(string="Product Tag Name")
    partner_id =fields.Many2one('res.partner' )

    timesheet_ids = fields.One2many('account.analytic.line', 'ticket_id', string="Timesheets")
    is_timesheet_visible = fields.Boolean(string='Show Timesheet Button', related='member_id.show_timesheet_button')
    is_start = fields.Boolean(string="Is Starting", default=False)
    is_ending = fields.Boolean(string="Is Ending", default=True)

    note =fields.Text(string='Note')
    state = fields.Selection([
        ('in_examination', 'Examination'),
        ('served', 'Served'),
        ('not_served', 'Not Served')
    ], string='State', default='in_examination')

    is_so = fields.Boolean(string='Is confirm to Sale order')
    member_id = fields.Many2one('technician.member', string='Member')
    name = fields.Char(related="member_id.name", string='Member')
    chevy_number_id = fields.Many2one('chevy.number', string='Chassis Number', required=True)
    _sql_constraints = [
        ('name_ref_uniq', 'unique(name)', 'The chassis number must be unique!')
    ]

    @api.onchange('chevy_number_id')
    def _onchange_chevy_number_id(self):
        if self.chevy_number_id:
            self.chevy_number_id.name = self.chevy_number_id.name.upper()

    @api.constrains('chevy_number_id')
    def _check_chevy_number(self):
        arabic_letters_pattern = re.compile(r'[\u0600-\u06FF]')
        for record in self:
            if len(record.chevy_number_id.name) != 17:
                raise ValidationError("Chassis Number must be exactly 17 characters long.")

            if not (record.chevy_number_id.name.isdigit() or record.chevy_number_id.name.isalnum()):
                raise ValidationError("Chassis Number must be 17 continuous numbers or 17 uppercase characters.")

            if arabic_letters_pattern.search(record.chevy_number_id.name):
                raise ValidationError("Chassis Number must not contain Arabic letters.")


    car_brands_id = fields.Many2one('car.brands', string='Car Brand', required=True)
    car_model_ids = fields.Many2many('car.models', string='Car Models', required=True)

    odometer = fields.Float(string='Odometer', required=True)
    odometer_unit = fields.Selection([('KM', 'KM'), ('mile', 'Mile')], string='Odometer Unit', required=True,
                                     default='KM')

    year_manufacture_id = fields.Many2one('year.manufacture', string='Year of Manufacture', store=True, )
    engine_size_cylinder_id = fields.Many2one('engine.size.cylinder', string='Engine Size (Cylinder)', store=True,)
    engine_size_liter_id = fields.Many2one('engine.size.liter', string='Engine Size (Liter)', store=True, )
    car_model_one_ids = fields.Many2many('car.models', string='Car Models', required=True)
    car_model_ids = fields.Many2many('car.models', 'car_model_ref', string='Car Models', )
    product_tag_lines = fields.One2many('technician.tag', 'ticket_id', string="Product Tag Lines")
    timesheet_ids = fields.One2many('account.analytic.line', 'ticket_id', string="Timesheets")
    is_timesheet_visible = fields.Boolean(string='Show Timesheet Button', related='member_id.show_timesheet_button')

    def action_start_timesheet(self):
        self.is_start = True
        self.is_ending = False
        self.ensure_one()
        project = self.env['project.project'].create({
            'name': self.name,
        })

        # Create the task
        task = self.env['project.task'].create({
            'name': self.id,
            'project_id': project.id,
        })

        if not project or not task:
            raise UserError('Project or Task not found.')

        self.env['account.analytic.line'].create({
            'name': f'Starting timesheet for {self.name}',
            'date': fields.Date.today(),
            'unit_amount': 0.0,
            'user_id': self.env.user.id,
            'ticket_id': self.id,
            'project_id': project.id,
            'task_id': task.id,
        })

    def action_end_timesheet(self):
        self.ensure_one()
        self.is_start = False
        self.is_ending = True
        timesheet = self.env['account.analytic.line'].search([('ticket_id', '=', self.id)], order='create_date desc',
                                                             limit=1)
        if timesheet:
            timesheet.write({
                'name': f'Ending timesheet for {self.name}',
                'date': fields.Date.today(),
                'unit_amount': (fields.Datetime.now() - timesheet.create_date).total_seconds() / 3600.0,
                'user_id': self.env.user.id,
            })



    @api.onchange('car_brands_id')
    def _onchange_car_brands_id(self):
        if self.car_brands_id:
            car_models = self.car_brands_id.model_id
            self.car_model_one_ids = [(6, 0, car_models.ids)]
        else:
            self.car_model_one_ids = [(5, 0, 0)]

    @api.model
    def create(self, vals):
        ticket = super(TechnicianTicket, self).create(vals)
        if ticket.chevy_number_id:
            ticket.chevy_number_id.write({
                'car_brands_id': ticket.car_brands_id.id,
                'car_model_ids': [(6, 0, ticket.car_model_ids.ids)],
                'year_manufacture_id': ticket.year_manufacture_id.id,
                'engine_size_cylinder_id': ticket.engine_size_cylinder_id.id,
                'engine_size_liter_id': ticket.engine_size_liter_id.id,
            })

        products = []
        for tag_line in ticket.product_tag_lines:
            if tag_line.priority in ('normal', 'high'):
                for product_tag in tag_line.product_tags_ids:
                    product = self.env['product.product'].search([('product_tag_ids', '=', product_tag.id)], limit=1)
                    if product:
                        products.append(product)

        if products:
            ticket.is_so = True
            last_sale_order = self.env['sale.order'].search([('chevy_number_id', '=', ticket.chevy_number_id.id)],
                                                            order='id desc', limit=1)
            partner_id = last_sale_order.partner_id.id if last_sale_order else ticket.partner_id.id

            sale_order = self.env['sale.order'].create({
                'partner_id': partner_id,
                'chevy_number_id': ticket.chevy_number_id.id,
                'origin': ticket.name,
            })

            for product in products:
                self.env['sale.order.from.helpdesk'].create({
                    'sale_order_id': sale_order.id,
                    'product_id': product.id,
                    'price_unit': product.list_price,
                })

        return ticket

    def write(self, vals):
        res = super(TechnicianTicket, self).write(vals)
        for ticket in self:
            if ticket.chevy_number_id:
                ticket.chevy_number_id.write({
                    'car_brands_id': ticket.car_brands_id.id,
                    'car_model_ids': [(6, 0, ticket.car_model_ids.ids)],
                    'year_manufacture_id': ticket.year_manufacture_id.id,
                    'engine_size_cylinder_id': ticket.engine_size_cylinder_id.id,
                    'engine_size_liter_id': ticket.engine_size_liter_id.id,
                })
        return res

    @api.onchange('chevy_number_id')
    def _onchange_chevy_number_id(self):
        if self.chevy_number_id:
            chevy = self.chevy_number_id
            self.car_brands_id = chevy.car_brands_id.id
            self.car_model_ids = [(6, 0, chevy.car_model_ids.ids)]
            self.year_manufacture_id = chevy.year_manufacture_id.id
            self.engine_size_cylinder_id = chevy.engine_size_cylinder_id.id
            self.engine_size_liter_id = chevy.engine_size_liter_id.id



    # @api.model
    # def default_get(self, fields):
    #     res = super(TechnicianTicket, self).default_get(fields)
    #     product_tags = self.env['product.tag'].search([])
    #     technician_tags = []
    #     for product_tag in product_tags:
    #         technician_tags.append((0, 0, {
    #             'product_tags_ids': [(6, 0, [product_tag.id])],
    #             'name': product_tag.name,
    #             'boolean_field': False,  # Adjust this as needed
    #         }))
    #     res.update({
    #         'product_tag_lines': technician_tags
    #     })
    #     return res


#########################new work 31/7/2024 ####################

#########################new work 1/8/2024 ####################
##product service 
    @api.model
    def default_get(self, fields):
        res = super(TechnicianTicket, self).default_get(fields)
        product_tags = self.env['product.template'].search([('category_two_id.is_service', '=', True)])
        technician_tags = []
        for product_tag in product_tags:
            technician_tags.append((0, 0, {
                'product_tags_ids': product_tag.id,
                'name': product_tag.category_two_id.name,
            }))
        res.update({
            'product_tag_lines': technician_tags
        })
        return res

#########################new work 25/5

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_technician_problem = fields.Boolean(string="Is Technician Problem")



class TechnicianTag(models.Model):
    _name = 'technician.tag'
    _description = 'Technician Tag'

    ticket_id = fields.Many2one('technician.car', string="Ticket", ondelete='cascade')
    product_tags_ids = fields.Many2one('product.tag', string="Product Tags")
    boolean_field = fields.Boolean(string="problem?")
    name = fields.Char(string="examination" )
    note = fields.Text(string='Note')

    priority = fields.Selection([
        ('_', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
    ], string='problem?')





class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    ticket_id = fields.Many2one('technician.car', string="Technician Ticket")














