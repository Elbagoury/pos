import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

from datetime import datetime, date, time, timedelta
import time

class sales_report(models.TransientModel):
	_name = "sales.report"

	date = fields.Date('Date')
	day_shift = fields.Selection([('day','Day'),('shift','Shift')],'Day/Shift')
	product_category = fields.Selection([('product','Product'),('category','Category')],'Product/Category')
	shift_id = fields.Many2one('shift.master','Shift')
	sales_ids = fields.One2many('sales.line','sales_id','Sales')
	pos_category_id = fields.Many2one('pos.category','Category')
	
	@api.onchange('date','day_shift','product_category','shift_id','pos_category_id')
	def onchange_sales_report(self):
		sales_dict = []
		if self.date and self.day_shift == 'day' and self.product_category == 'product':
			pos_order_ids = self.env['pos.order'].search([('date_order','>=',self.date),('date_order','<=',self.date)])
			pos_order_list = []
			for pos_order in pos_order_ids:
				pos_order_list.append(pos_order.id)
			
			for product in self.env['product.product'].search([]):
				product_wise_total = 0
				for line in self.env['pos.order.line'].search([('order_id','in',pos_order_list),('product_id','=',product.id)]):
					if line:
						fpos = line.order_id.fiscal_position_id
						tax_ids_after_fiscal_position = fpos.map_tax(line.tax_ids, line.product_id, line.order_id.partner_id) if fpos else line.tax_ids
						price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
						taxes = tax_ids_after_fiscal_position.compute_all(price, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id, partner=line.order_id.partner_id)
						product_wise_total += taxes['total_included']
				if product_wise_total != 0:
					sales_dict.append((0, 0, {'product_id': product.id, 'value': product_wise_total}))
		
		elif self.date and self.day_shift == 'shift' and self.product_category == 'product':
			pos_session_ids = self.env['pos.session'].search([('shift_id','=',self.shift_id.id)])
			pos_session_list = []
			for pos_session in pos_session_ids:
				pos_session_list.append(pos_session.id)
			pos_order_ids = self.env['pos.order'].search([('date_order','>=',self.date),('date_order','<=',self.date),('session_id','in',pos_session_list)])
			pos_order_list = []
			if pos_order_ids:
				for pos_order in pos_order_ids:
					pos_order_list.append(pos_order.id)
				for product in self.env['product.product'].search([]):
					product_wise_total = 0
					for line in self.env['pos.order.line'].search([('order_id','in',pos_order_list),('product_id','=',product.id)]):
						if line:
							fpos = line.order_id.fiscal_position_id
							tax_ids_after_fiscal_position = fpos.map_tax(line.tax_ids, line.product_id, line.order_id.partner_id) if fpos else line.tax_ids
							price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
							taxes = tax_ids_after_fiscal_position.compute_all(price, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id, partner=line.order_id.partner_id)
							product_wise_total += taxes['total_included']
					if product_wise_total != 0:
						sales_dict.append((0, 0, {'product_id': product.id, 'value': product_wise_total}))
					
		elif self.date and self.day_shift == 'day' and self.product_category == 'category':
			pos_order_ids = self.env['pos.order'].search([('date_order','>=',self.date),('date_order','<=',self.date)])
			pos_order_list = []
			for pos_order in pos_order_ids:
				pos_order_list.append(pos_order.id)
			for product in self.env['product.product'].search([('pos_categ_id','=',self.pos_category_id.id)]):
				product_wise_total = 0
				for line in self.env['pos.order.line'].search([('order_id','in',pos_order_list),('product_id','=',product.id)]):
					if line:
						fpos = line.order_id.fiscal_position_id
						tax_ids_after_fiscal_position = fpos.map_tax(line.tax_ids, line.product_id, line.order_id.partner_id) if fpos else line.tax_ids
						price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
						taxes = tax_ids_after_fiscal_position.compute_all(price, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id, partner=line.order_id.partner_id)
						product_wise_total += taxes['total_included']
				if product_wise_total !=0:
					sales_dict.append((0, 0, {'product_id': product.id, 'value': product_wise_total}))
			
		elif self.date and self.day_shift == 'shift' and self.product_category == 'category':
			pos_session_ids = self.env['pos.session'].search([('shift_id','=',self.shift_id.id)])
			pos_session_list = []
			for pos_session in pos_session_ids:
				pos_session_list.append(pos_session.id)
			pos_order_ids = self.env['pos.order'].search([('date_order','>=',self.date),('date_order','<=',self.date),('session_id','in',pos_session_list)])
			pos_order_list = []
			if pos_order_ids:
				for pos_order in pos_order_ids:
					pos_order_list.append(pos_order.id)
				for product in self.env['product.product'].search([('pos_categ_id','=',self.pos_category_id.id)]):
					product_wise_total = 0
					for line in self.env['pos.order.line'].search([('order_id','in',pos_order_list),('product_id','=',product.id)]):
						if line:
							fpos = line.order_id.fiscal_position_id
							tax_ids_after_fiscal_position = fpos.map_tax(line.tax_ids, line.product_id, line.order_id.partner_id) if fpos else line.tax_ids
							price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
							taxes = tax_ids_after_fiscal_position.compute_all(price, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id, partner=line.order_id.partner_id)
							product_wise_total += taxes['total_included']
					if product_wise_total != 0:
						sales_dict.append((0, 0, {'product_id': product.id, 'value': product_wise_total}))
		self.sales_ids = sales_dict
						
class sales_line(models.TransientModel):
	_name = "sales.line"

	product_id = fields.Many2one('product.product','Product')
	value = fields.Float('Value')
	sales_id = fields.Many2one('sales.report','Sales')
