# -*- coding: utf-8 -*-
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    lot_id = fields.Many2one(
        'stock.production.lot',
        string='Initial Serial Number',
        help="If the product is being tracked by unique serial number then this is the initial serial number",
        copy=False)
    tracking = fields.Selection(related='product_id.tracking')
    show_mass_produce = fields.Boolean()

    @api.onchange('lot_id', 'product_id', 'product_qty')
    def onchange_lot_id(self):
        lot_id = 'lot_id' in self._context and self._context.get(
            'lot_id') or self.lot_id
        if lot_id and self.product_qty > 1 and self.product_id.tracking == 'serial':
            lot_list = []
            serial_name = lot_id.name
            for count in range(int(self.product_qty)):
                if count == 0:
                    continue
                serial_name = self.env[
                    'mrp.product.produce.serial'].calculate_next_lot_number(serial_name)
                lot_list.append(serial_name)
            lots = self.env['stock.production.lot'].search(
                [('product_id', '=', self.product_id.id), ('name', 'in', lot_list)])
            if lots:
                return {
                    'warning': {
                        'title': "Please select another lot number",
                        'message': "The lot number (%s) already exists for this product" % (', '.join(
                            lots.mapped('name')))}}

    @api.onchange('bom_id')
    def onchange_bom_id(self):
        self.show_mass_produce = False
        if self.bom_id:
            if self.bom_id.product_tmpl_id.tracking == 'serial':
                if self.bom_id.bom_line_ids and len(
                        self.bom_id.bom_line_ids.filtered(
                            lambda line: line.product_id.tracking == 'none')) == len(
                        self.bom_id.bom_line_ids):
                    self.show_mass_produce = True

    @api.multi
    def open_produce_mass_product(self):
        self.ensure_one()
        action = self.env.ref(
            'mrp_automate_lot_number.act_mrp_product_produce').read()[0]
        return action
