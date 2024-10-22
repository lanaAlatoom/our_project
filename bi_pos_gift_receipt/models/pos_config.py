# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class PosConfig(models.Model):
	_inherit = 'pos.config'

	enable_gift_receipt = fields.Boolean(string="Enable Gift Receipt")


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	pos_enable_gift_receipt = fields.Boolean(related="pos_config_id.enable_gift_receipt", readonly=False)