import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.osv import expression
import base64
from functools import partial

from datetime import datetime, date, time, timedelta
import time
from odoo.exceptions import ValidationError

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)

class dom_nozle(models.Model):
	_name="dom.nozle"
	
	available_fuel = fields.Float('Available Fuel')
	consumed_fuel = fields.Float('Consumed Fuel')
	display_name = fields.Char('Display Name')
	image = fields.Binary('Image')
	image1 = fields.Binary('Image')
	is_active = fields.Boolean('Active')
	dom_pump_id = fields.Many2one('dom.pump','Pump')
	left_fuel = fields.Float('Left Fuel')
	name = fields.Char('Name')
	product_id = fields.Many2one('product.product','Product')
	state = fields.Selection([('idle','Idle'),('reserved','Reserved'),('requested','Requested'),('approve','Approve'),('denied','Denied')], 'State')
	vechile_info = fields.Char('Vechile info')
	pos_order_ids = fields.One2many('pos.order','nozle_id','Orders')
	tank_id = fields.Many2one('tank.master','Tank')
	
	@api.model
	def get_request_from_dom(self, name, image_f):
		if name:
			nozle_id = self.env['dom.nozle'].search([('name','=',name)])
			if nozle_id.state == 'idle':
				nozle_id.write({'state':'requested', 'image':image_f})
				notification = {'nozle_id':nozle_id.id, 'image':image_f, 'nozle_polling':'pos.nozle_polling'}
				self.env['bus.bus'].sendone((self._cr.dbname, 'res.partner', self.env.user.partner_id.id), notification)
				return [1]
			elif nozle_id.state == 'reserved':
				return [0]
		
	@api.model
	def check_dom_approve_or_denied(self, name):
		if name:
			nozle_id = self.env['dom.nozle'].search([('name','=',name)])
			if nozle_id.state == 'reserved':
				return [1]
			elif nozle_id.state == 'denied':
				return [0]
			elif nozle_id.state == 'requested':
				return [2]

	@api.model
	def get_request_from_dom_make_order(self, name, qty):
		if name:
			nozle_id = self.env['dom.nozle'].search([('name','=',name)])
			notification = {'nozle_id':nozle_id.id, 'quantity':qty, 'nozle_polling':'pos.make_order'}
			self.env['bus.bus'].sendone((self._cr.dbname, 'res.partner', self.env.user.partner_id.id), notification)
			return [1]
	
	@api.model
	def nozle_vehicle_info_in_reserved_state(self, nozle_id, vehicle_info):
		if nozle_id and vehicle_info:
			nozle = self.env['dom.nozle'].search([('id','=',nozle_id)])
			nozle.write({'vechile_info':vehicle_info, 'state':'reserved'})
			return True
		
	@api.model
	def get_nozle_request_from_pos(self, nozle_id, status):
		nozle_id = self.env['dom.nozle'].search([('id','=',nozle_id)])
		if status == 'approve':
			nozle_id.write({'state':'approve'})
			return True
		elif status =='denied':
			nozle_id.write({'state':'denied'})
			return True
			
	@api.onchange('tank_id')
	def onchange_tank_id(self):
		if self.tank_id:
			self.available_fuel = self.tank_id.available_fuel
			self.consumed_fuel = self.tank_id.consumed_fuel
			self.left_fuel = self.tank_id.left_fuel
			self.product_id = self.tank_id.tank_type.id
	
	@api.model		
	def make_nozle_in_idle_state(self, nozle_id):
		if nozle_id:
			nozle = self.env['dom.nozle'].search([('id','=',nozle_id)])
			nozle.write({'state':'idle'})
	
class dom_pump(models.Model):
	_name = "dom.pump"
	
	available_fuel = fields.Float('Available Fuel')
	consumed_fuel = fields.Float('Consumed Fuel')
	display_name = fields.Char('Display Name')
	image = fields.Binary('Image')
	is_active = fields.Boolean('Active')
	dom_nozle_ids = fields.One2many('dom.nozle','dom_pump_id','Nozle')
	left_fuel = fields.Float('Left Fuel')
	name = fields.Char('Name')
	product_id = fields.Many2one('product.product','Product')
	
