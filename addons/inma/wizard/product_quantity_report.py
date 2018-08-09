import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

from datetime import datetime, date, time, timedelta
import time

import base64
import sys
import os

import StringIO
import base64
from xlwt import *
from __builtin__ import True
from email import _name

try:
    import cStringIO as StringIO
    import xlwt
except:
    raise osv.except_osv('Warning !','python-xlwt module missing. Please install it.')

class product_category_report(models.TransientModel):
	_name="product.category.report"
	
	category = fields.Selection([('all', 'All')], 'Category',default='all')
	product_id = fields.Many2one('product.product','Product')
	product_quantity_ids = fields.One2many('product.quantity.report', 'product_category_report_id', 'Product Details')
	file_f = fields.Binary("File", readonly=True)	
	file_name = fields.Char("File Name",size=128, readonly=True)    
	
	@api.onchange('category', 'product_id')
	def on_change_category(self):
		if self.category == 'all':
			product_quant = []
			for product in self.env['product.product'].search([]):
				reorder_rule = self.env['stock.warehouse.orderpoint'].search([('product_id','=',product.id)])
				if product.qty_available < reorder_rule.product_min_qty:
					product_quant.append((0, 0, {'product_name': product.name,'product_attribute':product.attribute_value_ids.id,'unit_id':product.uom_id.id,'qty_avail': product.qty_available}))
				#product_quant.append((0, 0, {'product_id': product.id, 'qty_avail': product.qty_available}))
			
			self.product_quantity_ids = product_quant
		
		#if 	self.category =='particular':	
			#if self.product_id:
				#product_quant = []
				#product_quant.append((0, 0, {'product_name': self.product_id.name,'product_attribute':self.product_id.attribute_value_ids.id,'unit_id':self.product_id.uom_id.id,'qty_avail': self.product_id.qty_available}))
				
				#self.product_quantity_ids = product_quant
				
	#@api.multi
	#def create_srm(self):
		#if self.product_quantity_ids:
			
			#srm_id = self.env['stock.requirement.memo'].create({'date':datetime.now().strftime('%Y-%m-%d')})
			#srm_line = self.env['stock.requirement.product']
			#srm_line_dict = {}
			#for product in self.env['product.product'].search([]):
				#reorder_rule = self.env['stock.warehouse.orderpoint'].search([('product_id','=',product.id)])
				#if product.qty_available < reorder_rule.product_min_qty:
					#srm_line.create({'stock_requirement_memo_id':srm_id.id,'product_temp_id':product.product_tmpl_id.id,'product_id':product.id,'product_code_no':product.inma_code_no,'unit':product.uom_id.id,'current_stock':product.qty_available})
			
				
	@api.multi
	def print_report(self):
		if self.category:
			wbk = xlwt.Workbook()
			borders = xlwt.Borders()
			borders.left = xlwt.Borders.THIN
			borders.right = xlwt.Borders.THIN
			borders.top = xlwt.Borders.THIN
			borders.bottom = xlwt.Borders.THIN
			
			style_header = XFStyle()
			fnt = Font()
			fnt.bold = True
			fnt.height = 12*0x14
			style_header.font = fnt        
			al1 = Alignment()
			al1.horz = Alignment.HORZ_CENTER
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header.alignment = al1
			style_header.pattern = pat2
			style_header.borders = borders
			
			style_header_without_border = XFStyle()        
			fnt = Font()
			fnt.bold = True
			fnt.height = 12*0x14
			style_header_without_border.font = fnt        
			al1 = Alignment()
			al1.horz = Alignment.HORZ_CENTER
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()        
			style_header_without_border.alignment = al1
			style_header_without_border.pattern = pat2
			
			style_header1 = XFStyle()
			fnt = Font()
			fnt.bold = True
			fnt.height = 16*0x16
			style_header1.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_CENTER
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header1.alignment = al1
			style_header1.pattern = pat2
			style_header1.borders = borders
			
			
			style_header_right = XFStyle()
			fnt = Font()
			fnt.bold = True
			fnt.height = 11*0x14
			style_header_right.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_RIGHT
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header_right.alignment = al1
			style_header_right.pattern = pat2
			style_header_right.borders = borders
			
			style_header_left = XFStyle()
			fnt = Font()
			fnt.bold = True
			fnt.height = 11*0x14
			style_header_left.font = fnt
			style_header_left.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_LEFT
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header_left.alignment = al1
			style_header_left.pattern = pat2
			style_header_left.borders = borders
			
			
			style_header_left1 = XFStyle()
			fnt = Font()
			fnt.height = 11*0x14
			style_header_left1.font = fnt
			style_header_left1.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_LEFT
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header_left1.alignment = al1
			style_header_left1.pattern = pat2
			style_header_left1.borders = borders

			
			style_right_align = XFStyle()
			al_r = Alignment()
			al_r.horz = Alignment.HORZ_RIGHT
			al_r.vert = Alignment.VERT_CENTER
			style_right_align.alignment = al_r
			style_right_align.num_format_str = "0.00"
			style_right_align.borders = borders
			
			style_right_align_2 = XFStyle()
			style_right_align_2.alignment = al_r
			style_right_align_2.borders = borders
			
			style_center_align = XFStyle()
			al_c = Alignment()
			al_c.horz = Alignment.HORZ_CENTER
			al_c.vert = Alignment.VERT_CENTER
			style_center_align.alignment = al_c
			style_center_align.borders = borders
			
			style_center_align2 = XFStyle()
			fnt1 = Font()
			fnt1.bold = True
			fnt1.height = 11*0x14
			al_c = Alignment()
			al_c.horz = Alignment.HORZ_CENTER
			al_c.vert = Alignment.VERT_CENTER
			style_center_align2.font = fnt1
			style_center_align2.alignment = al_c
			
			style_left_align = XFStyle()
			al_l = Alignment()
			al_l.horz = Alignment.HORZ_LEFT
			al_l.vert = Alignment.VERT_CENTER
			style_left_align.alignment = al_l
			style_left_align.borders = borders
			
			sheet1 = wbk.add_sheet('CONSUMABLES STOCK REPORT')
			sheet1.portrait = False
			sheet1.col(0).width = 2000
			sheet1.col(1).width = 8000
			sheet1.col(2).width = 10000
			sheet1.col(3).width = 3000
			sheet1.col(4).width = 5000
			sheet1.col(5).width = 5000
			
			sheet1.row(0).height = 1600
			sheet1.row(1).height = 400
			sheet1.row(2).height = 400
			sheet1.row(3).height = 400
			sheet1.row(4).height = 400
			sheet1.row(5).height = 900
			row = 0
			sheet1.write_merge(row, row, 1, 4, 'CONSUMABLES STOCK REPORT', style_header1)
			row = 1
			sheet1.write(row, 0,  'Sr.No', style_header_left)			
			sheet1.write(row, 1,  'CONSUMABLES', style_header_left)
			sheet1.write(row, 2,  'Description', style_header_left)
			sheet1.write(row, 3,  'Unit', style_header_left)
			sheet1.write(row, 4,  'Quantity Available', style_header_left)
			sheet1.write(row, 5,  'Remarks', style_header_left)

			
			i = 0
			row = 2

			for product in self:
				for product_quantity in product.product_quantity_ids:					
					i = i+1
					sheet1.write(row, 0, i, style_header_left1)
					sheet1.write(row, 1, product_quantity.product_name, style_header_left1)
					if product_quantity.product_attribute:
						sheet1.write(row, 2, str(product_quantity.product_attribute.attribute_id.name)+":" + str(product_quantity.product_attribute.name) , style_header_left1)
					else:
						sheet1.write(row, 2, " " , style_header_left1)

					sheet1.write(row, 3, product_quantity.unit_id.name, style_header_left1)
					sheet1.write(row, 4, product_quantity.qty_avail, style_header_left1)
					if product_quantity.remarks:
						sheet1.write(row, 5, product_quantity.remarks, style_header_left1)
					else:
						sheet1.write(row, 5, ' ', style_header_left1)
					
					row += 1    
							
					
            			
			"""Parsing data as string """
			file_data = StringIO.StringIO()
			o=wbk.save(file_data)
			"""string encode of data in wksheet"""
			out = base64.encodestring(file_data.getvalue())
			"""returning the output xls as binary"""
			filename = 'conusmable_report.xls'
			self.write({'file_f':out, 'file_name':filename})
			return {

                   'url': '/inma/spreadsheet_report_controller/download_document?model=product.category.report&field=%s&id=%s&filename=%s'%(self.file_f,self.id,self.file_name),
                   'target': 'new',
                   'type': 'ir.actions.act_url',

                   }
		#else:
			#warning = {
                      #'title': _('Warning!'),
                      #'message': _('Fill all mandatory fields before attempting to generate report!')
                       #}
			#return {'warning': warning}
            
		
