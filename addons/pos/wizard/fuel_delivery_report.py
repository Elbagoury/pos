import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

from datetime import datetime, date, time, timedelta
import time

class fuel_delivery_report(models.TransientModel):
	_name = "fuel.delivery.report"

	date = fields.Date('Date')
	day_shift = fields.Selection([('day','Day'),('shift','Shift')],'Day/Shift')
	shift_id = fields.Many2one('shift.master','Shift')
	fuel_delivery_ids = fields.One2many('fuel.delivery.line','fuel_delivery_id','Fuel Delivery')
	
	@api.onchange('date','day_shift','shift_id')
	def onchange_fuel_delivery(self):
		
		if self.date and self.day_shift=='day':
			
			fuel_delivery_list = []
			fuel_delivery_br = self.env['fuel.delivery'].search([('date','=',self.date)])	
				
			opening_gauge_ids = self.env['tank.reading'].search([('date','<=',self.date),('date','>=',self.date)], order='date asc', limit=1)
			closing_gauge_ids = self.env['tank.reading'].search([('date','<=',self.date),('date','>=',self.date)], order='date desc', limit=1)
			for tank in self.env['tank.master'].search([]):
				sale_product = 0
				purchase_product = 0
				nozle_list = []
				for nozle in self.env['dom.nozle'].search([('tank_id','=',tank.id)]):
					nozle_list.append(nozle.id)
				pos_order_list = []
				for pos_order in self.env['pos.order'].search([('date_order','>=',self.date),('date_order','<=',self.date),('nozle_id','in',nozle_list)]):
					pos_order_list.append(pos_order.id)
				for line in self.env['pos.order.line'].search([('order_id','in',pos_order_list),('product_id','=',tank.tank_type.id)]): 
					if line:
						sale_product += line.qty
				
				for fuel_delivery in fuel_delivery_br:
					for tank_log in self.env['fuel.delivery.detail'].search([('fuel_delivery_id','=',fuel_delivery.id),('tank_id','=',tank.id)]):
						purchase_product += tank_log.fuel_qty
				
				opening_gauge_sr = self.env['tank.log.reading'].search([('date_time','<=',self.date),('date_time','>=',self.date),('tank_id','=',tank.id)], order='date_time asc', limit=1)
				closing_gauge_sr = self.env['tank.log.reading'].search([('date_time','<=',self.date),('date_time','>=',self.date),('tank_id','=',tank.id)], order='date_time desc', limit=1)
				
				close_book = closing_gauge_sr.opening_gauge- opening_gauge_sr.opening_gauge + purchase_product
				variance = close_book - sale_product
				
				fuel_delivery_list.append((0, 0, {'tank_id': tank.id, 'product_id':tank.tank_type.id,'opening_gauge':opening_gauge_sr.opening_gauge,'delivery':purchase_product,'sales':sale_product,'closing_book':close_book,'closing_gauge':closing_gauge_sr.opening_gauge,'variance':variance}))
			
			self.fuel_delivery_ids = fuel_delivery_list
				
				
		#if self.date and self.day_shift=='day':
			
			##purchase_order_ids = self.env['purchase.order'].search([('date_order','>=',self.date),('date_order','<=',self.date)])
			##purchase_order_list = []
			##for purchase_order in purchase_order_ids:
				##purchase_order_list.append(purchase_order.id)
			
			##pos_order_ids = self.env['pos.order'].search([('date_order','>=',self.date),('date_order','<=',self.date)])
			##pos_order_list = []
			##for pos_order in pos_order_ids:
				##pos_order_list.append(pos_order.id)
				
			#fuel_delivery = []
			#fuel_delivery_br = self.env['fuel.delivery'].search([('date','=',self.date)])		
			#for tank in self.env['tank.master'].search([]):
				#purchase_product = 0
				#sale_product = 0
				#opening_gauge = 0
				#closing_gauge = 0
				#for tank_log_reading in self.env['tank.log.reading'].search([('date_time','>=',self.date),('date_time','<=',self.date),('tank_id','=',tank.id)]):
					#opening_gauge += tank_log_reading.opening_gauge
					#closing_gauge += tank_log_reading.closing_gauge
				##for purchase in self.env['purchase.order.line'].search([('order_id','in',purchase_order_list),('product_id','=',tank.tank_type.id)]):
					##if purchase:
						##purchase_product += purchase.product_qty
				#if fuel_delivery_br:
					#for tank_log in self.env['fuel.delivery.detail'].search([('fuel_delivery_id','=',fuel_delivery_br.id),('tank_id','=',tank.id)]):
						#purchase_product += tank_log.fuel_qty
				##for line in self.env['pos.order.line'].search([('order_id','in',pos_order_list),('product_id','=',tank.tank_type.id)]): 
					##if line:
						##sale_product += line.qty
						
				#nozle_list = []
				#for nozle in self.env['dom.nozle'].search([('tank_id','=',tank.id)]):
					#nozle_list.append(nozle.id)
				#pos_order_list = []
				#for pos_order in self.env['pos.order'].search([('date_order','>=',self.date),('date_order','<=',self.date),('nozle_id','in',nozle_list)]):
					#pos_order_list.append(pos_order.id)
				#for line in self.env['pos.order.line'].search([('order_id','in',pos_order_list),('product_id','=',tank.tank_type.id)]): 
					#if line:
						#sale_product += line.qty
				
				#close_book = opening_gauge + purchase_product - sale_product
				#variance = close_book - closing_gauge
				#fuel_delivery.append((0, 0, {'tank_id': tank.id, 'product_id':tank.tank_type.id,'opening_gauge':opening_gauge,'delivery':purchase_product,'sales':sale_product,'closing_book':close_book,'closing_gauge':closing_gauge,'variance':variance}))
			
			#self.fuel_delivery_ids = fuel_delivery
			
		elif self.date and self.day_shift=='shift':
			pos_session_list = []
			for pos_session in self.env['pos.session'].search([('shift_id','=',self.shift_id.id)]):
				pos_session_list.append(pos_session.id)
			fuel_delivery = []
			for tank in self.env['tank.master'].search([]):
				purchase_product = 0
				sale_product = 0
				opening_gauge = 0
				closing_gauge = 0
				for tank_log_reading in self.env['tank.log.reading'].search([('date_time','>=',self.date),('date_time','<=',self.date),('tank_id','=',tank.id),('shift_id','=',self.shift_id.id)]):
					opening_gauge += tank_log_reading.opening_gauge
					closing_gauge += tank_log_reading.closing_gauge
				#for purchase in self.env['purchase.order.line'].search([('order_id','in',purchase_order_list),('product_id','=',tank.tank_type.id)]):
					#if purchase:
						#purchase_product += purchase.product_qty
						
				for tank_log in self.env['tank.log'].search([('date','=',self.date),('tank_id','=',tank.id),('shift_id','=',self.shift_id.id)]):
					purchase_product += tank_log.qty
				#for line in self.env['pos.order.line'].search([('order_id','in',pos_order_list),('product_id','=',tank.tank_type.id)]): 
					#if line:
						#sale_product += line.qty
						
				nozle_list = []
				for nozle in self.env['dom.nozle'].search([('tank_id','=',tank.id)]):
					nozle_list.append(nozle.id)
				pos_order_list = []
				for pos_order in self.env['pos.order'].search([('date_order','>=',self.date),('date_order','<=',self.date),('nozle_id','in',nozle_list),('session_id','in',pos_session_list)]):
					pos_order_list.append(pos_order.id)
				for line in self.env['pos.order.line'].search([('order_id','in',pos_order_list),('product_id','=',tank.tank_type.id)]): 
					if line:
						sale_product += line.qty
				
				close_book = opening_gauge + purchase_product - sale_product
				variance = close_book - closing_gauge
				fuel_delivery.append((0, 0, {'tank_id': tank.id, 'product_id':tank.tank_type.id,'opening_gauge':opening_gauge,'delivery':purchase_product,'sales':sale_product,'closing_book':close_book,'closing_gauge':closing_gauge,'variance':variance}))
			
			self.fuel_delivery_ids = fuel_delivery
			
					
class fuel_delivery_line_report(models.TransientModel):
	_name = "fuel.delivery.line"

	tank_id = fields.Many2one('tank.master', 'Tank')
	opening_gauge = fields.Float('Opening Gauge')
	delivery = fields.Float('Delivery')
	sales = fields.Float('Sales')
	closing_gauge = fields.Float('Closing Gauge')
	variance = fields.Float('Variance')
	closing_book = fields.Float('Closing Book')
	product_id = fields.Many2one('product.product','Grade')
	fuel_delivery_id = fields.Many2one('fuel.delivery.report','Fuel Delivery')
	pump_test = fields.Float('Pump Test')
	var_percent = fields.Float('Var%')
	water_level = fields.Float('Water Level')
	temp = fields.Float('Temperature')
	gauge = fields.Float('Gauge')