class PosOrder(models.Model):
	_inherit="pos.order"
	
	nozle_id = fields.Many2one('dom.nozle','Nozle')
	vehicle_info = fields.Char("Vechile Info")
	
	@api.model
    	def _order_fields(self, ui_order):
       		process_line = partial(self.env['pos.order.line']._order_line_fields)
       		nozle_id = self.env['dom.nozle'].search([('id','=',ui_order['nozle_id'])])
       		tank_ids = self.env['tank.master'].search([('id','=',nozle_id.tank_id.id)])
		for l in ui_order['lines']:
			if l and len(l) == 3 and l[2] is not False:
				if l[2].get('product_id') == tank_ids.tank_type.id:
					total_consumed_qty = tank_ids.consumed_fuel + l[2].get('qty', 0.0)
					tank_ids.write({'consumed_fuel':total_consumed_qty})
			if ui_order['vehicle_info']:
				vechile_no = ui_order['vehicle_info']
			else:
				vechile_no = ' '
        	return {
				'name':         ui_order['name'],
				'user_id':      ui_order['user_id'] or False,
				'session_id':   ui_order['pos_session_id'],
				'lines':        [process_line(l) for l in ui_order['lines']] if ui_order['lines'] else False,
				'pos_reference': ui_order['name'],
            	'partner_id':   ui_order['partner_id'] or False,
            	'date_order':   ui_order['creation_date'],
            	'fiscal_position_id': ui_order['fiscal_position_id'],
            	'nozle_id': ui_order['nozle_id'],
            	'vehicle_info': vechile_no
			}
	
class day_master(models.Model):
	_name = "day.master"
	
	name = fields.Char("Day")
	date_from = fields.Datetime("Date From")
	date_to = fields.Datetime("Date To")
	shift_ids = fields.One2many('shift.day.master','day_master_id','Shift')
	batch_id = fields.Many2one('batch.master','Branch', ondelete='cascade')
	state = fields.Selection([('active','Active'),('archived','Archived')], 'State')
	
class shift_day_master(models.Model):
	_name = "shift.day.master"
	
	name = fields.Many2one('shift.master','Shift')
	date_from = fields.Datetime("Date From")
	date_to = fields.Datetime("Date To")
	day_master_id = fields.Many2one('day.master','Day', ondelete='cascade')

class shift_master(models.Model):
	_name = 'shift.master'
	
	name = fields.Char('Shift Id')
	
	_sql_constraints = [
		('name_uniq', 'unique(name)', 'Already same shift name created'),
	]
		
class tank_master(models.Model):
	_name = "tank.master"
	
	name = fields.Char('Name')
	tank_type = fields.Many2one('product.product','Type')
	capacity = fields.Float('Capacity')
	available_fuel = fields.Float(compute='_get_available_fuel',string='Available Fuel')
	consumed_fuel = fields.Float(compute='_get_consumed_fuel',string='Consumed Fuel')
	left_fuel = fields.Float(compute='_get_left_fuel',string='Left Fuel')
	tank_log_ids = fields.One2many('tank.log','tank_id','Tank Log')
	ullage = fields.Float('Ullage')
	water = fields.Float('Water')
	temp = fields.Float('temp')
	
	@api.multi
	@api.depends('available_fuel')
	def _get_available_fuel(self):
		purchase_total= 0
		#for tank_log in self.env['tank.log'].search([('date','=',fields.Datetime.now()),('tank_id','=',self.id)]):
			#purchase_total += tank_log.qty
		for fuel_delivery in self.env['fuel.delivery'].search([('date','=',datetime.today().strftime('%Y-%m-%d'))]):
			if fuel_delivery:
				for fuel_line in self.env['fuel.delivery.detail'].search([('fuel_delivery_id','=',fuel_delivery.id),('tank_id','=',self.id)]):
					purchase_total += fuel_line.fuel_qty
		for open_stock in self.env['tank.log.reading'].search([('date_time','>=',datetime.today().strftime('%Y-%m-%d')),('date_time','<=',datetime.today().strftime('%Y-%m-%d')),('tank_id','=',self.id)]):
			if open_stock:
				if 	open_stock.opening_gauge != 0:
					self.available_fuel = open_stock.opening_gauge + purchase_total
			else:
				self.available_fuel = purchase_total
	@api.multi
	@api.depends('consumed_fuel')
	def _get_consumed_fuel(self):	
		self.consumed_fuel = self.available_fuel - self.left_fuel

	@api.multi
	@api.depends('left_fuel')
	def _get_left_fuel(self):
		for close_stock in self.env['tank.log.reading'].search([('date_time','>=',datetime.today().strftime('%Y-%m-%d')),('date_time','<=',datetime.today().strftime('%Y-%m-%d')),('tank_id','=',self.id)]):
			if close_stock.closing_gauge != 0:
				self.left_fuel = close_stock.closing_gauge
		
