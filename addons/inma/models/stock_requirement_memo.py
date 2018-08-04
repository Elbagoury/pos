import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

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

class stock_requirement_memo(models.Model):
	_name="stock.requirement.memo"
	_inherit = ['mail.thread']


	project_id = fields.Many2one('project.name','Project')
	date = fields.Date('Date', default = fields.Date.context_today)
	name = fields.Char('SRM No')
	project_srm_no = fields.Integer('Project SRM No')
	delivery_date = fields.Date('Expected Delivery Date')
	stock_requirement_product_ids = fields.One2many('stock.requirement.product', 'stock_requirement_memo_id','Stock Product')
	file_f = fields.Binary("File", readonly=True)
	file_name = fields.Char("File Name",size=128, readonly=True)
	state = fields.Selection([('confirm','Confirm')], 'State')
	partner_id = fields.Many2one('res.partner','Mail User')
	cc_user = fields.Many2many('res.users','mail_user_rel','uid','srmid','CC User' )
	from_csr = fields.Boolean('From CSR')

	@api.onchange('project_id')
	def onchange_project_id(self):
		if self.project_id:
			stock_requirement_id = self.env['stock.requirement.memo'].search([('project_id','=',self.project_id.id)],order='project_srm_no desc', limit=1) 
			self.project_srm_no = stock_requirement_id.project_srm_no + 1
			self.name = str(self.project_id.code) +'/'+ str(stock_requirement_id.project_srm_no + 1)

	@api.one
	@api.constrains('stock_requirement_product_ids')
	def constraint_stock_requirement_product(self):
		if self.stock_requirement_product_ids:
			return True
		else:
			raise ValidationError(_("Enter Stock Requirement Product"))
			
	@api.onchange('from_csr')
	def create_srm(self):
		srm_line_list = []
		if self.from_csr:
			srm_line_list = []
			for product in self.env['product.product'].search([]):
				reorder_rule = self.env['stock.warehouse.orderpoint'].search([('product_id','=',product.id)])
				if product.qty_available < reorder_rule.product_min_qty:
					srm_line_list.append((0,0, {'product_temp_id':product.product_tmpl_id.id,'specification':product.product_tmpl_id.specification,'product_code_no':product.product_tmpl_id.inma_code_no,'unit':product.product_tmpl_id.uom_id.id,'current_stock':product.product_tmpl_id.qty_available}))
			self.stock_requirement_product_ids = srm_line_list
		else:
			self.stock_requirement_product_ids = srm_line_list

	@api.multi
	def print_report(self):
		if self.project_id and self.stock_requirement_product_ids:
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
			fnt.bold = True
			fnt.height = 11*0x14
			style_header_left.font = fnt
			style_header_left.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_LEFT
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header_left1.alignment = al1
			style_header_left1.pattern = pat2

			style_header_left2 = XFStyle()
			fnt = Font()
			fnt.height = 11*0x14
			style_header_left.font = fnt
			style_header_left.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_LEFT
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header_left2.alignment = al1
			style_header_left2.pattern = pat2
			style_header_left2.borders = borders

			style_center_align = XFStyle()
			fnt1 = Font()
			fnt1.bold = True
			fnt1.height = 11*0x14
			al_c = Alignment()
			al_c.horz = Alignment.HORZ_CENTER
			al_c.vert = Alignment.VERT_CENTER
			style_center_align.font = fnt1
			style_center_align.alignment = al_c

			style_center_align1 = XFStyle()
			fnt1 = Font()
			fnt1.bold = True
			fnt1.height = 11*0x14
			al_c = Alignment()
			al_c.horz = Alignment.HORZ_CENTER
			al_c.vert = Alignment.VERT_CENTER
			style_center_align1.font = fnt1
			style_center_align1.alignment = al_c
			style_center_align1.borders = borders

			sheet1 = wbk.add_sheet('Stock Requirement Memo')
			sheet1.portrait = False

			sheet1.col(0).width = 2000
			sheet1.col(1).width = 3000
			sheet1.col(2).width = 3000
			sheet1.col(3).width = 3000
			sheet1.col(4).width = 3000
			sheet1.col(5).width = 3000
			sheet1.col(6).width = 3000
			sheet1.col(7).width = 3000
			sheet1.col(8).width = 3000
			sheet1.col(9).width = 3000

			sheet1.row(0).height = 400
			row = 0
			sheet1.write_merge(row, row, 0, 9, 'Stock Requirement Memo', style_header)
			row = 1
			sheet1.write_merge(row, row, 0, 9, 'INMA INTERNATIONAL LTD', style_header)
			row = 2
			sheet1.write_merge(row, 5, 0, 4, 'To\n The Project Director, IIL\n Head Office, Chennai - 600086', style_header_left2)
			sheet1.write_merge(row, row, 5, 6, 'Project', style_header_left2)
			sheet1.write_merge(row, row, 7, 9, self.project_id.name, style_header_left2)
			row = 3
			sheet1.write_merge(row, row, 5, 6, 'Date', style_header_left2)
			sheet1.write_merge(row, row, 7, 9, self.date, style_header_left2)
			row = 4
			sheet1.write_merge(row, row, 5, 6, 'Project SRM No', style_header_left2)
			sheet1.write_merge(row, row, 7, 9, self.name, style_header_left2)
			row = 5
			sheet1.write_merge(row, row, 5, 6, 'Expected Date', style_header_left2)
			sheet1.write_merge(row, row, 7, 9, self.delivery_date, style_header_left2)
			row = 6
			sheet1.write_merge(row, row, 0, 9, 'Please send the following on / before', style_header_left2)

			i = 0
			row = 7
			sheet1.write(row, 0, 'S.No', style_center_align1)
			sheet1.write_merge(row, row, 1, 4, 'Product', style_center_align1)
			sheet1.write_merge(row, row, 5,8, 'Specification', style_center_align1)
			sheet1.write(row, 9, 'Qty', style_center_align1)
			row = 8
			for stock_product in self.stock_requirement_product_ids:
				i += 1
				sheet1.write(row, 0, i, style_header_left2)
				sheet1.write_merge(row, row, 1, 4, stock_product.product_temp_id.name, style_header_left2)
				if stock_product.product_temp_id.specification:
					sheet1.write_merge(row, row, 5, 8, stock_product.specification, style_header_left2)
				else:
					sheet1.write_merge(row, row, 5, 8, ' ', style_header_left2)
				#if stock_product.product_id.attribute_value_ids:
					#sheet1.write_merge(row, row, 1, 4, stock_product.product_id.name+'-'+stock_product.product_id.attribute_value_ids.attribute_id.name+':'+stock_product.product_id.attribute_value_ids.name, style_header_left2)
				#else:
					#sheet1.write_merge(row, row, 1, 4, stock_product.product_id.name, style_header_left2)
				#sheet1.write_merge(row, row, 5, 8, stock_product.specification, style_header_left2)
				sheet1.write(row, 9, stock_product.quantity, style_header_left2)
				row += 1
			row = row
			for i in range(row+4):

				sheet1.write(row, 0, ' ', style_header_left2)
				sheet1.write_merge(row, row, 1, 4, ' ', style_header_left2)
				sheet1.write_merge(row, row, 5, 8, ' ', style_header_left2)
				sheet1.write(row, 9, ' ', style_header_left2)
				row += 1
			row = row
			sheet1.write_merge(row, row, 0, 9, 'For Inma International Ltd.', style_header_left1)
			row += 8
			sheet1.row(row).height = 600
			sheet1.write_merge(row, row, 0, 1, 'Store Incharge', style_center_align)
			sheet1.write_merge(row, row, 2, 3, 'Site Engineer', style_center_align)
			sheet1.write_merge(row, row, 4, 5, 'Project Manager', style_center_align)
			sheet1.write_merge(row, row, 6, 7, 'Purchase\nIn-charge', style_center_align)
			sheet1.write_merge(row, row, 8, 9, 'Approved by\nDirector - HO', style_center_align)

			"""Parsing data as string """
			file_data = StringIO.StringIO()
			o=wbk.save(file_data)
			"""string encode of data in wksheet"""
			out = base64.encodestring(file_data.getvalue())
			"""returning the output xls as binary"""
			filename = 'stock_requirement_report.xls'
			self.write({'file_f':out, 'file_name':filename})
			return {

                   'url': '/inma/spreadsheet_report_controller/download_document?model=stock.requirement.memo&field=%s&id=%s&filename=%s'%(self.file_f,self.id,self.file_name),
                   'target': 'new',
                   'type': 'ir.actions.act_url',
                   }

	@api.multi
	def confirm(self):
		action_id = self.env['ir.actions.act_window'].search([('name', '=', 'Requests for Quotation')], limit=1).id
		menu_id = self.env['ir.ui.menu'].search([('name', '=', 'Requests for Quotation')], limit=1).id
		server_url = 'http://184.95.34.90:8061/web?#&view_type=form&model=purchase.order&menu_id=%s&action=%s'%(menu_id,action_id)
		body = "Click on the following link to"+ "<a href =\"%s\"> Create Purchase Order</a>"% server_url
		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		try:
			template_id = ir_model_data.get_object_reference('inma', 'email_template_send_srm')[1]
		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False
		if template_id:
			self.env['mail.template'].browse(template_id).write({
	 					'body_html':body,
					 })
					
		ctx = dict(self.env.context or {})
		ctx.update({
            'default_model': 'stock.requirement.memo',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })

		return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

	# @api.multi
	# def confirm(self):
	# 	if self:
	# 		#if self.cc_user:
	# 			#cc_mail = []
	# 			#for user in self.cc_user:
	# 				#cc_mail.append(user.email)
	# 		user_id = self.env['res.users'].search([('id','=',self.env.uid)])
	# 		action_id = self.env['ir.actions.act_window'].search([('name', '=', 'Requests for Quotation')], limit=1).id
	# 		menu_id = self.env['ir.ui.menu'].search([('name', '=', 'Requests for Quotation')], limit=1).id
	# 		server_url = 'http://184.95.34.90:8061/web?#&view_type=form&model=purchase.order&menu_id=%s&action=%s'%(menu_id,action_id)
	# 		#print server_url , base_url
	# 		template = self.env['ir.model.data'].get_object_reference('inma', 'email_template_send_srm')[1]
	# 		subject = 'SRM Request'
	# 		body = "Click on the following link to"+ "<a href =\"%s\"> Create Purchase Order</a>"% server_url
	# 		if self.partner_id and template:
	# 			self.env['mail.template'].browse(template).write({
	# 					'email_from':user_id.login,
	# 					'email_to':self.partner_id.email,
	# 					#'email_cc':cc_mail,
	# 					'subject':subject,
	# 					'body_html':body,
	# 				 })
	# 			self.env['mail.template'].browse(template).send_mail(self.id,force_send=True)
				
				

