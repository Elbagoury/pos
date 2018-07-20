import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

from datetime import datetime, date, time, timedelta
import time

class day_summary_report(models.TransientModel):
	_name = "day.summary.report"

	date = fields.Date('Date')
	day_shift = fields.Selection([('day','Day'),('shift','Shift')],'Day/Shift')
	shift_id = fields.Many2one('shift.master','Shift')
	day_summary_ids = fields.One2many('day.summary.line.report','day_summary_id','Day Summary')
	
	@api.onchange('date','day_shift')
	def onchange_day_summary(self):
		if self.date:
			day_summary_list = []
			for shift in self.env['shift.master'].search([]):
				pos_session_list = []
				for pos_session in self.env['pos.session'].search([('shift_id','=',shift.id)]):
					pos_session_list.append(pos_session.id)
				pos_order_list = []
				for pos_order in self.env['pos.order'].search([('date_order','>=',self.date),('date_order','<=',self.date),('session_id','in',pos_session_list)]):
					pos_order_list.append(pos_order.id)	
				for pos_category in self.env['pos.category'].search([]):
					product_list = []
					sales_qty = 0
					for product in self.env['product.product'].search([('pos_categ_id','=',pos_category.id)]):
						product_list.append(product.id)
					for line in self.env['pos.order.line'].search([('order_id','in',pos_order_list),('product_id','in',product_list)]): 
						sales_qty += line.qty
					
					day_summary_list.append((0, 0, {'shift_id': shift.id, 'pos_categ_id':pos_category.id,'total':sales_qty}))
			self.day_summary_ids = day_summary_list
			
class day_summary_line_report(models.TransientModel):
	_name = "day.summary.line.report"

	shift_id = fields.Many2one('shift.master','Shift')
	pos_categ_id = fields.Many2one('pos.category','Category')
	product_id = fields.Many2one('product.product','Grade')
	total = fields.Float('Total')
	day_summary_id = fields.Many2one('day.summary.report','Day Summary')
