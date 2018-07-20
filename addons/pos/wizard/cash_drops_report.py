import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

from datetime import datetime, date, time, timedelta
import time

class cash_drop_report(models.TransientModel):
	_name = "cash.drop.report"

	date = fields.Date('Date')
	day_shift = fields.Selection([('day','Day'),('shift','Shift')],'Day/Shift')
	shift_id = fields.Many2one('shift.master','Shift')
	cash_drop_ids = fields.One2many('cash.drop.line','cash_drop_id','Cash Drops')
	overall_total = fields.Float('Total')
	
	@api.onchange('date','day_shift','shift_id')
	def onchange_date(self):
		order_dict = []
		overall_total = 0
		if self.date and self.day_shift == 'day':
			pos_order_ids = self.env['pos.order'].search([('date_order','>=',self.date),('date_order','<=',self.date)])
			
			for order in pos_order_ids:
				total = 0
				for line in order.lines:
					fpos = line.order_id.fiscal_position_id
					tax_ids_after_fiscal_position = fpos.map_tax(line.tax_ids, line.product_id, line.order_id.partner_id) if fpos else line.tax_ids
					price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
					taxes = tax_ids_after_fiscal_position.compute_all(price, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id, partner=line.order_id.partner_id)
					total += taxes['total_included']
				overall_total += total
				order_dict.append((0, 0, {'time': order.date_order, 'value': total,'receipt_number':order.pos_reference}))
		elif self.date and self.day_shift == 'shift':
			pos_session_ids = self.env['pos.session'].search([('shift_id','=',self.shift_id.id)])
			pos_session_list = []
			for pos_session in pos_session_ids:
				pos_session_list.append(pos_session.id)
			pos_order_ids = self.env['pos.order'].search([('date_order','>=',self.date),('date_order','<=',self.date),('session_id','in',pos_session_list)])
			for order in pos_order_ids:
				total = 0
				for line in order.lines:
					fpos = line.order_id.fiscal_position_id
					tax_ids_after_fiscal_position = fpos.map_tax(line.tax_ids, line.product_id, line.order_id.partner_id) if fpos else line.tax_ids
					price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
					taxes = tax_ids_after_fiscal_position.compute_all(price, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id, partner=line.order_id.partner_id)
					total += taxes['total_included']
				overall_total += total
				order_dict.append((0, 0, {'time': order.date_order, 'value': total,'receipt_number':order.pos_reference}))
		self.overall_total = overall_total
		self.cash_drop_ids = order_dict
 
class cash_drop_line(models.TransientModel):
	_name = "cash.drop.line"

	time = fields.Datetime('Date')
	receipt_number = fields.Char('Receipt Number')
	value = fields.Float('Value')
	cash_drop_id = fields.Many2one('cash.drop.report','Operator')
