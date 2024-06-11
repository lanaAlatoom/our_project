from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, format_amount, format_date, formatLang, get_lang, groupby
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError, ValidationError



class ProductInherit(models.Model):
    _inherit = 'product.product'

    last_purchase_cost = fields.Float(string='Last Purchase Cost', compute='_compute_last_purchase_cost')

    def _compute_last_purchase_cost(self):
        for product in self:
            last_purchase_line = self.env['purchase.order.line'].search([
                ('product_id.name', '=', product.name),
                ('order_id.state', '=', 'purchase'),
            ], order='id desc', limit=1)

            if last_purchase_line:
                product.last_purchase_cost = last_purchase_line.price_unit
            else:
                product.last_purchase_cost = product.standard_price


class MrpBomInherit(models.Model):
    _inherit = "mrp.bom"

    type = fields.Selection(tracking=True, )
    code = fields.Char(tracking=True, )
    product_id = fields.Many2one(tracking=True, )
    product_qty = fields.Float(tracking=True, )
    product_tmpl_id = fields.Many2one('product.template', tracking=True, )
    bom_line_ids = fields.One2many('mrp.bom.line', 'bom_id', 'BoM Lines', tracking=True, )


class MrpBomLineInherit(models.Model):
    _inherit = "mrp.bom.line"

    product_qty = fields.Float(tracking=True, )
    product_id = fields.Many2one('product.product', tracking=True, )


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    subtotal_one = fields.Float(string='Subtotal One')

    price_unit_last = fields.Float(string='Last Unit Price', digits='Product Price', readonly=True)
    last_purchase_uom = fields.Many2one('uom.uom', string='Last Purchase UoM', readonly=True,default=lambda self: self.env['uom.uom'].browse(61) )
     

    @api.depends('product_qty', 'product_uom', 'company_id')
    def _compute_price_unit_and_date_planned_and_name(self):
        for line in self:
            if not line.product_id or line.invoice_lines or not line.company_id:
                continue
            line = line.with_company(line.company_id)
            params = {'order_id': line.order_id}
            seller = line.product_id._select_seller(
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order and line.order_id.date_order.date() or fields.Date.context_today(line),
                uom_id=line.product_uom,
                params=params)

            if seller or not line.date_planned:
                line.date_planned = line._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

            # If not seller, use the standard price. It needs a proper currency conversion.
            if not seller:
                unavailable_seller = line.product_id.seller_ids.filtered(
                    lambda s: s.partner_id == line.order_id.partner_id)
                if not unavailable_seller and line.price_unit and line.product_uom == line._origin.product_uom:
                    # Avoid to modify the price unit if there is no price list for this partner and
                    # the line has already one to avoid to override unit price set manually.
                    continue
                po_line_uom = line.product_uom or line.product_id.uom_po_id
                price_unit = line.env['account.tax']._fix_tax_included_price_company(
                    line.product_id.uom_id._compute_price(line.product_id.standard_price, po_line_uom),
                    line.product_id.supplier_taxes_id,
                    line.taxes_id,
                    line.company_id,
                )
                price_unit = line.product_id.cost_currency_id._convert(
                    price_unit,
                    line.currency_id,
                    line.company_id,
                    line.date_order or fields.Date.context_today(line),
                    False
                )
                line.price_unit = float_round(price_unit, precision_digits=max(line.currency_id.decimal_places,
                                                                               self.env[
                                                                                   'decimal.precision'].precision_get(
                                                                                   'Product Price')))
                continue

            # Fetch the last purchase price
            last_purchase = self.env['purchase.order.line'].search([
                ('product_id', '=', line.product_id.id),
                ('partner_id', '=', line.partner_id.id),
                ('state', 'in', ['purchase', 'done'])
            ], order='id desc', limit=1)

            if last_purchase:
                price_unit = last_purchase.price_unit
                product_uom = last_purchase.product_uom

            else:
                price_unit = seller.price if seller else 0.0
                product_uom = line.product_id.uom_po_id or line.product_id.uom_id

            price_unit = line.env['account.tax']._fix_tax_included_price_company(price_unit,
                                                                                 line.product_id.supplier_taxes_id,
                                                                                 line.taxes_id,
                                                                                 line.company_id) if seller else 0.0
            # price_unit = seller.currency_id._convert(price_unit, line.currency_id, line.company_id,
            #                                          line.date_order or fields.Date.context_today(line), False)
            # price_unit = float_round(price_unit, precision_digits=max(line.currency_id.decimal_places,
            #                                                           self.env['decimal.precision'].precision_get(
            #                                                               'Product Price')))
            line.price_unit = price_unit
            line.product_uom = product_uom

            # record product names to avoid resetting custom descriptions
            default_names = []
            vendors = line.product_id._prepare_sellers({})
            for vendor in vendors:
                product_ctx = {'seller_id': vendor.id, 'lang': get_lang(line.env, line.partner_id.lang).code}
                default_names.append(line._get_product_purchase_description(line.product_id.with_context(product_ctx)))
            if not line.name or line.name in default_names:
                product_ctx = {'seller_id': seller.id, 'lang': get_lang(line.env, line.partner_id.lang).code}
                line.name = line._get_product_purchase_description(line.product_id.with_context(product_ctx))

class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    last_purchase_price = fields.Float(string='Last Purchase Price', compute='_compute_last_purchase_info',
                                       readonly=True)
    last_purchase_uom = fields.Many2one('uom.uom', string='Last Purchase UoM', compute='_compute_last_purchase_info',
                                        readonly=True)

    @api.depends('product_tmpl_id')
    def _compute_last_purchase_info(self):
        for record in self:
            last_purchase_order_line = self.env['purchase.order.line'].search([
                ('product_id', '=', record.product_tmpl_id.product_variant_ids.id),
                ('partner_id', '=', record.partner_id.id),

                ('state', 'in', ['purchase', 'done']),
            ], order='id desc', limit=1)

            if last_purchase_order_line:
                record.last_purchase_price=0.0
                record.last_purchase_uom = last_purchase_order_line.product_id.product_tmpl_id.uom_po_id.id
                record.last_purchase_price = last_purchase_order_line.price_unit
                record.last_purchase_uom = last_purchase_order_line.product_uom.id
            else:
                record.last_purchase_price = 0.0
                record.last_purchase_uom = last_purchase_order_line.product_id.product_tmpl_id.uom_po_id.id


# class SupplierInfo(models.Model):
#     _inherit = "product.supplierinfo"

#     last_purchase_price = fields.Float(string='Last Purchase Price', readonly=True)
#     last_purchase_uom = fields.Many2one('uom.uom', string='Last Purchase UoM', readonly=True)
#     product_uom = fields.Many2one(
#         'uom.uom', 'Unit of Measure')

# class PurchaseOrderLine(models.Model):
#     _inherit = "purchase.order.line"

#     @api.model
#     def create(self, vals):
#         res = super(PurchaseOrderLine, self).create(vals)
#         res._update_supplier_info()
#         return res

#     def write(self, vals):
#         res = super(PurchaseOrderLine, self).write(vals)
#         self._update_supplier_info()
#         return res

#     def _update_supplier_info(self):
#         for line in self:
#             supplier_info = self.env['product.supplierinfo'].search([
#                 ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
#                 ('partner_id', '=', line.order_id.partner_id.id)
#             ], limit=1)
#             if supplier_info:
#                 supplier_info.write({
#                     'last_purchase_price': line.price_unit,
#                     'price': line.price_unit,
#                     'last_purchase_uom': line.product_uom.id,
#                     'product_uom': line.product_uom.id,
#                 })
