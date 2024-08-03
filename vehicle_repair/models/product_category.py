from odoo import models, fields, api


class ProductCategoryInherit(models.Model):
    _inherit = 'product.category'

    sequence = fields.Char(string='Prefix', required=True, copy=False)
    next_seq = fields.Integer('Next Sequence', default=1)

    @api.model
    def create(self, vals):
        if not vals.get('sequence'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('product.category.sequence')
        return super(ProductCategoryInherit, self).create(vals)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Many2one('car.brands', string='Car Brand')
    model_id = fields.Many2one('car.models', string='Car Model')
    engine_cylinder_id = fields.Many2one('engine.size.cylinder', string='Car Engine Size Cylinder')
    engine_cylinder_size_id = fields.Many2one('engine.size.liter', string='Car Engine Size Liter')
    car_year_id = fields.Many2one('year.manufacture', string='Car Year')

class ProductTemplate(models.Model):
    _inherit = "product.product"

    default_code = fields.Char(compute="compute_default_code", store=True, readonly=True)

    @api.depends('categ_id')
    def compute_default_code(self):
        for product in self:
            if product.id:
                if product.categ_id:
                    product.default_code = "{}{}".format(product.categ_id.sequence, product.categ_id.next_seq)
                    product.categ_id.next_seq += 1
