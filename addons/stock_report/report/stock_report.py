import time
from datetime import date, timedelta, datetime
from odoo import api, models, fields, _
import base64
import sys
import StringIO
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from xlwt import *

try:
    import xlwt            
except:
    raise UserError(_('Warning !','python-xlwt module missing. Please install it.'))


class product_stock_report(models.TransientModel):
    _name = 'product.stock.report'
    _description = 'Product Stock Report'
    
    from_date = fields.Date("From Date", required=True)
    till_date = fields.Date("Till Date", required=True)
    location_id = fields.Many2one('stock.location', 'Location', required=True)
    file = fields.Binary("File", readonly=True)
    file_name = fields.Char("File Name", readonly=True)               
    filter_by = fields.Selection([('breakup', 'Break up'), ('consolidated', 'Consolidated'),('all', 'All')], 
                                            "Mode", required=True)

    
    def generate_report_excel(self):
        
        res = {}
            
        from_date = self.from_date
        till_date = self.till_date
        filter_by = self.filter_by
        location_id = self.location_id
        
        partner_obj = self.env['res.partner']
        account_move_line_obj = self.env['account.move.line']
        account_invoice_line_obj = self.env['account.invoice.line']
        products = self.env['product.product'].search([])
        company_name = location_id.company_id.name
        parent_company = self.env['res.company'].search([],order='id')[0]
        
        wbk = xlwt.Workbook('utf-8')
        
        # borders
        borders = xlwt.Borders()
        borders.bottom = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.left = xlwt.Borders.THIN
        borders.right = xlwt.Borders.THIN
        
        style_header = XFStyle()        
        fnt = Font()
        fnt.colour_index = 0x36
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
        
        style_header2 = XFStyle()        
        fnt = Font()        
        fnt.bold = True        
        style_header2.font = fnt        
        al1 = Alignment()
        al1.horz = Alignment.HORZ_CENTER
        al1.vert = Alignment.VERT_CENTER        
        pat2 = Pattern()
        pat2.pattern = Pattern.SOLID_PATTERN
        pat2.pattern_fore_colour = Style.colour_map['light_turquoise']        
        style_header2.alignment = al1
        style_header2.pattern = pat2
        style_header2.borders = borders
        
        style_header_right = XFStyle()        
        fnt = Font()
        fnt.colour_index = 0x36
        fnt.bold = True
        fnt.height = 12*0x14
        style_header_right.font = fnt        
        al1 = Alignment()
        al1.horz = Alignment.HORZ_RIGHT
        al1.vert = Alignment.VERT_CENTER        
        pat2 = Pattern()        
        style_header_right.alignment = al1
        style_header_right.pattern = pat2
        style_header_right.borders = borders
        
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
        
        style_right_align3 = XFStyle()        
        al_r = Alignment()
        al_r.horz = Alignment.HORZ_RIGHT
        al_r.vert = Alignment.VERT_CENTER
        style_right_align3.alignment = al_r
        style_right_align3.num_format_str = "0.00"
        pat3 = Pattern()
        pat3.pattern = Pattern.SOLID_PATTERN
        pat3.pattern_fore_colour = Style.colour_map['light_turquoise']  
        style_right_align3.pattern = pat3
        style_right_align3.borders = borders
        
        style_center_align = XFStyle()
        al_c = Alignment()
        al_c.horz = Alignment.HORZ_CENTER
        al_c.vert = Alignment.VERT_CENTER
        style_center_align.alignment = al_c
        style_center_align.borders = borders
        
        style_left_align = XFStyle()
        al_l = Alignment()
        al_l.horz = Alignment.HORZ_LEFT
        al_l.vert = Alignment.VERT_CENTER
        style_left_align.alignment = al_l
        style_left_align.borders = borders
        
        style_left_align2 = XFStyle()
        al_l = Alignment()
        al_l.horz = Alignment.HORZ_LEFT
        al_l.vert = Alignment.VERT_CENTER
        style_left_align2.alignment = al_l
        pat2 = Pattern()
        pat2.pattern = Pattern.SOLID_PATTERN
        pat2.pattern_fore_colour = Style.colour_map['light_turquoise']  
        style_left_align2.pattern = pat2
        style_left_align2.borders = borders
        
        from_date_gmt = datetime.strptime(from_date, "%Y-%m-%d")
        from_date_gmt_time = datetime.combine(from_date_gmt, datetime.strptime("00:00:00","%H:%M:%S").time())
        from_date_ist = str(from_date_gmt_time - timedelta(0, 19800))
        
        next_till_date_gmt = datetime.strptime(till_date, "%Y-%m-%d").date()+timedelta(days=+1)
        next_till_date_gmt_time = datetime.combine(next_till_date_gmt, datetime.strptime("00:00:00","%H:%M:%S").time())
        next_till_date_ist = str(next_till_date_gmt_time - timedelta(0, 19800))
        
        if 'consolidated' in filter_by or 'all' in filter_by:
            
            total_value = 0
            sheet1 = wbk.add_sheet('Consolidated')
            
            sheet1.col(0).width = 20000
            sheet1.col(1).width = 3000
            sheet1.col(2).width = 3000
            sheet1.col(3).width = 3000
            sheet1.col(4).width = 3000   
            sheet1.row(0).height = 380
            sheet1.row(1).height = 350
            sheet1.row(2).height = 350
            sheet1.row(3).height = 350 
                
            row = 0        
            sheet1.write_merge(row, row, 0, 6, parent_company.name, style_header)        
            row += 1
            sheet1.write_merge(row, row, 0, 6, 'Branch Name: ' + str(company_name) + ', Location: ' + str(location_id.display_name) , style_header)        
            row += 1
            sheet1.write_merge(row, row, 0, 6, 'Product Wise Consolidated Stock Report:'  + ' From: '+from_date+' To: '+till_date, style_header)
           
            row += 1
            sheet1.write(row, 0, 'Product', style_header)
            sheet1.write(row, 1, 'Opening', style_header)
            sheet1.write(row, 2, 'In', style_header)
            sheet1.write(row, 3, 'Out', style_header)
            sheet1.write(row, 4, 'Closing', style_header)
            sheet1.write(row, 5, 'Price', style_header)
            sheet1.write(row, 6, 'Value', style_header)
            
        
            for product in products:

                self.env.cr.execute('SELECT product_id, sum(product_qty) AS product_qty \
                                    FROM stock_move AS sm \
                                    JOIN stock_picking sp ON (sp.id = sm.picking_id) \
                                    WHERE \
                                    sm.product_id = %s AND \
                                    sm.location_id = %s AND \
                                    sm.state = %s AND \
                                    sm.date <= %s GROUP BY product_id', (product.id, location_id.id, 'done', from_date_ist))        
                total_out = self.env.cr.dictfetchall()
                
                self.env.cr.execute('SELECT product_id, sum(product_qty) AS product_qty \
                                    FROM stock_move AS sm \
                                    JOIN stock_picking sp ON (sp.id = sm.picking_id) \
                                    WHERE \
                                    sm.product_id = %s AND \
                                    sm.location_dest_id = %s AND \
                                    sm.state = %s AND \
                                    sm.date <= %s GROUP BY product_id', (product.id, location_id.id, 'done', from_date_ist))        
                total_in = self.env.cr.dictfetchall()
                
                self.env.cr.execute('SELECT product_id, sum(product_qty) AS product_qty \
                                    FROM stock_move AS sm \
                                    WHERE \
                                    sm.product_id = %s AND \
                                    sm.location_dest_id = %s AND \
                                    sm.state = %s AND \
                                    sm.picking_id IS NULL AND \
                                    sm.date <= %s GROUP BY product_id', (product.id, location_id.id, 'done', from_date_ist))        
                total_in_without_picking = self.env.cr.dictfetchall()
                
                self.env.cr.execute('SELECT product_id, sum(product_qty) AS product_qty \
                                    FROM stock_move AS sm \
                                    WHERE \
                                    sm.product_id = %s AND \
                                    sm.location_id = %s AND \
                                    sm.state = %s AND \
                                    sm.picking_id IS NULL AND \
                                    sm.date <= %s GROUP BY product_id', (product.id, location_id.id, 'done', from_date_ist))        
                total_out_without_picking = self.env.cr.dictfetchall()
                
                if not total_in:
                    total_in = 0
                else:
                    total_in = total_in[0]['product_qty']
                
                if total_in_without_picking:
                    total_in += total_in_without_picking[0]['product_qty']
                    
                if not total_out:
                    total_out = 0
                else:
                    total_out = total_out[0]['product_qty']
                    
                if total_out_without_picking:
                    total_out += total_out_without_picking[0]['product_qty']
                
                opening_stock = total_in - total_out 
                    
                self.env.cr.execute('SELECT product_id, sum(product_qty) AS product_qty \
                                    FROM stock_move AS sm \
                                    JOIN stock_picking sp ON (sp.id = sm.picking_id) \
                                    WHERE \
                                    sm.product_id = %s AND \
                                    sm.location_id = %s AND \
                                    sm.state = %s AND \
                                    sm.date > %s AND \
                                    sm.date <= %s GROUP BY product_id', (product.id, location_id.id, 'done', from_date_ist, next_till_date_ist))        
                total_out_this = self.env.cr.dictfetchall()
                
                self.env.cr.execute('SELECT product_id, sum(product_qty) AS product_qty \
                                    FROM stock_move AS sm \
                                    JOIN stock_picking sp ON (sp.id = sm.picking_id) \
                                    WHERE \
                                    sm.product_id = %s AND \
                                    sm.location_dest_id = %s AND \
                                    sm.state = %s AND \
                                    sm.date > %s AND \
                                    sm.date <= %s GROUP BY product_id', (product.id, location_id.id, 'done', from_date_ist, next_till_date_ist))        
                total_in_this = self.env.cr.dictfetchall()
                
                self.env.cr.execute('SELECT product_id, sum(product_qty) AS product_qty \
                                    FROM stock_move AS sm \
                                    WHERE \
                                    sm.product_id = %s AND \
                                    sm.location_dest_id = %s AND \
                                    sm.state = %s AND \
                                    sm.picking_id IS NULL AND \
                                    sm.date > %s AND \
                                    sm.date <= %s GROUP BY product_id', (product.id, location_id.id, 'done', from_date_ist, next_till_date_ist))        
                total_in_this_without_picking = self.env.cr.dictfetchall()
                
                self.env.cr.execute('SELECT product_id, sum(product_qty) AS product_qty \
                                    FROM stock_move AS sm \
                                    WHERE \
                                    sm.product_id = %s AND \
                                    sm.location_id = %s AND \
                                    sm.state = %s AND \
                                    sm.picking_id IS NULL AND \
                                    sm.date > %s AND \
                                    sm.date <= %s GROUP BY product_id', (product.id, location_id.id, 'done', from_date_ist, next_till_date_ist))        
                total_out_this_without_picking = self.env.cr.dictfetchall()
                
                if not total_in_this:
                    total_in_this = 0
                else:
                    total_in_this = total_in_this[0]['product_qty']
                
                if total_in_this_without_picking:
                    total_in_this += total_in_this_without_picking[0]['product_qty']
                     
                if not total_out_this:
                    total_out_this = 0
                else:
                    total_out_this = total_out_this[0]['product_qty']
                
                if total_out_this_without_picking:
                    total_out_this += total_out_this_without_picking[0]['product_qty']
                
                closing_stock = opening_stock + total_in_this - total_out_this 
                if not opening_stock and not total_in_this and not total_out_this and not closing_stock:
                    continue
                else:
                    row += 1
                    sheet1.write(row, 0, product.name, style_left_align)
                    sheet1.write(row, 1, opening_stock, style_right_align)
                    sheet1.write(row, 2, total_in_this, style_right_align)
                    sheet1.write(row, 3, total_out_this, style_right_align)
                    sheet1.write(row, 4, closing_stock, style_right_align)
                    sheet1.write(row, 5, product.lst_price, style_right_align)
                    sheet1.write(row, 6, closing_stock*product.lst_price, style_right_align)
                    total_value += closing_stock*product.lst_price
                    
            row += 1
            sheet1.write_merge(row, row, 0, 5, 'TOTAL VALUE', style_header)
            sheet1.write(row, 6, total_value, style_right_align)
            
        if 'breakup' in filter_by or 'all' in filter_by:
            
            total_value = 0
            sheet1 = wbk.add_sheet('Breakup')
            
            sheet1.col(0).width = 20000
            sheet1.col(1).width = 4000
            sheet1.col(2).width = 3000
            sheet1.col(3).width = 3000
            sheet1.col(4).width = 3000   
            sheet1.row(0).height = 380
            sheet1.row(1).height = 350
            sheet1.row(2).height = 350
            sheet1.row(3).height = 350  
                
            row = 0        
            sheet1.write_merge(row, row, 0, 6, parent_company.name, style_header)        
            row += 1
            sheet1.write_merge(row, row, 0, 6, 'Branch Name: ' + str(company_name) + ', Location: ' + str(location_id.display_name), style_header)        
            row += 1
            sheet1.write_merge(row, row, 0, 6, 'Product Wise Breakup Stock Report:'  + ' From: '+from_date+' To: '+till_date, style_header)
           
            row += 1
            sheet1.write(row, 0, 'Product', style_header)
            sheet1.write(row, 1, 'Opening', style_header)
            sheet1.write(row, 2, 'In', style_header)
            sheet1.write(row, 3, 'Out', style_header)
            sheet1.write(row, 4, 'Closing', style_header)
            sheet1.write(row, 5, 'Price', style_header)
            sheet1.write(row, 6, 'Value', style_header)
        
            for product in products:
                
                self.env.cr.execute('SELECT product_id, sum(product_qty) AS product_qty \
                                    FROM stock_move AS sm \
                                    JOIN stock_picking sp ON (sp.id = sm.picking_id) \
                                    WHERE \
                                    sm.product_id = %s AND \
                                    sm.location_id = %s AND \
                                    sm.state = %s AND \
                                    sm.date <= %s GROUP BY product_id', (product.id, location_id.id, 'done', from_date_ist))        
                total_out = self.env.cr.dictfetchall()
                
                self.env.cr.execute('SELECT product_id, sum(product_qty) AS product_qty \
                                    FROM stock_move AS sm \
                                    JOIN stock_picking sp ON (sp.id = sm.picking_id) \
                                    WHERE \
                                    sm.product_id = %s AND \
                                    sm.location_dest_id = %s AND \
                                    sm.state = %s AND \
                                    sm.date <= %s GROUP BY product_id', (product.id, location_id.id, 'done', from_date_ist))        
                total_in = self.env.cr.dictfetchall()
                
                self.env.cr.execute('SELECT product_id, sum(product_qty) AS product_qty \
                                    FROM stock_move AS sm \
                                    WHERE \
                                    sm.product_id = %s AND \
                                    sm.location_dest_id = %s AND \
                                    sm.state = %s AND \
                                    sm.picking_id IS NULL AND \
                                    sm.date <= %s GROUP BY product_id', (product.id, location_id.id, 'done', from_date_ist))        
                total_in_without_picking = self.env.cr.dictfetchall()
                
                self.env.cr.execute('SELECT product_id, sum(product_qty) AS product_qty \
                                    FROM stock_move AS sm \
                                    WHERE \
                                    sm.product_id = %s AND \
                                    sm.location_id = %s AND \
                                    sm.state = %s AND \
                                    sm.picking_id IS NULL AND \
                                    sm.date <= %s GROUP BY product_id', (product.id, location_id.id, 'done', from_date_ist))        
                total_out_without_picking = self.env.cr.dictfetchall()
                
                if not total_in:
                    total_in = 0
                else:
                    total_in = total_in[0]['product_qty']
                
                if total_in_without_picking:
                    total_in += total_in_without_picking[0]['product_qty']
                    
                if not total_out:
                    total_out = 0
                else:
                    total_out = total_out[0]['product_qty']
                    
                if total_out_without_picking:
                    total_out += total_out_without_picking[0]['product_qty']
                
                opening_stock = total_in - total_out 
                    
                self.env.cr.execute('SELECT product_id, sum(product_qty) AS product_qty \
                                    FROM stock_move AS sm \
                                    JOIN stock_picking sp ON (sp.id = sm.picking_id) \
                                    WHERE \
                                    sm.product_id = %s AND \
                                    sm.location_id = %s AND \
                                    sm.state = %s AND \
                                    sm.date > %s AND \
                                    sm.date <= %s GROUP BY product_id', (product.id, location_id.id, 'done', from_date_ist, next_till_date_ist))        
                total_out_this = self.env.cr.dictfetchall()
                
                self.env.cr.execute('SELECT product_id, sum(product_qty) AS product_qty \
                                    FROM stock_move AS sm \
                                    JOIN stock_picking sp ON (sp.id = sm.picking_id) \
                                    WHERE \
                                    sm.product_id = %s AND \
                                    sm.location_dest_id = %s AND \
                                    sm.state = %s AND \
                                    sm.date > %s AND \
                                    sm.date <= %s GROUP BY product_id', (product.id, location_id.id, 'done', from_date_ist, next_till_date_ist))        
                total_in_this = self.env.cr.dictfetchall()
                
                self.env.cr.execute('SELECT product_id, sum(product_qty) AS product_qty \
                                    FROM stock_move AS sm \
                                    WHERE \
                                    sm.product_id = %s AND \
                                    sm.location_dest_id = %s AND \
                                    sm.state = %s AND \
                                    sm.picking_id IS NULL AND \
                                    sm.date > %s AND \
                                    sm.date <= %s GROUP BY product_id', (product.id, location_id.id, 'done', from_date_ist, next_till_date_ist))        
                total_in_this_without_picking = self.env.cr.dictfetchall()
                
                self.env.cr.execute('SELECT product_id, sum(product_qty) AS product_qty \
                                    FROM stock_move AS sm \
                                    WHERE \
                                    sm.product_id = %s AND \
                                    sm.location_id = %s AND \
                                    sm.state = %s AND \
                                    sm.picking_id IS NULL AND \
                                    sm.date > %s AND \
                                    sm.date <= %s GROUP BY product_id', (product.id, location_id.id, 'done', from_date_ist, next_till_date_ist))        
                total_out_this_without_picking = self.env.cr.dictfetchall()
                
                if not total_in_this:
                    total_in_this = 0
                else:
                    total_in_this = total_in_this[0]['product_qty']
                
                if total_in_this_without_picking:
                    total_in_this += total_in_this_without_picking[0]['product_qty']
                     
                if not total_out_this:
                    total_out_this = 0
                else:
                    total_out_this = total_out_this[0]['product_qty']
                
                if total_out_this_without_picking:
                    total_out_this += total_out_this_without_picking[0]['product_qty']
                
                closing_stock = opening_stock + total_in_this - total_out_this 
                if not opening_stock and not total_in_this and not total_out_this and not closing_stock:
                    continue
                else:
                    row += 1
                    sheet1.write(row, 0, product.name, style_left_align)
                    sheet1.write(row, 1, opening_stock, style_right_align)
                    sheet1.write(row, 2, total_in_this, style_right_align)
                    sheet1.write(row, 3, total_out_this, style_right_align)
                    sheet1.write(row, 4, closing_stock, style_right_align)
                    sheet1.write(row, 5, product.lst_price, style_right_align)
                    sheet1.write(row, 6, closing_stock*product.lst_price, style_right_align)
                    total_value += closing_stock*product.lst_price
                    
                self.env.cr.execute('SELECT sm.picking_id as ref, sm.date, sm.origin, sm.product_id, sm.product_qty AS product_qty, sld.name AS destination, sls.name AS source \
                                FROM stock_move AS sm \
                                JOIN stock_location sld ON (sm.location_dest_id = sld.id) \
                                JOIN stock_location sls ON (sm.location_id = sls.id) \
                                WHERE \
                                sm.product_id = %s AND \
                                sm.location_dest_id = %s AND \
                                sm.state = %s AND \
                                sm.picking_id IS NULL AND \
                                sm.date > %s AND \
                                sm.date <= %s ORDER BY date', (product.id, location_id.id, 'done', from_date_ist, next_till_date_ist))
                in_moves_without_picking = self.env.cr.dictfetchall()
                
                self.env.cr.execute('SELECT sp.name as ref, sm.date, sm.origin, sm.product_id, sm.product_qty AS product_qty, sld.name AS destination, sls.name AS source \
                                FROM stock_move AS sm \
                                JOIN stock_location sld ON (sm.location_dest_id = sld.id) \
                                JOIN stock_location sls ON (sm.location_id = sls.id) \
                                JOIN stock_picking sp ON (sp.id = sm.picking_id) \
                                WHERE \
                                sm.product_id = %s AND \
                                sm.location_dest_id = %s AND \
                                sm.state = %s AND \
                                sm.date > %s AND \
                                sm.date <= %s ORDER BY date', (product.id, location_id.id, 'done', from_date_ist, next_till_date_ist))
                in_moves = self.env.cr.dictfetchall()   
                
                if in_moves_without_picking:             
                    if in_moves:
                        in_moves = in_moves_without_picking+in_moves
                    else:
                        in_moves = in_moves_without_picking[:]
                        
                if in_moves:
                    row += 1
                    sheet1.write_merge(row, row, 0, 6, 'Incoming Stock', style_header2)
                    
                    row += 1
                    sheet1.write(row, 0, "Ref", style_header2)
                    sheet1.write(row, 1, "Date", style_header2)                        
                    sheet1.write_merge(row, row, 2, 3, "Source", style_header2)
                    sheet1.write_merge(row, row, 4, 5, "Destination", style_header2)
                    sheet1.write(row, 6, "Qty", style_header2)
                    
                    for move in in_moves:
                        row += 1
                        if move['ref']:
                            if move['origin']:
                                sheet1.write(row, 0, move['origin']+'-'+move['ref'], style_left_align2)
                            else:
                                sheet1.write(row, 0, move['ref'], style_left_align2)
                        else:
                            sheet1.write(row, 0, move['origin'], style_left_align2)
                        sheet1.write(row, 1, move['date'], style_left_align2)                        
                        sheet1.write_merge(row, row, 2, 3, move['source'], style_left_align2)
                        sheet1.write_merge(row, row, 4, 5, move['destination'], style_left_align2)
                        sheet1.write(row, 6, move['product_qty'], style_right_align3)
                    row += 1
                    sheet1.write_merge(row, row, 0, 6, '--------------', style_header2)
                
                self.env.cr.execute('SELECT sm.picking_id as ref, sm.date, sm.origin, sm.product_id, sm.product_qty AS product_qty, sld.name AS destination, sls.name AS source \
                                FROM stock_move AS sm \
                                JOIN stock_location sld ON (sm.location_dest_id = sld.id) \
                                JOIN stock_location sls ON (sm.location_id = sls.id) \
                                WHERE \
                                sm.product_id = %s AND \
                                sm.location_id = %s AND \
                                sm.state = %s AND \
                                sm.picking_id IS NULL AND \
                                sm.date > %s AND \
                                sm.date <= %s ORDER BY date', (product.id, location_id.id, 'done', from_date_ist, next_till_date_ist))
                out_moves_without_picking = self.env.cr.dictfetchall()
                
                self.env.cr.execute('SELECT sp.name as ref, sm.date, sm.origin, sm.product_id, sm.product_qty AS product_qty, sld.name AS destination, sls.name AS source \
                                FROM stock_move AS sm \
                                JOIN stock_location sld ON (sm.location_dest_id = sld.id) \
                                JOIN stock_location sls ON (sm.location_id = sls.id) \
                                JOIN stock_picking sp ON (sp.id = sm.picking_id) \
                                WHERE \
                                sm.product_id = %s AND \
                                sm.location_id = %s AND \
                                sm.state = %s AND \
                                sm.date > %s AND \
                                sm.date <= %s ORDER BY date', (product.id, location_id.id, 'done', from_date_ist, next_till_date_ist))
                
                out_moves = self.env.cr.dictfetchall()
                
                if out_moves_without_picking:             
                    if out_moves:
                        out_moves = out_moves_without_picking+out_moves
                    else:
                        out_moves = out_moves_without_picking[:]
                        
                if out_moves:
                    row += 1
                    sheet1.write_merge(row, row, 0, 6, 'Outgoing Stock', style_header2)
                    
                    row += 1
                    sheet1.write(row, 0, "Ref", style_header2)
                    sheet1.write(row, 1, "Date", style_header2)                        
                    sheet1.write_merge(row, row, 2, 3, "Source", style_header2)
                    sheet1.write_merge(row, row, 4, 5, "Destination", style_header2)
                    sheet1.write(row, 6, "Qty", style_header2)
                    
                    for move in out_moves:
                        row += 1
                        if move['ref']:
                            if move['origin']:
                                sheet1.write(row, 0, move['origin']+'-'+move['ref'], style_left_align2)
                            else:
                                sheet1.write(row, 0, move['ref'], style_left_align2)
                        else:
                            sheet1.write(row, 0, move['origin'], style_left_align2)
                        sheet1.write(row, 1, move['date'], style_left_align2)                                                
                        sheet1.write_merge(row, row, 2, 3, move['source'], style_left_align2)
                        sheet1.write_merge(row, row, 4, 5, move['destination'], style_left_align2)
                        sheet1.write(row, 6, move['product_qty'], style_right_align3)
                    row += 1
                    sheet1.write_merge(row, row, 0, 6, '--------------', style_header2)
                    
            row += 1
            sheet1.write_merge(row, row, 0, 5, 'TOTAL VALUE', style_header)
            sheet1.write(row, 6, total_value, style_right_align)
                                   
        """Parsing data as string """

        file_data=StringIO.StringIO()
        o=wbk.save(file_data)
        """string encode of data in wksheet"""
        out=base64.encodestring(file_data.getvalue())
        """returning the output xls as binary"""
        
        file = out
        file_name = 'Stock_Report.xls'
        
        self.write({'file':out, 'file_name':file_name})
        
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'res_model': 'product.stock.report',
            'target': 'new',
            'context': self._context
            }
    
    
    
product_stock_report()

