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

class valet_reconciliation(models.Model):
	_name="valet.reconciliation"
	
	date = fields.Date("Date", default = datetime.today())
	shift_id = fields.Many2one('shift.master','Shift')
	valet_ids = fields.One2many('valet.reconciliation.line','valet_id','Valet Reconciliation')
	
	#@api.model
	#def default_get(self, fields):
		#res = super(valet_reconciliation, self).default_get(fields)
		#d = datetime.today() - timedelta(days=1)
		#print d.strftime('%Y-%m-%d')
		#res['date'] = d.strftime('%Y-%m-%d')
		#return res
	
	@api.onchange('date','shift_id')
	def onchange_date(self):
		valet_reconciliation_list = []
		if self.date and self.shift_id: 
			pos_session_list = []
			for pos_session in self.env['pos.session'].search([('shift_id','=',self.shift_id.id)]):
				pos_session_list.append(pos_session.id)
			pos_order_ids = self.env['pos.order'].search([('date_order','>=',self.date),('date_order','<=',self.date),('session_id','in',pos_session_list)])
			pos_order_list = []
			if pos_order_ids:
				for pos_order in pos_order_ids:
					pos_order_list.append(pos_order.id)
				categ_id = self.env['pos.category'].search([('name','=','CAR WASH')])
				for product in self.env['product.product'].search([('pos_categ_id','=',categ_id.id)]):
					product_wise_total = 0
					product_qty = 0
					for line in self.env['pos.order.line'].search([('order_id','in',pos_order_list),('product_id','=',product.id)]):
						if line:
							fpos = line.order_id.fiscal_position_id
							tax_ids_after_fiscal_position = fpos.map_tax(line.tax_ids, line.product_id, line.order_id.partner_id) if fpos else line.tax_ids
							price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
							taxes = tax_ids_after_fiscal_position.compute_all(price, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id, partner=line.order_id.partner_id)
							product_wise_total += taxes['total_included']
							product_qty += line.qty
					
					valet_reconciliation_list.append((0,0, {'product_id':product.id,'description':product.default_code,'retail_price':product.lst_price,'pos_quantity':product_qty,'pos_value':product_wise_total}))
			self.valet_ids = valet_reconciliation_list
				
class valet_reconciliation_line(models.Model):
	_name="valet.reconciliation.line"
	
	product_id = fields.Many2one('product.product','Category')
	description = fields.Char('Description')
	retail_price = fields.Float('Retail Price')
	open_read = fields.Float('Open Read')
	close_read = fields.Float('Close Read')
	meter_sales = fields.Float(compute='_get_meter_sale',string='Meter Sale')
	test_meter = fields.Float('Test Meters')
	net_meter_sale_qty = fields.Float(compute='_get_net_meter_sale',string='Net Metered Sales/Quantity')
	net_meter_sale_value = fields.Float(compute='_get_net_meter_sale_value',string='Net Metered Sales/Value')
	pos_quantity = fields.Float('POS Quantity')
	pos_value = fields.Float('POS Value')
	quantity_variance = fields.Float(compute='_get_quantity_variance',string='Quantity Variance')
	value_variance = fields.Float(compute='_get_value_variance',string='Value Variance')
	notes = fields.Text('Notes')
	valet_id = fields.Many2one('valet.reconciliation','Valet Reconciliation')
	
	@api.multi
	@api.depends('open_read','close_read')
	def _get_meter_sale(self):
		for valet in self:
			valet.meter_sales = valet.close_read - valet.open_read
			
	@api.multi
	@api.depends('meter_sales','test_meter')
	def _get_net_meter_sale(self):
		for valet in self:
			valet.net_meter_sale_qty = valet.test_meter + valet.meter_sales
			
	@api.multi
	@api.depends('net_meter_sale_qty','retail_price')
	def _get_net_meter_sale_value(self):
		for valet in self:
			valet.net_meter_sale_value = valet.net_meter_sale_qty * valet.retail_price

	@api.multi
	@api.depends('pos_quantity','net_meter_sale_qty')
	def _get_quantity_variance(self):
		for valet in self:
			valet.quantity_variance = valet.net_meter_sale_qty - valet.pos_quantity
			
	@api.multi
	@api.depends('net_meter_sale_value','pos_value')
	def _get_value_variance(self):
		for valet in self:
			valet.value_variance = valet.net_meter_sale_value - valet.pos_value
