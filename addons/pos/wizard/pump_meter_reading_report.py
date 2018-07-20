import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

from datetime import datetime, date, time, timedelta
import time

class pump_meter_read_report(models.TransientModel):
	_name = "pump.meter.read.report"

	date = fields.Date('Date')
	day_shift = fields.Selection([('day','Day'),('shift','Shift')],'Day/Shift')
	shift_id = fields.Many2one('shift.master','Shift')
	pump_meter_ids = fields.One2many('pump.meter.read.line.report','pump_meter_id','Pump Meter Read')
	
	@api.onchange('date','day_shift','shift_id')
	def onchange_fuel_delivery(self):
		if self.date and self.day_shift=='day':
			pump_meter_read = []
			
			opening_gauge_ids = self.env['pump.meter'].search([('date','<=',self.date),('date','>=',self.date)], order='date asc', limit=1)
			closing_gauge_ids = self.env['pump.meter'].search([('date','<=',self.date),('date','>=',self.date)], order='date desc', limit=1)

			for open_gauge in opening_gauge_ids.pump_nozzle_ids:
				close_gauge = self.env['pump.meter.log'].search([('pump_log_id','=',closing_gauge_ids.id),('nozzel_id','=',open_gauge.nozzel_id.id)])
				meter_sale = close_gauge.opening_read - open_gauge.opening_read
				net_meter_sale = meter_sale
				
				pos_order_list = []
				sale_product = 0
				for pos_order in self.env['pos.order'].search([('date_order','>=',self.date),('date_order','<=',self.date),('nozle_id','=',open_gauge.nozzel_id.id)]):
					pos_order_list.append(pos_order.id)
				for line in self.env['pos.order.line'].search([('order_id','in',pos_order_list),('product_id','=',open_gauge.nozzel_id.tank_id.tank_type.id)]): 
					if line:
						sale_product += line.qty
				variance = sale_product - net_meter_sale
				pump_meter_read.append((0, 0, {'pump_id':open_gauge.pump_id.id,'nozzel_id':open_gauge.nozzel_id.id,'product_id':open_gauge.nozzel_id.product_id.id,'opening_read':open_gauge.opening_read,'closing_read':close_gauge.opening_read,'meter_sale':meter_sale,'net_meter_sale':net_meter_sale,'till_sales':sale_product,'variance':variance}))
			self.pump_meter_ids = pump_meter_read
			
	#@api.onchange('date','day_shift','shift_id')
	#def onchange_fuel_delivery(self):
		#if self.date and self.day_shift=='day':
			#pump_meter_read = []
			#for tank in self.env['tank.master'].search([]):
				#purchase_stock = 0
				#for tank_log in self.env['tank.log'].search([('date','<',self.date),('tank_id','=',tank.id)]):
					#purchase_stock += tank_log.qty
				#for tank_log_read in self.env['tank.log.reading'].search([('date_time','<',self.date),('tank_id','=',tank.id)]):
					#purchase_stock += tank_log_read.opening_gauge
				#for nozzel in self.env['dom.nozle'].search([('tank_id','=',tank.id)]):
					#sale_product = 0
					#for pos_order in self.env['pos.order'].search([('date_order','<',self.date),('nozle_id','=',nozzel.id)]):
						#for order_line in self.env['pos.order.line'].search([('product_id','=',tank.tank_type.id)]):
							#sale_product += order_line.qty
					#open_stock = purchase_stock - sale_product
				
				#purchase_stock = 0
				#for tank_log in self.env['tank.log'].search([('date','<=',self.date),('tank_id','=',tank.id)]):
					#purchase_stock += tank_log.qty
				#for tank_log_read in self.env['tank.log.reading'].search([('date_time','<=',self.date),('tank_id','=',tank.id)]):
					#purchase_stock += tank_log_read.opening_gauge
				#for nozzel in self.env['dom.nozle'].search([('tank_id','=',tank.id)]):
					#sale_product = 0
					#for pos_order in self.env['pos.order'].search([('date_order','<=',self.date),('nozle_id','=',nozzel.id)]):
						#for order_line in self.env['pos.order.line'].search([('product_id','=',tank.tank_type.id)]):
							#sale_product += order_line.qty
					#close_stock = purchase_stock - sale_product
				
				
					#pump_meter_read.append((0,0,{'pump_id':nozzel.dom_pump_id.id,'nozzel_id':nozzel.id,'product_id':tank.tank_type.id,'opening_read':open_stock,'closing_read':close_stock}))
			#self.pump_meter_ids = pump_meter_read
			
class pump_meter_read_line_report(models.TransientModel):
	_name = "pump.meter.read.line.report"

	nozzel_id = fields.Many2one('dom.nozle', 'Nozzel')
	pump_id = fields.Many2one('dom.pump','Pump', order='pump_id')
	product_id = fields.Many2one('product.product','Grade')
	opening_read = fields.Float('Opening Read')
	closing_read = fields.Float('Closing Read')
	meter_sale = fields.Float('Meter Sale')
	pump_test = fields.Float('Pump Test')
	net_meter_sale = fields.Float('Net Meter Sale')
	till_sales = fields.Float('Till Sale')
	variance = fields.Float('Variance')
	pump_meter_id = fields.Many2one('pump.meter.read.report','Pump Meter Read')

