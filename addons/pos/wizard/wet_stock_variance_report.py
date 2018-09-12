from odoo import api, fields, models

import StringIO
import base64
from xlwt import *

from datetime import datetime, date, time, timedelta
import time

try:
    import cStringIO as StringIO
    import xlwt
except:
    raise osv.except_osv('Warning !','python-xlwt module missing. Please install it.')

class WetStockVarianceReport(models.TransientModel):
    _name = "wet.stock.variance.report"

    from_date = fields.Date("From Date")
    till_date = fields.Date("To Date")
    file_f = fields.Binary("File", readonly=True)
    file_name = fields.Char("File Name",size=128, readonly=True)
    
    @api.multi
    def print_report(self):
        
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

        style_header_left2 = XFStyle()
        fnt = Font()
        fnt.height = 11*0x14
        style_header_left2.font = fnt
        al1 = Alignment()
        al1.horz = Alignment.HORZ_LEFT
        al1.vert = Alignment.VERT_CENTER
        pat2 = Pattern()
        style_header_left2.alignment = al1
        style_header_left2.pattern = pat2
        style_header_left2.borders = borders

        sheet1 = wbk.add_sheet('Wetstock Variance')

        sheet1.col(0).width = 2000
        sheet1.col(1).width = 2000
        sheet1.col(2).width = 2000
        sheet1.col(3).width = 2000
        sheet1.col(4).width = 2000
        sheet1.col(5).width = 2000
        sheet1.col(6).width = 2000
        sheet1.col(7).width = 2000
        sheet1.col(8).width = 2000
        sheet1.col(9).width = 2000
        sheet1.col(10).width = 2000
        
        row = 3
        col = 1
        sheet1.write_merge(row, row, 0, 1, ' ', style_center_align1)
        tank_list = []
        for tank in self.env['tank.master'].search([], order = 'name asc'):
            tank_list.append(tank.name)
            col += 1
            next_col = col
            sheet1.write_merge(row, row, col, next_col+1, (tank.name).upper(), style_center_align1)
            col = next_col + 1

        row = 0
        sheet1.write_merge(row, row, 0, col, 'Day Report', style_header)
        row = 1
        sheet1.write_merge(row, row, 0, col, datetime.strptime(self.from_date, "%Y-%m-%d").strftime('%A %d. %B %Y') + '-' + datetime.strptime(self.till_date, "%Y-%m-%d").strftime('%A %d. %B %Y'), style_header)
        row = 2
        sheet1.write_merge(row, row, 0, col, 'Wetstock Variance', style_header)
        
        row = 4
        if self.from_date and self.till_date:
            date_start = datetime.strptime(self.from_date, "%Y-%m-%d").date()
            date_end = datetime.strptime(self.till_date, "%Y-%m-%d").date()
            while date_start <= date_end:
                col = 0
                next_col = col 
                running_date = datetime.strftime(date_start, "%Y-%m-%d")
                sheet1.write_merge(row, row, col, next_col+1, running_date, style_header_left2)
                col = next_col + 2
                for tank in self.env['tank.master'].search([], order = 'name asc'):
                    
                    open_gauge_ids = self.env['tank.log.reading'].search([('date_time','>=', running_date),('date_time','<=', running_date),('tank_id','=', tank.id)], order='date_time asc', limit=1)
                    close_gauge_ids = self.env['tank.log.reading'].search([('date_time','>=', running_date),('date_time','<=', running_date),('tank_id','=', tank.id)], order='date_time desc', limit=1)
                    
                    opening_gauge = open_gauge_ids.opening_gauge
                    closing_gauge = close_gauge_ids.opening_gauge
                   
                    purchase_stock = 0
                    for fuel_delivery in self.env['fuel.delivery'].search([('date','=',running_date)]):
                        for fuel_line in self.env['fuel.delivery.detail'].search([('fuel_delivery_id','=',fuel_delivery.id),('tank_id','=',tank.id)]):
                            purchase_stock += fuel_line.fuel_qty	
                    delivery = purchase_stock		

                    nozle_list = []
                    for nozle in self.env['dom.nozle'].search([('tank_id','=',tank.id)]):
                        nozle_list.append(nozle.id)    
                    pos_order_ids = self.env['pos.order'].search([('date_order','>=',running_date),('date_order','<=',running_date),('nozle_id','in',nozle_list)])
                    sale_stock = 0
                    pos_order_list = []
                    for pos_order in pos_order_ids:
                        pos_order_list.append(pos_order.id)
                    for line in self.env['pos.order.line'].search([('order_id','in',pos_order_list),('product_id','=',tank.tank_type.id)]): 
                        if line:
                            sale_stock += line.qty
                    sales = sale_stock

                    closing_book = opening_gauge + delivery - sales
                    variance = closing_book - closing_gauge

                    next_col = col
                    sheet1.write_merge(row, row, col, next_col+1, variance, style_header_left2)
                    col = next_col + 2

                row += 1
                date_start = date_start + timedelta(days=1)


        """Parsing data as string """
        file_data = StringIO.StringIO()
        o=wbk.save(file_data)
        """string encode of data in wksheet"""
        out = base64.encodestring(file_data.getvalue())
        """returning the output xls as binary"""
        filename = 'sales_report.xls'
        self.write({'file_f':out, 'file_name':filename})       

        return {
                   'url': '/pos/spreadsheet_report_controller/download_document?model=wet.stock.variance.report&field=%s&id=%s&filename=%s'%(self.file_f,self.id,self.file_name),
                   'target': 'new',
                   'type': 'ir.actions.act_url',
                }