class batch_master(models.Model):
	_name = "batch.master"
	
	batch_start = fields.Datetime('Batch Start')
	batch_end = fields.Datetime('Batch End')
	day_ids = fields.One2many('day.master','batch_id','Day')
	state = fields.Selection([('active','Active'),('archived','Archived')], 'State')
	
	@api.onchange('batch_start','batch_end')
	def onchange_date(self):
		if self.batch_start and self.batch_end:
			date_start = datetime.strptime(self.batch_start, "%Y-%m-%d %H:%M:%S")
			date_end = datetime.strptime(self.batch_end, "%Y-%m-%d %H:%M:%S")
			day = 0
			day_ids = self.env['day.master'].search([],order='id desc',limit=1)
			if day_ids:
				day = int(day_ids.name) + 1
			else:
				day = 1
			day_dict = []
			while date_start <= date_end:
				day_end = date_start + timedelta(days=1)
				day_dict.append((0, 0, {'name': day, 'date_from': date_start.strftime("%Y-%m-%d %H:%M:%S"),'date_to':day_end.strftime("%Y-%m-%d %H:%M:%S")}))
				day += 1
				date_start = date_start + timedelta(days=1)
			self.day_ids = day_dict
			
#class PosOrder(models.Model):
	#_inherit = 'pos.order'
			
	#@api.model
	#def check_shift_time(self):
		#day_master_ids = self.env['day.master'].search([('state','=','active')])
		#for days in day_master_ids:
			#for shift in days.shift_ids:
				#print datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				##date_to = datetime.strptime(shift.date_to, "%Y-%m-%d %H:%M:%S")
				##date_to.strftime("%Y-%m-%d %H:%M:%S")
				#print date_to
				#if datetime.now().strftime('%Y-%m-%d %H:%M:%S') == shift.date_to:
					#print "Execute"
					#raise osv.except_osv(_('Warning'), _('Shift time over'))
					#_logger.warning('Shift time over')
					##raise ValidationError(_("Shift time over"))

