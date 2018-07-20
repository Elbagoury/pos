from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource
from odoo import tools, _

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

class good_issue_slip(models.Model):
	_name='good.issue.slip'

	date = fields.Date("Date")
	purpose_issue = fields.Selection([('internal','Internal'),('sale','Sale')], 'Purpose of Issue')
	issue_name_id = fields.Many2one('hr.employee','Name of Issue')
	issuing_authority = fields.Many2one('hr.job','Issuing Authority')
	employee_id = fields.Many2one('hr.employee','Employee name')
	employee_id_no	= fields.Char('Employee ID')
	good_issue_slip_line_ids = fields.One2many('good.issue.slip.line','good_issue_slip_id','Items')
	file_f = fields.Binary("File", readonly=True)
	file_name = fields.Char("File Name",size=128, readonly=True)

	@api.onchange('issue_name_id','employee_id')
	def onchange_issue_name_id(self):
		if self.issue_name_id:
			self.issuing_authority = self.issue_name_id.job_appointed_id.id
		if self.employee_id:
			self.employee_id_no = self.employee_id.cid

	@api.multi
	def button_print(self):
		if self:
			wbk = xlwt.Workbook()
			borders = xlwt.Borders()
			borders.left = xlwt.Borders.THIN
			borders.right = xlwt.Borders.THIN
			borders.top = xlwt.Borders.THIN
			borders.bottom = xlwt.Borders.THIN

			style_header = XFStyle()
			fnt = Font()
			fnt.bold = True
			fnt.height = 18*0x16
			style_header.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_CENTER
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header.alignment = al1
			style_header.pattern = pat2
			style_header.borders = borders

			style_header1 = XFStyle()
			fnt = Font()
			fnt.bold = True
			fnt.height = 12*0x14
			style_header1.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_CENTER
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header1.alignment = al1
			style_header1.pattern = pat2
			style_header1.borders = borders

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

			style_header_center = XFStyle()
			fnt = Font()
			fnt.height = 11*0x14
			style_header_center.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_LEFT
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header_center.alignment = al1
			style_header_center.pattern = pat2
			style_header_center.borders = borders

			style_center_align = XFStyle()
			al_c = Alignment()
			al_c.horz = Alignment.HORZ_CENTER
			al_c.vert = Alignment.VERT_CENTER
			style_center_align.alignment = al_c
			style_center_align.borders = borders

			sheet1 = wbk.add_sheet('Good Issue Slip')
			sheet1.portrait = False
			sheet1.col(0).width = 4000
			sheet1.col(1).width = 7000
			sheet1.col(2).width = 10000
			sheet1.col(3).width = 4000
			sheet1.col(4).width = 4000
			sheet1.col(5).width = 4000

			sheet1.row(0).height = 400
			sheet1.row(1).height = 300
			sheet1.row(2).height = 300
			sheet1.row(3).height = 400
			sheet1.row(4).height = 400
			sheet1.row(5).height = 400

			row = 0
			sheet1.write_merge(row, row, 0, 5, 'INMA INTERNATIONAL LIMITED', style_header)
			row = 1
			sheet1.write_merge(row, row, 0, 5, 'GOOD ISSUE SLIP', style_header1)
			row = 2
			sheet1.write_merge(row, row, 0, 1, 'Date of Issue', style_header1)
			sheet1.write(row, 2, self.date, style_header_center)
			sheet1.write_merge(row, row, 3, 4, 'Purpose of Issue Internal/Sale: ', style_header1)
			sheet1.write(row, 5, self.purpose_issue, style_header_center)
			row = 3
			sheet1.write_merge(row, row, 0, 1, 'Name of Issuee', style_header1)
			sheet1.write(row, 2, self.issue_name_id.name, style_header_center)
			sheet1.write_merge(row, row, 3, 4, 'Issuing Authority', style_header1)
			sheet1.write(row, 5, self.issuing_authority.name, style_header_center)
			row = 4
			sheet1.write_merge(row, row, 0, 1, 'Employee Name', style_header1)
			sheet1.write(row, 2, self.employee_id.name, style_header_center)
			sheet1.write_merge(row, row, 3, 4, 'Employee ID', style_header1)
			sheet1.write(row, 5, self.employee_id_no, style_header_center)
			row = 5
			sheet1.write(row, 0, 'S.No', style_header1)
			sheet1.write(row, 1, 'Item Code no', style_header1)
			sheet1.write(row, 2, 'Item Description', style_header1)
			sheet1.write(row, 3, 'Unit', style_header1)
			sheet1.write(row, 4, 'Quantity', style_header1)
			sheet1.write(row, 5, 'Remarks', style_header1)
			row = 6
			i = 0
			for issue_line in self.good_issue_slip_line_ids:
				i += 1
				sheet1.row(row).height = 400
				sheet1.write(row, 0, i, style_center_align)
				sheet1.write(row, 1, issue_line.item_code, style_center_align)
				sheet1.write(row, 2, issue_line.item_id.name, style_center_align)
				sheet1.write(row, 3, issue_line.unit_id.name, style_center_align)
				sheet1.write(row, 4, issue_line.qty, style_center_align)
				sheet1.write(row, 5, issue_line.remarks, style_center_align)
				row += 1
			row = row
			for i in range(row-3):
				sheet1.row(row).height = 400
				sheet1.write(row, 0, ' ', style_center_align)
				sheet1.write(row, 1,  ' ', style_center_align)
				sheet1.write(row, 2,  ' ', style_center_align)
				sheet1.write(row, 3,  ' ', style_center_align)
				sheet1.write(row, 4,  ' ', style_center_align)
				sheet1.write(row, 5,  ' ', style_center_align)
				row += 1

			row = row + 2
			sheet1.write(row, 0, 'Sign:', style_header_without_border)
			row += 1
			sheet1.write(row, 1, 'Issuer', style_header_without_border)
			sheet1.write(row, 4, 'Issuee', style_header_without_border)

			"""Parsing data as string """
			file_data = StringIO.StringIO()
			o=wbk.save(file_data)
			"""string encode of data in wksheet"""
			out = base64.encodestring(file_data.getvalue())
			"""returning the output xls as binary"""
			filename = 'good_issue_slip.xls'
			self.write({'file_f':out, 'file_name':filename})
			return {

                   'url': '/inma/spreadsheet_report_controller/download_document?model=good.issue.slip&field=%s&id=%s&filename=%s'%(self.file_f,self.id,self.file_name),
                   'target': 'new',
                   'type': 'ir.actions.act_url',

                   }

class good_issue_slip_line(models.Model):
	_name='good.issue.slip.line'

	item_code = fields.Char('Item Code')
	item_id = fields.Many2one('product.product', 'Item Discription')
	unit_id = fields.Many2one('product.uom', 'unit')
	qty = fields.Float('Quantity')
	remarks = fields.Text('Remarks')
	good_issue_slip_id = fields.Many2one('good.issue.slip','Good Issue Slip')

	@api.onchange('item_code')
	def onchange_item_Code(self):
		if self.item_code:
			product_id = self.env['product.product'].search([('inma_code_no','=',self.item_code)])
			self.item_id = product_id.id
			self.unit_id = product_id.uom_po_id.id