class product_quantity_report(models.TransientModel):
	_name="product.quantity.report"
	
	product_name = fields.Char('Consumables Product')
	product_attribute = fields.Many2one('product.attribute.value', 'Description')
	unit_id = fields.Many2one('product.uom','Unit')
	qty_avail = fields.Float('Quantity Available')
	remarks = fields.Char('Remarks')
	product_category_report_id = fields.Many2one('product.category.report', 'Product Quantity Report')
	
class product_stock(models.TransientModel):
	_name="product.stock"
	
	date = fields.Date('Stock Date')
	product_types = fields.Selection([('consume','Cosumable'),('stockable','Stockable')], 'Product Type')
	product_stock_line_ids = fields.One2many('product.stock.line', 'product_stock_id', 'Product Details')
	file_f = fields.Binary("File", readonly=True)	
	file_name = fields.Char("File Name",size=128, readonly=True)   

	@api.onchange('date', 'product_types')
	def onchange_date(self):
		if self.date and self.product_types:
			product_stock = []
			self.env.cr.execute("""SELECT product_id as product_id,SUM(quantity) as quantity FROM stock_history where date::date <= %s and product_type = %s GROUP BY product_id""",(self.date,self.product_types))
			for stock_dict in self.env.cr.dictfetchall():
				#print stock_dict['product_id'], stock_dict['quantity']
				product_stock.append((0, 0, {'product_id': stock_dict['product_id'],'qty_avail': stock_dict['quantity']}))
			self.product_stock_line_ids = product_stock
	
	@api.multi
	def print_report(self):
		if self.date:
			wbk = xlwt.Workbook()
			borders = xlwt.Borders()
			borders.left = xlwt.Borders.THIN
			borders.right = xlwt.Borders.THIN
			borders.top = xlwt.Borders.THIN
			borders.bottom = xlwt.Borders.THIN
			
			style_header1 = XFStyle()
			fnt = Font()
			fnt.bold = True
			fnt.height = 16*0x16
			style_header1.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_CENTER
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header1.alignment = al1
			style_header1.pattern = pat2
			style_header1.borders = borders

			style_header_left = XFStyle()
			fnt = Font()
			fnt.bold = True
			fnt.height = 11*0x14
			style_header_left.font = fnt
			style_header_left.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_LEFT
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header_left.alignment = al1
			style_header_left.pattern = pat2
			style_header_left.borders = borders
			
			style_header_left1 = XFStyle()
			fnt = Font()
			fnt.height = 11*0x14
			style_header_left1.font = fnt
			style_header_left1.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_LEFT
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header_left1.alignment = al1
			style_header_left1.pattern = pat2
			style_header_left1.borders = borders

			style_header_right1 = XFStyle()
			fnt = Font()
			fnt.height = 11*0x14
			style_header_right1.font = fnt
			style_header_right1.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_RIGHT
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header_right1.alignment = al1
			style_header_right1.pattern = pat2
			style_header_right1.borders = borders
			
			sheet1 = wbk.add_sheet('Consumable Stock Report - (Date/Period)')
			sheet1.portrait = False
			sheet1.col(0).width = 3000
			sheet1.col(1).width = 10000
			sheet1.col(2).width = 3000
		
			sheet1.row(0).height = 1600
			sheet1.row(1).height = 400
			
			row = 0
			sheet1.write_merge(row, row, 1, 4, 'Consumable Stock Report - (Date/Period)', style_header1)
			row = 1
			sheet1.write(row, 0,  'Sr.No', style_header_left)			
			sheet1.write_merge(row, row, 1, 2,  'Consumable Product', style_header_left)
			sheet1.write_merge(row, row, 3, 4, 'Quantity Available', style_header_left)
			
			i = 0
			row = 2

			for product in self:
				for product_stock in product.product_stock_line_ids:					
					i = i+1
					sheet1.write(row, 0, i, style_header_left1)
					sheet1.write_merge(row, row, 1, 2, product_stock.product_id.name, style_header_left1)
					sheet1.write_merge(row, row, 3, 4, product_stock.qty_avail, style_header_right1)
					
					row += 1    
										
			"""Parsing data as string """
			file_data = StringIO.StringIO()
			o=wbk.save(file_data)
			"""string encode of data in wksheet"""
			out = base64.encodestring(file_data.getvalue())
			"""returning the output xls as binary"""
			filename = 'conusmable_report.xls'
			self.write({'file_f':out, 'file_name':filename})
			return {
                   'url': '/inma/spreadsheet_report_controller/download_document?model=product.stock&field=%s&id=%s&filename=%s'%(self.file_f,self.id,self.file_name),
                   'target': 'new',
                   'type': 'ir.actions.act_url',
                   }
			
class product_stock_line(models.TransientModel):
	_name="product.stock.line"
	
	product_id = fields.Many2one('product.product','Consumables Product')
	qty_avail = fields.Float('Quantity Available')
	product_stock_id = fields.Many2one('product.stock', 'Product Stock Report')