class PosSession(models.Model):
	_inherit = 'pos.session'
	
	shift_id = fields.Many2one('shift.master','Shift')
	
	@api.multi
    	def action_pos_session_open(self):
        # second browse because we need to refetch the data from the DB for cash_register_id
        # we only open sessions that haven't already been opened
		for session in self.filtered(lambda session: session.state == 'opening_control'):
		    values = {}
		    shift_id = self.env['tank.reading'].search([('date','<=', datetime.now().date().strftime("%Y-%m-%d")),('date','>=',datetime.now().date().strftime("%Y-%m-%d"))])
		    if not shift_id:
				raise ValidationError(_("First Create tank log Reading"))
		    
		    if not session.start_at:
		        values['start_at'] = fields.Datetime.now()
		    day_id = self.env['day.master'].search([('date_from','<=', fields.Datetime.now()),('date_to','>=',fields.Datetime.now())])
		    if day_id:
				if not day_id.shift_ids:
					shift_master_id = self.env['shift.master'].search([('name','=','1')])
					day_id.shift_ids.create({'name':shift_master_id.id,'date_from':fields.Datetime.now(),'day_master_id':day_id.id})
					#shift_id = self.env['shift.day.master'].search([('date_from','<=', fields.Datetime.now()),('date_to','>=',fields.Datetime.now()),('day_master_id','=',day_id.id)])
					#if shift_id:
						#values['shift_id'] = shift_id.name.id
					values['shift_id'] = shift_master_id.id
					#else:
						#raise ValidationError(_("First create a shift for today date"))
				elif day_id.shift_ids:
					shift_list = []
					for day in self.env['day.master'].search([('date_from','<=', fields.Datetime.now()),('date_to','>=',fields.Datetime.now())]):
						for shift in day.shift_ids:
							shift_list.append(shift.id)
					next_shift = str(len(shift_list) + 1)
					shift_master_id = self.env['shift.master'].search([('name','=',next_shift)])
					if shift_master_id:
						self.env['shift.day.master'].create({'name':shift_master_id.id,'date_from':fields.Datetime.now(),'day_master_id':day_id.id})
						values['shift_id'] = shift_master_id.id
					elif not shift_master_id:
						shift_master_id = self.env['shift.master'].create({'name':next_shift})
						self.env['shift.day.master'].create({'name':shift_master_id.id,'date_from':fields.Datetime.now(),'day_master_id':day_id.id})
						values['shift_id'] = shift_master_id.id
						
				values['state'] = 'opened'
				session.write(values)
				session.statement_ids.button_open()
				return True
						
		    else:
				raise ValidationError(_("First Active the current day shift"))
				
	@api.multi
	def action_pos_session_closing_control(self):
		for session in self:
			for statement in session.statement_ids:
				if (statement != session.cash_register_id) and (statement.balance_end != statement.balance_end_real):
						statement.write({'balance_end_real': statement.balance_end})
			#DO NOT FORWARD-PORT
			if session.state == 'closing_control':
				session.action_pos_session_close()
				continue
				
			shift_id = self.env['shift.day.master'].search([('date_from','=', session.start_at)])
			shift_id.write({'date_to':fields.Datetime.now()})
			session.write({'state': 'closing_control', 'stop_at': fields.Datetime.now()})
			if not session.config_id.cash_control:
				session.action_pos_session_close()
				
class StockMove(models.Model):
	_inherit = "stock.move"
	
	shift_id = fields.Many2one('shift.day.master','Shift')
	
class tank_log_reading(models.Model):
	_name = "tank.log.reading"
	
	tank_id = fields.Many2one('tank.master', 'Tank')
	day_id = fields.Many2one('day.master','Day')
	shift_id = fields.Many2one('shift.master','Shift')
	opening_gauge = fields.Float('Opening Gauge')
	closing_gauge = fields.Float('Closing Gauge')
	date_time = fields.Datetime('DATE TIME')
	tank_log_id = fields.Many2one('tank.reading','Tank Log', ondelete='cascade')
	product_id = fields.Many2one('product.product','Type')
	capacity = fields.Float('Capacity')
			
	@api.model
	def create(self,vals):
		res = super(tank_log_reading, self).create(vals)	
		if res:
			confirmation_date = datetime.strptime(res['date_time'], "%Y-%m-%d %H:%M:%S").date()
			tank_stock_log = self.env['tank.stock.log']
			tank_stock_log_ids = self.env['tank.stock.log'].search([('date','=',confirmation_date),('tank_id','=',res['tank_id'].id)])
			if not tank_stock_log_ids:
				tank_stock_log.create({'date':confirmation_date,'tank_id':res['tank_id'].id, 'product_id':res['tank_id'].tank_type.id,})
		return res

	#@api.model
	#def create_tank_stock_log(self):
		##today_date = self.date_time.strftime('%Y-%m-%d')
        	#confirmation_date = datetime.strptime(self.date_time, "%Y-%m-%d %H:%M:%S").date()
		#tank_stock_log_ids = self.env['tank.stock.log'].search([('date','=',confirmation_date)])
		#if self.opening_gauge:
			#if tank_stock_log_ids:
				#opening_gauge = tank_stock_log_ids.opening_gauge + self.opening_gauge
				#tank_stock_log_dict = {
										#'opening_gauge':opening_gauge
										#}
				#tank_stock_log_ids.write(tank_stock_log_dict)
			#else:
				#tank_stock_log_dict = {'tank_id':self.tank_id.id,
										#'product_id':self.tank_id.tank_type.id,
										#'opening_gauge':self.opening_gauge,
										#'date':confirmation_date
										#}
				#self.env['tank.stock.log'].create(tank_stock_log_dict)
		#if self.closing_gauge:
			#if tank_stock_log_ids:
				#closing_gauge = tank_stock_log_ids.closing_gauge + self.closing_gauge
				#tank_stock_log_dict = {
										#'closing_gauge':closing_gauge
										#}
				#tank_stock_log_ids.write(tank_stock_log_dict)
			#else:
				#tank_stock_log_dict = {'tank_id':self.tank_id.id,
										#'product_id':self.tank_id.tank_type.id,
										#'closing_gauge':self.closing_gauge,
										#'date':confirmation_date
										#}
				#self.env['tank.stock.log'].create(tank_stock_log_dict)
			
			
