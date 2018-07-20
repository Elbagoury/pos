import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

class vendor_list_report(models.TransientModel):
	_name="vendor.list.report"
	
	category = fields.Selection([('city_wise', 'City Wise'), ('product_wise','Product Wise'),('vendor_wise','Vendor Wise')], 'Category')
	city_id = fields.Many2one('res.city','City')
	product_id = fields.Many2one('product.product','Product')
	vendor_id = fields.Many2one('res.partner','Vendor')
	vendor_list_ids = fields.One2many('vendor.list.line', 'vendor_list_report_id', 'Vendor List')
	
	@api.onchange('category','city_id','product_id','vendor_id')
	def onchange_category(self):
		if self.category:
			vendor_list = []
			if self.city_id and self.category == 'city_wise':
				vendor_ids = self.env['res.partner'].search([('supplier','=','True'),('city_id','=',self.city_id.id)])
				for vendor in vendor_ids:
					vendor_list.append((0, 0, {'vendor_id': vendor.id}))

			elif self.product_id and self.category == 'product_wise':
				for seller in self.product_id.vendor_list_id:
					vendor_list.append((0, 0, {'vendor_id': seller.vendor_id.id}))
					
			elif self.vendor_id and self.category == 'vendor_wise':
				vendor_ids = self.env['vendor.list'].search([('vendor_id', '=', self.vendor_id.id)])
				for vendor in vendor_ids:
					product_ids = self.env['product.product'].search([('product_tmpl_id','=',vendor.product_id.id)])
					for product in product_ids:
						vendor_list.append((0, 0, {'vendor_id': vendor.vendor_id.id, 'product_id':product.id}))
			self.vendor_list_ids = vendor_list

class vendor_list_line(models.TransientModel):
	_name="vendor.list.line"
	
	vendor_id = fields.Many2one('res.partner','Vendor Name')
	product_id = fields.Many2one('product.product','Product')
	vendor_list_report_id = fields.Many2one('vendor.list.report', 'Vendor List Report')
