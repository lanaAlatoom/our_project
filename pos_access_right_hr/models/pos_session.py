from odoo import models


class PosSession(models.Model):

    _inherit = 'pos.session'

    def _loader_params_hr_employee(self):

        result = super()._loader_params_hr_employee()
        result['search_params']['fields'].extend(
            ['disable_payment', 'disable_customer', 'disable_plus_minus',
             'disable_numpad', 'disable_qty', 'disable_discount',
             'disable_price', 'disable_remove_button'])
        return result