class PurchaseOrder(models.Model):
	_inherit = "purchase.order"
	
	shift_id = fields.Many2one('shift.day.master','Shift')

	@api.onchange('date_order')
	def onchange_orderdate(self):
		if self.date_order:
			shift_id = self.env['shift.day.master'].search([('date_from','<=', fields.Datetime.now()),('date_to','>=',fields.Datetime.now())])
			self.shift_id = shift_id.name.id
			#self.write({'shift_id':shift_id.name.id})
	
	#@api.multi
	#def button_confirm(self):
		#for order in self:
			#if order.state not in ['draft', 'sent']:
				#continue
			#order._add_supplier_to_product()
			#if order.company_id.po_double_validation == 'one_step'\
				#or (order.company_id.po_double_validation == 'two_step'\
					#and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))\
				#or order.user_has_groups('purchase.group_purchase_manager'):
				#order.button_approve()
			#else:
				#order.write({'state': 'to approve'})
			
			#if order.order_line:
				#for line in order.order_line:
					#if self.env['tank.master'].search([('tank_type','=',line.product_id.id)]):
						#confirmation_date = datetime.strptime(order.date_order, "%Y-%m-%d %H:%M:%S").date()
						#tank_stock_log_ids = self.env['tank.stock.log'].search([('date','=',confirmation_date)])
						#if tank_stock_log_ids:
							#delivery = tank_stock_log_ids.delivery + line.product_qty
							#tank_stock_log_dict = {
													#'delivery':delivery
													#}
							#tank_stock_log_ids.write(tank_stock_log_dict)
		
		#return True
			
