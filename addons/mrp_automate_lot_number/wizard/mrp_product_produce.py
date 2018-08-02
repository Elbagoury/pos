# -*- coding: utf-8 -*-
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class MrpProductProduce(models.TransientModel):
    _name = "mrp.product.produce.serial"
    _inherit = 'mrp.product.produce'
    
    segment_count = fields.Char('Segment Start From')

    @api.multi
    def _get_product_qty(self):
        production = self.env['mrp.production'].browse(
            self._context['active_id'])
        main_product_moves = production.move_finished_ids.filtered(
            lambda x: x.product_id.id == production.product_id.id)
        return production.product_qty - \
            sum(main_product_moves.mapped('quantity_done'))

    @api.model
    def default_get(self, fields):
        res = super(MrpProductProduce, self).default_get(fields)
        res['product_qty'] = self._get_product_qty()
        stock_production_lot = self.env['stock.production.lot']
        last_lot_id = stock_production_lot.search([('product_id','=',res['product_id'])],order='id desc', limit=1)
        res['segment_count'] = int(last_lot_id.name)+1
        return res

    @api.multi
    def calculate_next_lot_number(self, name):
        head = name.rstrip('0123456789')
        tail = name[len(head):]
        if not tail:
            tail = '0'
        tail_len = "{0:0>%d}" % (len(tail))
        l_tail = tail_len.format(int(tail) + 1)
        return head + l_tail

    @api.multi
    def do_produce(self):
        self.ensure_one()
        lot_id = self.lot_id
        remaining_qty = self._get_product_qty()
        if self.product_qty > remaining_qty:
            raise UserError(_('Please enter valid quantity to produce!!!'))

        context = dict(self.env.context or {})
        context['lot_id'] = self.lot_id
        if self._context.get('active_id'):
            lot_onchange = self.env['mrp.production'].with_context(
                context).browse(self._context.get('active_id')).onchange_lot_id()
            if lot_onchange:
                warning = lot_onchange['warning']['message']
                raise UserError(_("Warning: %s") % (warning))

        lot_unique = self.env['stock.move.lots'].search(
            [('product_id', '=', self.product_id.id), ('lot_id', '=', self.lot_id.id)])
        if lot_unique:
            raise UserError(
                _("The lot number (%s) already exists for this product") % str(
                    lot_unique.lot_id.name))
        for count in range(int(self.product_qty)):
            if count:
                name = self.calculate_next_lot_number(lot_id.name)
                val = {'product_id': self.product_id.id, 'name': name}
                lot_id = self.env['stock.production.lot'].create(val)
            mrp_produce = self.env['mrp.product.produce'].create(
                {'product_qty': 1.0, 'lot_id': lot_id.id})
            mrp_produce.do_produce()
        return {'type': 'ir.actions.act_window_close'}
