import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

from datetime import datetime, date, time, timedelta
import time

class operator_monitor_report(models.TransientModel):
	_name = "operator.monitor.report"

	date = fields.Date('Date')
	user_id = fields.Many2one('res.users','Operator')
	day_shift = fields.Selection([('day','Day'),('shift','Shift')],'Day/Shift')
	shift_id = fields.Many2one('shift.master','Shift')
	operator_monitor_ids = fields.One2many('operator.monitor.line','operator_monitor_id','Operator Monitor')

	@api.onchange('date','user_id','day_shift','shift_id')
	def onchange_date(self):
		if self.date and self.user_id and self.day_shift == 'day':
			pos_order_ids = self.env['pos.order'].search([('date_order','>=',self.date),('date_order','<=',self.date),('user_id','=',self.user_id.id)])
			order_dict = []
			for order in pos_order_ids:
				for order_line in order.lines:
					order_dict.append((0, 0, {'operator_id': order.session_id.user_id.id, 'date': order.date_order,'product_id':order_line.product_id.id,'quantity':order_line.qty,'price':order_line.price_unit,'amount':order_line.qty*order_line.price_unit}))	
			self.operator_monitor_ids = order_dict
		elif self.date and self.user_id and self.day_shift == 'shift':
			pos_session_ids = self.env['pos.session'].search([('user_id','=',self.user_id.id),('shift_id','=',self.shift_id.id)])
			pos_session_list = []
			for pos_session in pos_session_ids:
				pos_session_list.append(pos_session.id)
			pos_order_ids = self.env['pos.order'].search([('date_order','>=',self.date),('date_order','<=',self.date),('session_id','in',pos_session_list)])
			order_dict = []
			for order in pos_order_ids:
				for order_line in order.lines:
					order_dict.append((0, 0, {'operator_id': order.session_id.user_id.id, 'date': order.date_order,'product_id':order_line.product_id.id,'quantity':order_line.qty,'price':order_line.price_unit,'amount':order_line.qty*order_line.price_unit}))	
			self.operator_monitor_ids = order_dict
			
class operator_monitor_line(models.TransientModel):
	_name = "operator.monitor.line"

	operator_id = fields.Many2one('res.users','Operator')
	date = fields.Datetime('Date')
	reference = fields.Char('Reference')
	description = fields.Char('Description')
	till_code = fields.Char('Till Code')
	product_id = fields.Many2one('product.product','Name')
	quantity = fields.Float('Quantity')
	price = fields.Float('Price')
	amount = fields.Float('Amount')
	other_data = fields.Char('Other Data')
	operator_monitor_id = fields.Many2one('operator.monitor.report','Operator')