class tank_stock_log(models.Model):
	_name = 'tank.stock.log'
	
	tank_id = fields.Many2one('tank.master', 'Tank')
	opening_gauge = fields.Float(compute='_get_opening_gauge',string='Opening Gauge')
	delivery = fields.Float(compute='_get_delivery',string='Delivery')
	sales = fields.Float(compute='_get_sales',string='Sales')
	closing_gauge = fields.Float(compute='_get_closing_gauge',string='Closing Gauge')
	variance = fields.Float(compute='_get_variance',string='Variance')
	closing_book = fields.Float(compute='_get_closing_book',string='Closing Book')
	product_id = fields.Many2one('product.product','Product')
	date = fields.Date('Date')
	
	@api.multi
	@api.depends('opening_gauge')
	def _get_opening_gauge(self):
		for stock in self:
			open_gauge_ids = self.env['tank.log.reading'].search([('date_time','>=',stock.date),('date_time','<=',stock.date),('tank_id','=',stock.tank_id.id)], order='date_time asc', limit=1)
			stock.opening_gauge = open_gauge_ids.opening_gauge
			
			#open_gauge = 0
			#for stock_open in open_gauge_ids:
				#open_gauge += stock_open.opening_gauge
			#stock.opening_gauge = open_gauge
				
	@api.multi
	@api.depends('closing_gauge')
	def _get_closing_gauge(self):
		for stock in self:
			close_gauge_ids = self.env['tank.log.reading'].search([('date_time','>=',stock.date),('date_time','<=',stock.date),('tank_id','=',stock.tank_id.id)], order='date_time desc', limit=1)
			stock.closing_gauge = close_gauge_ids.opening_gauge
			
			#close_gauge = 0
			#for stock_close in close_gauge_ids:
				#close_gauge += stock_close.closing_gauge
			#stock.closing_gauge = close_gauge
	
	@api.multi
	@api.depends('opening_gauge','delivery','sales','closing_book')
	def _get_closing_book(self):
		for open_stock in self:
			open_stock.closing_book = open_stock.opening_gauge + open_stock.delivery - open_stock.sales

	@api.multi
	@api.depends('closing_gauge','closing_book','variance')
	def _get_variance(self):
		for close_stock in self:
			close_stock.variance = close_stock.closing_book - close_stock.closing_gauge
			
	@api.multi
	@api.depends('sales')
	def _get_sales(self):
		for stock in self:
			nozle_list = []
			for nozle in self.env['dom.nozle'].search([('tank_id','=',stock.tank_id.id)]):
				nozle_list.append(nozle.id)
				
			pos_order_ids = self.env['pos.order'].search([('date_order','>=',stock.date),('date_order','<=',stock.date),('nozle_id','in',nozle_list)])
			sale_stock = 0
			pos_order_list = []
			for pos_order in pos_order_ids:
				pos_order_list.append(pos_order.id)
			for line in self.env['pos.order.line'].search([('order_id','in',pos_order_list),('product_id','=',stock.tank_id.tank_type.id)]): 
				if line:
					sale_stock += line.qty
			stock.sales = sale_stock
			
	@api.multi
	@api.depends('delivery')
	def _get_delivery(self):
		for stock in self:
			purchase_stock = 0
			for fuel_delivery in self.env['fuel.delivery'].search([('date','=',stock.date)]):
				purchase_stock = 0
				for fuel_line in self.env['fuel.delivery.detail'].search([('fuel_delivery_id','=',fuel_delivery.id),('tank_id','=',stock.tank_id.id)]):
					purchase_stock += fuel_line.fuel_qty	
			stock.delivery = purchase_stock		
			#tank_purchase = self.env['tank.log'].search([('date','=',stock.date),('tank_id','=',stock.tank_id.id)])
			#purchase_stock = 0
			#for tank in tank_purchase:
				#purchase_stock += tank.qty	
			#stock.delivery = purchase_stock				
		#for stock in self:
			#order_ids = self.env['purchase.order'].search([('date_order','>=',stock.date),('date_order','<=',stock.date)])
			#purchase_order_list = []
			#for purchase_order in order_ids:
				#purchase_order_list.append(purchase_order.id)
			#purchase_stock = 0
			#for purchase in self.env['purchase.order.line'].search([('order_id','in',purchase_order_list),('product_id','=',stock.tank_id.tank_type.id)]):
				#purchase_stock += purchase.product_qty
			#stock.delivery = stock.delivery + purchase_stock
			
class tank_log(models.Model):
	_name = 'tank.log'
	
	date = fields.Date('Date')
	product_id = fields.Many2one('product.product','Product')
	qty = fields.Float('Purchase Qty')
	tank_id = fields.Many2one('tank.master','Tank')
	shift_id = fields.Many2one('shift.master','Shift')
	