class stock_requirement_product(models.Model):
	_name="stock.requirement.product"
	
	product_temp_id = fields.Many2one('product.template','Product')
	specification = fields.Char('Specification')
	product_code_no = fields.Char('Code No')
	unit = fields.Many2one('product.uom','unit')
	current_stock = fields.Float('Current Stock')
	quantity = fields.Float('Required qty')
	stock_requirement_memo_id = fields.Many2one('stock.requirement.memo','Stock Requirement Memo')

	@api.onchange('product_temp_id')
	def onchange_product_temp_id(self):
		if self.product_temp_id:
			self.specification = self.product_temp_id.specification
			self.product_code_no = self.product_temp_id.inma_code_no
			self.unit = self.product_temp_id.uom_id.id
			self.current_stock = self.product_temp_id.qty_available

	# @api.onchange('product_temp_id')
	# def onchange_product_temp_id(self):
	# 	if self.product_temp_id:
	# 		product_ids = self.env['product.product'].search([('product_tmpl_id','=',self.product_temp_id.id)])
	# 		domain ={}
	# 		product_values = []
	# 		for product in product_ids:
	# 			if product.attribute_value_ids:
	# 				product_values.append(product.id)
	# 			else:
	# 				self.product_code_no = product.inma_code_no
	# 				self.unit = product.uom_id.id
	# 				self.current_stock = product.qty_available
	# 		domain['product_id'] = [('id', 'in', product_values)]
	# 		return {'domain': domain} 
	
	# @api.onchange('product_id')
	# def onchange_product_id(self):
	# 	if self.product_id:
	# 		self.product_code_no = self.product_id.inma_code_no
	# 		self.unit = self.product_id.uom_id.id
	# 		self.current_stock = self.product_id.qty_available
			
class project_name(models.Model):
	_name = "project.name"
	
	name = fields.Char('Project Name', size=64)
	year = fields.Date('year')
	code = fields.Char('Project Code', size=6)
	address = fields.Text("Address")
	upload = fields.Binary("Upload")
	
	_sql_constraints = [
        ('name_code_uniq', 'unique (name,code)',
            'Name and code must be unique !')
    ]
	
	@api.model
	def create(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(project_name, self).create(vals)
	
	@api.one
	@api.constrains('name')
	def _check_name_constraints(self):
		if self.name:
			name = self.name.strip()
			self.env.cr.execute('''select count(id) as count from project_name where LOWER(name) = LOWER(%s)''',((name),))
			for name_id in self.env.cr.dictfetchall():
				name_count = name_id['count']
				if name_count > 1:
					raise ValidationError(_("Already Exist"))
					
	@api.multi
	def write(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(project_name, self).write(vals)

