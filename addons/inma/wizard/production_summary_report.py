import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

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

class production_summary_report(models.TransientModel):
	_name="production.summary.report"
	
	date_from = fields.Date('From Date')
	date_to = fields.Date('To Date')
	production_summary_ids = fields.One2many('production.summary.line', 'production_summary_id', 'Product Summary')
	file_f = fields.Binary("File", readonly=True)	
	file_name = fields.Char("File Name",size=128, readonly=True)
	
	@api.onchange('date_from','date_to')
	def onchange_date(self):
		if self:
			production_ids = self.env['production.testing.line'].search([('date','>=',self.date_from),('date','<=',self.date_to)])
			production_dict = {}
			production_list = []
			cumalative_left = 0
			cumalative_right = 0
			for production in production_ids:
				if production.mould_id.mould_type == 'l':
					cumalative_left += 1
					production_list.append((0,0,{'rfi_no':production.rfi_no,'date':production.date, 'mould_id':production.mould_id.id,'ring_id_left':production.ring_id,'ring_id_right':'-','ring_produced_left': 1,'ring_produced_right':0,'cumalative_count_left':cumalative_left,'cumalative_count_right':0,'mf_date':production.date,'approved_date':production.approved_date,'dispatched_date':production.dispatched_date,'permanent_ring':production.permanent_ring,'temporary_ring':production.temporary_ring,'approved_ring':production.approved_ring,'dispatched_ring':production.dispatched_ring}))
				elif production.mould_id.mould_type == 'r':
					cumalative_right += 1
					production_list.append((0,0,{'rfi_no':production.rfi_no,'date':production.date, 'mould_id':production.mould_id.id,'ring_id_left':'-','ring_id_right':production.ring_id,'ring_produced_left': 0,'ring_produced_right':1,'cumalative_count_left': 0,'cumalative_count_right': cumalative_right,'mf_date':production.date,'approved_date':production.approved_date,'dispatched_date':production.dispatched_date,'permanent_ring':production.permanent_ring,'temporary_ring':production.temporary_ring,'approved_ring':production.approved_ring,'dispatched_ring':production.dispatched_ring}))
					
			self.production_summary_ids = production_list
			
	@api.multi
	def print_report(self):
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
			fnt.height = 12*0x14
			style_header.font = fnt        
			al1 = Alignment()
			al1.horz = Alignment.HORZ_CENTER
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header.alignment = al1
			style_header.pattern = pat2
			style_header.borders = borders
			pat2.pattern = xlwt.Pattern.SOLID_PATTERN
			pat2.pattern_fore_colour = xlwt.Style.colour_map['light_turquoise']
			style_header.pattern = pat2 
			
			
		
			style_center_align = XFStyle()
			fnt1 = Font()
			fnt1.height = 11*0x14
			al_c = Alignment()
			al_c.horz = Alignment.HORZ_CENTER
			al_c.vert = Alignment.VERT_CENTER
			style_center_align.font = fnt1
			style_center_align.alignment = al_c
			style_center_align.borders = borders
			
			style_center_align1 = XFStyle()
			style_center_align1.borders = borders
			pattern = xlwt.Pattern()
			pattern.pattern = xlwt.Pattern.SOLID_PATTERN
			pattern.pattern_fore_colour = xlwt.Style.colour_map['sky_blue']
			style_center_align1.pattern = pattern 
			
			style_center_align2 = XFStyle()
			style_center_align2.borders = borders
			pattern = xlwt.Pattern()
			pattern.pattern = xlwt.Pattern.SOLID_PATTERN
			pattern.pattern_fore_colour = xlwt.Style.colour_map['violet']
			style_center_align2.pattern = pattern 
			
			style_center_align3 = XFStyle()
			style_center_align3.borders = borders
			pattern = xlwt.Pattern()
			pattern.pattern = xlwt.Pattern.SOLID_PATTERN
			pattern.pattern_fore_colour = xlwt.Style.colour_map['light_green']
			style_center_align3.pattern = pattern 
			
			style_center_align4 = XFStyle()
			fnt1 = Font()
			fnt1.bold = True
			fnt1.height = 11*0x14
			al_c = Alignment()
			al_c.horz = Alignment.HORZ_CENTER
			al_c.vert = Alignment.VERT_CENTER
			style_center_align4.font = fnt1
			style_center_align4.alignment = al_c
			style_center_align4.borders = borders
			pattern = xlwt.Pattern()
			pattern.pattern = xlwt.Pattern.SOLID_PATTERN
			pattern.pattern_fore_colour = xlwt.Style.colour_map['yellow']
			style_center_align4.pattern = pattern 
			
			style_header_center = XFStyle()
			fnt = Font()
			fnt.bold = True
			fnt.height = 11*0x14
			style_header_center.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_CENTER
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header_center.alignment = al1
			style_header_center.pattern = pat2
			style_header_center.borders = borders
			pat2.pattern = xlwt.Pattern.SOLID_PATTERN
			pat2.pattern_fore_colour = xlwt.Style.colour_map['light_turquoise']
			style_header_center.pattern = pat2 
			
			style_header_center1 = XFStyle()
			fnt = Font()
			fnt.bold = True
			fnt.height = 11*0x14
			style_header_center1.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_CENTER
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header_center1.alignment = al1
			style_header_center1.pattern = pat2
			style_header_center1.borders = borders
			
			sheet1 = wbk.add_sheet('Production Summary')
			sheet1.portrait = False
		
			sheet1.col(0).width = 3000
			sheet1.col(1).width = 3000
			sheet1.col(2).width = 2000
			sheet1.col(3).width = 4500
			sheet1.col(4).width = 3500
			sheet1.col(5).width = 3000
			sheet1.col(6).width = 3000
			sheet1.col(7).width = 3000
			sheet1.col(8).width = 5000
			sheet1.col(9).width = 5000
			sheet1.col(10).width = 6000
			sheet1.col(11).width = 6000
			sheet1.col(12).width = 3000
			sheet1.col(13).width = 4000
			sheet1.col(14).width = 5000
			
			sheet1.row(0).height = 400
			row = 1
			sheet1.write_merge(row, row, 0, 14, 'INMA INTERNATIONAL LIMTED - PRODUCTION DETAILS ', style_header)
			row = 2
			sheet1.write_merge(row, row, 0, 14, 'Production Summary', style_header)
			row = 3
			sheet1.write(row, 0, 'RFI NO', style_header_center)
			sheet1.write(row, 1, 'Date', style_header_center)
			sheet1.write(row, 2, 'S.No', style_header_center)
			sheet1.write(row, 3, 'Dispatch Status', style_header_center)
			sheet1.write(row, 4, 'Ring Status', style_header_center)
			sheet1.write(row, 5, 'Mould ID', style_header_center)
			sheet1.write(row, 6, 'Ring ID(L)', style_header_center)
			sheet1.write(row, 7, 'Ring ID(R)', style_header_center)
			sheet1.write(row, 8, 'Ring Produced(L)', style_header_center)
			sheet1.write(row, 9, 'Ring Produced(R)', style_header_center)
			sheet1.write(row, 10, 'Cumalative Count(L)', style_header_center)
			sheet1.write(row, 11, 'Cumalative Count(R)', style_header_center)
			sheet1.write(row, 12, 'MF Date', style_header_center)
			sheet1.write(row, 13, 'Approved Date', style_header_center)
			sheet1.write(row, 14, 'Dispatched Date', style_header_center)
			i = 0
			row = 4
			permanent = 0
			temporary = 0
			approved = 0
			dispatch = 0
			for production in self.production_summary_ids:
				i += 1
				if production.rfi_no:
					sheet1.write(row, 0, production.rfi_no, style_center_align)
				else:
					sheet1.write(row, 0, ' ', style_center_align)
				sheet1.write(row, 1, production.date, style_center_align)
				sheet1.write(row, 2, i, style_center_align)
				if production.dispatched_ring:
					dispatch += 1
					sheet1.write(row, 3, ' ', style_center_align1)
				else:
					sheet1.write(row, 3, ' ', style_center_align)
				if production.permanent_ring:
					permanent += 1
					sheet1.write(row, 4, ' ', style_center_align3)
				elif production.temporary_ring:
					temporary += 1
					sheet1.write(row, 4, 'T', style_center_align4)
				elif production.approved_ring:
					approved += 1
					sheet1.write(row, 4, ' ', style_center_align2)
				else:
					sheet1.write(row, 4, ' ', style_center_align)
				sheet1.write(row, 5, str(production.mould_id.name)+'/'+str((production.mould_id.mould_type)).upper(), style_center_align)
				sheet1.write(row, 6, production.ring_id_left, style_center_align)
				sheet1.write(row, 7, production.ring_id_right, style_center_align)
				sheet1.write(row, 8, production.ring_produced_left, style_center_align)
				sheet1.write(row, 9, production.ring_produced_right, style_center_align)
				sheet1.write(row, 10, production.cumalative_count_left, style_center_align)
				sheet1.write(row, 11, production.cumalative_count_right, style_center_align)
				sheet1.write(row, 12, production.mf_date, style_center_align)
				sheet1.write(row, 13, production.approved_date, style_center_align)
				sheet1.write(row, 14, production.dispatched_date, style_center_align)
				row += 1
			
			sheet1.write_merge(4, 4, 15, 18, 'NOTE', style_header_center1)
			sheet1.write(5, 15, ' ', style_center_align3)
			sheet1.write(6, 15, ' ', style_center_align4)
			sheet1.write(7, 15, ' ', style_center_align2)
			sheet1.write(8, 15, ' ', style_center_align1)
			
			sheet1.write_merge(5, 5, 16, 17, 'PERMANENT RING', style_header_center1)
			sheet1.write_merge(6, 6, 16, 17, 'TEMPORARY RING', style_header_center1)
			sheet1.write_merge(7, 7, 16, 17, 'APPORVED RING', style_header_center1)
			sheet1.write_merge(8, 8, 16, 17, 'DISPATCHED RING', style_header_center1)
			
			sheet1.write(5, 18, permanent, style_center_align)
			sheet1.write(6, 18, temporary, style_center_align)
			sheet1.write(7, 18, approved, style_center_align)
			sheet1.write(8, 18, dispatch, style_center_align)
				
			
			"""Parsing data as string """
			file_data = StringIO.StringIO()
			o=wbk.save(file_data)
			"""string encode of data in wksheet"""
			out = base64.encodestring(file_data.getvalue())
			"""returning the output xls as binary"""
			filename = 'production_summary_report.xls'
			self.write({'file_f':out, 'file_name':filename})
	
			return {

                   'url': '/inma/spreadsheet_report_controller/download_document?model=production.summary.report&field=%s&id=%s&filename=%s'%(self.file_f,self.id,self.file_name),
                   'target': 'new',
                   'type': 'ir.actions.act_url',

                   }
			
		
class production_summary_line(models.TransientModel):
	_name="production.summary.line"
	
	rfi_no = fields.Char("RFI No")
	date = fields.Date("Date")
	mould_id = fields.Many2one("mould.master","Mould ID")
	ring_id_left = fields.Char("Ring ID-L")
	ring_id_right = fields.Char("Ring ID-R")
	ring_produced_left = fields.Integer("Ring Produced-L")
	ring_produced_right = fields.Integer("Ring Produced-R")
	cumalative_count_left = fields.Integer("Cumalative Count-L")
	cumalative_count_right = fields.Integer("Cumalative Count-R")
	permanent_ring = fields.Boolean("Permanant Ring")
	temporary_ring = fields.Boolean("Temporary Ring")
	approved_ring = fields.Boolean("Approved Ring")
	dispatched_ring = fields.Boolean("Dispatched Ring")
	mf_date = fields.Date("MF Date")
	approved_date = fields.Date("Approved Date")
	dispatched_date = fields.Date("Dispatched Date")
	production_summary_id = fields.Many2one('production.summary.report','Production Summary')
