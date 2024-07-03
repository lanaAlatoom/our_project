from odoo import models, fields, api

class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    name_seq = fields.Char(string='Prefix')

    @api.model
    def create(self, vals):
        if not vals.get('name_seq'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('product.template.name_seq')
        return super(ProductTemplateInherit, self).create(vals)


class ProductProductInherit(models.Model):
    _inherit = "product.product"

    default_code = fields.Char(compute="compute_default_code", store=True, readonly=True)

    @api.depends('product_tmpl_id', 'product_tmpl_id.name_seq', 'product_template_attribute_value_ids')
    def compute_default_code(self):
        for product in self:
            dimension_value = self._get_dimension_value(product)
            product.default_code = "{}{}".format(product.product_tmpl_id.name_seq or '', dimension_value)

    def _get_dimension_value(self, product):
        dimension_value = ''
        for value in product.product_template_attribute_value_ids:
            if value.attribute_id.name == 'Dimensions (cm)':
                dimension_value = value.name
                break
        return dimension_value
