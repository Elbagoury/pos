import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError

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

class assert_report(models.TransientModel):
    _name = 'assert.report'

    filter_by = fields.Selection([('all','All'),('state','State')],'Filter By')
    location = fields.Many2one('bt.asset.location','Location')
    state = fields.Selection([('active', 'Active'),
            ('scrapped', 'Scrapped'), ('inactive','In Active'),('repair','Under Repair'),('maintenance','Under Maintenance')], 'State')
    asset_ids = fields.One2many('assert.report.line','asset_id','Assets')
    file_f = fields.Binary("File", readonly=True)
    file_name = fields.Char("File Name",size=128, readonly=True)

    @api.onchange('filter_by','location','state')
    def onchange_state(self):
        asset_list = []
        if self.location and self.state and self.filter_by == 'state':
            asset_ids_sr = self.env['bt.asset'].search([('current_loc_id','=',self.location.id),('state','=',self.state)])
            for asset in asset_ids_sr:
                asset_list.append((0, 0, {'date':asset.write_date,'name':asset.id,'model_name':asset.model_name}))
          
        elif self.location and self.filter_by == 'all':
            asset_ids_sr = self.env['bt.asset'].search([('current_loc_id','=',self.location.id)])
            for asset in asset_ids_sr:
                asset_list.append((0, 0, {'date':asset.write_date,'name':asset.id,'model_name':asset.model_name}))

        self.asset_ids = asset_list
        
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
            style_header.borders
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

            sheet1 = wbk.add_sheet('Asset Report')
		
	    sheet1.col(0).width = 3000
	    sheet1.col(1).width = 14000
	    sheet1.col(2).width = 6000
            row = 0 
        
            sheet1.write_merge(row, row, 0, 2, 'Asset Summary', style_header)

            row = 1

            sheet1.write(row, 0, 'Date', style_header_center)
	    sheet1.write(row, 1, 'Asset', style_header_center)
	    sheet1.write(row, 2, 'Model Name', style_header_center)
            row = 2
            for asset in self.asset_ids:
                sheet1.write(row, 0, asset.date, style_center_align)
                sheet1.write(row, 1, asset.name.name, style_center_align)
                sheet1.write(row, 2, asset.model_name, style_center_align)
                row += 1
            
            """Parsing data as string """
	    file_data = StringIO.StringIO()
	    o=wbk.save(file_data)
	    """string encode of data in wksheet"""
	    out = base64.encodestring(file_data.getvalue())
	    """returning the output xls as binary"""
	    filename = 'asset_report.xls'
	    self.write({'file_f':out, 'file_name':filename})

            return {

                   'url': '/bt_asset_management/spreadsheet_report_controller/download_document?model=assert.report&field=%s&id=%s&filename=%s'%(self.file_f,self.id,self.file_name),
                   'target': 'new',
                   'type': 'ir.actions.act_url',

                   }

class assert_report_line(models.TransientModel):
    _name = 'assert.report.line'

    date = fields.Date('Date')
    name = fields.Many2one('bt.asset','Asset')
    model_name = fields.Char(string='Model Name')
    asset_id = fields.Many2one('assert.report','Asset')