class tank_reading(models.Model):
	_name = 'tank.reading'
	
	date = fields.Datetime('Date')
	tank_log_ids = fields.One2many('tank.log.reading','tank_log_id','Tank Log')
	
	@api.onchange('date')
	def onchange_date(self):
		if self.date:
			tank_list = []
			tank_dict = {}
			for tank in self.env['tank.master'].search([]):
				prev_tank_read = self.env['tank.log.reading'].search([('tank_id','=',tank.id),('date_time','<=',datetime.strptime(self.date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'))],order='id desc', limit=1)
				if prev_tank_read:
					tank_dict = {'date_time':self.date,'tank_id':tank.id,'product_id':tank.tank_type.id,'capacity':tank.capacity,'closing_gauge':prev_tank_read.opening_gauge}
				else:
					tank_dict = {'date_time':self.date,'tank_id':tank.id,'product_id':tank.tank_type.id,'capacity':tank.capacity}
				
				tank_list.append((0,0,tank_dict))
				
			self.tank_log_ids = tank_list
			#day_id = self.env['day.master'].search([('date_from','<=', fields.Datetime.now()),('date_to','>=',fields.Datetime.now())])
			#shift_id = self.env['shift.day.master'].search([('date_from','<=', fields.Datetime.now()),('date_to','>=',fields.Datetime.now())])
			#if shift_id:
				#tank_dict = []
				#for tank in self.env['tank.master'].search([]):
					#tank_dict.append((0,0,{'date_time':self.date,'tank_id':tank.id,'product_id':tank.tank_type.id,'capacity':tank.capacity,'day_id':day_id.id,'shift_id':shift_id.name.id}))
				#self.tank_log_ids = tank_dict
			#else:
				#raise ValidationError(_("First create the current day shift"))

class pump_meter(models.Model):
	_name = 'pump.meter'
	
	date = fields.Datetime('Date')
	pump_nozzle_ids = fields.One2many('pump.meter.log','pump_log_id','Pump Nozzle')
	
	@api.onchange('date')
	def onchange_date(self):
		if self.date:
			pump_meter_list = []
			pump_dict = {}
			prev_pump_meter = self.env['pump.meter'].search([('date','<=',datetime.strptime(self.date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'))], order='id desc', limit=1)
			for nozzel in self.env['dom.nozle'].search([],order='dom_pump_id asc' ):
				if prev_pump_meter:
					for pump_log in self.env['pump.meter.log'].search([('pump_log_id','=',prev_pump_meter.id),('nozzel_id','=',nozzel.id)]):
						pump_dict = {'pump_id':nozzel.dom_pump_id.id,'nozzel_id':nozzel.id,'closing_read':pump_log.opening_read}
				else:
					pump_dict = {'pump_id':nozzel.dom_pump_id.id,'nozzel_id':nozzel.id}	
						
				pump_meter_list.append((0, 0, pump_dict))
			
			
			self.pump_nozzle_ids = pump_meter_list
			
			
class pump_meter_log(models.Model):
	_name = "pump.meter.log"
	
	nozzel_id = fields.Many2one('dom.nozle', 'Nozzel')
	pump_id = fields.Many2one('dom.pump','Pump', order='pump_id')
	opening_read = fields.Float('Current Reading')
	closing_read = fields.Float('Closing Reading')
	pump_log_id = fields.Many2one('pump.meter','Pump Meter')
	
class fuel_delivery(models.Model):
	_name = 'fuel.delivery'
		
	supplier = fields.Many2one('res.partner','Supplier')
	order_no = fields.Char('Order No')
	date = fields.Date('Date')
	eta = fields.Char('ETA')
	delivery_line_ids = fields.One2many('fuel.delivery.detail','fuel_delivery_id','Delivery Details')
	
	@api.onchange('date')
	def onchange_date(self):
		if self.date:
			delivery_detail = []
			for tank in self.env['tank.master'].search([],order='id asc'):
				delivery_detail.append((0, 0, {'tank_id':tank.id,'grade_id':tank.tank_type.id}))
			self.delivery_line_ids = delivery_detail
	
class fuel_delivery_line(models.Model):
	_name = 'fuel.delivery.detail'
	
	tank_id = fields.Many2one('tank.master','Tank')
	grade_id = fields.Many2one('product.product','Grade')
	opening_reading = fields.Float('Opening Reading')
	closing_reading = fields.Float('Closing Reading')
	qty = fields.Float(compute='_get_quantity',string='Quantity')
	fuel_qty = fields.Float('Quantity')
	fuel_delivery_id = fields.Many2one('fuel.delivery','Fuel Delivery')
	
	@api.multi
	@api.depends('opening_reading','closing_reading')
	def _get_quantity(self):
		for fuel in self:
			fuel.qty = fuel.closing_reading - fuel.opening_reading
