from odoo import api, fields, models


class SaleReport(models.TransientModel):
	_name = 'sales.report'
	
	order_from_date = fields.Date('From')
	order_to_date = fields.Date('To')
	state = fields.Selection([('draft','Quotation'), ('sent','Quotation Sent'), ('sale','Sales Order'), ('done','Locked'), ('cancel','Cancelled')], string='Order Status')
	user_id = fields.Many2one('res.users','Salesperson')
	payment_term_id = fields.Many2one('account.payment.term','Payment Terms')
	team_id = fields.Many2one('crm.team','Sales Team')
	filter_by = fields.Selection([('date','Date Range'),('state','Order Status'),('users','Salesperson'),('payment_term','Payment Terms'),('team','Sales Team')], 'Filter By', default='date')
	total_quantity = fields.Float('Total Quantity')
	total_unit_price = fields.Float('Total Unit Price')
	total_taxes = fields.Float('Total Taxes')
	total_amount = fields.Float('Total Amount')
	sale_report_line_ids = fields.One2many('sale.report.line','sales_report_id','Sales Report')

	@api.onchange('order_from_date','order_to_date','filter_by','user_id','payment_term_id','team_id','state')
	def onchange_salesreport(self):
		sale_report_list = []
		total_quantity = 0
		total_unit_price = 0
		total_taxes = 0
		total_amount = 0
		if self.order_from_date and self.order_to_date and self.filter_by == 'date':
			
			sales_ids = self.env['sale.order'].search([('date_order','>=',self.order_from_date),('date_order','<=',self.order_to_date)])
			for sale in sales_ids:
				for sale_line in sale.order_line:
					total_quantity = total_quantity + sale_line.product_uom_qty
					total_unit_price = total_unit_price + sale_line.price_unit
					total_taxes = total_taxes + sale_line.price_tax
					total_amount = total_amount + sale_line.price_reduce_taxinc
					sale_report_list.append((0, 0, {'order_date':sale.date_order,'order_no':sale.name,'customer_id':sale.partner_id.id,'state':sale.state,'user_id':sale.user_id.id,'payment_term_id':sale.payment_term_id.id,'team_id':sale.team_id.id,'product_id':sale_line.product_id.id,'product_uom_qty':sale_line.product_uom_qty,'unit_measure':sale_line.product_uom.id,'unit_price':sale_line.price_unit,'tax':sale_line.price_tax,'total':sale_line.price_reduce_taxinc}))

		if self.order_from_date and self.order_to_date and self.state and self.filter_by == 'state':
			sales_ids = self.env['sale.order'].search([('date_order','>=',self.order_from_date),('date_order','<=',self.order_to_date),('state','=',self.state)])
			for sale in sales_ids:
				for sale_line in sale.order_line:
					total_quantity = total_quantity + sale_line.product_uom_qty
					total_unit_price = total_unit_price + sale_line.price_unit
					total_taxes = total_taxes + sale_line.price_tax
					total_amount = total_amount + sale_line.price_reduce_taxinc
					sale_report_list.append((0, 0, {'order_date':sale.date_order,'order_no':sale.name,'customer_id':sale.partner_id.id,'state':sale.state,'user_id':sale.user_id.id,'payment_term_id':sale.payment_term_id.id,'team_id':sale.team_id.id,'product_id':sale_line.product_id.id,'product_uom_qty':sale_line.product_uom_qty,'unit_measure':sale_line.product_uom.id,'unit_price':sale_line.price_unit,'tax':sale_line.price_tax,'total':sale_line.price_reduce_taxinc}))

		if self.order_from_date and self.order_to_date and self.user_id and self.filter_by == 'users':
			sales_ids = self.env['sale.order'].search([('date_order','>=',self.order_from_date),('date_order','<=',self.order_to_date),('user_id','=',self.user_id.id)])
			for sale in sales_ids:
				for sale_line in sale.order_line:
					total_quantity = total_quantity + sale_line.product_uom_qty
					total_unit_price = total_unit_price + sale_line.price_unit
					total_taxes = total_taxes + sale_line.price_tax
					total_amount = total_amount + sale_line.price_reduce_taxinc
					sale_report_list.append((0, 0, {'order_date':sale.date_order,'order_no':sale.name,'customer_id':sale.partner_id.id,'state':sale.state,'user_id':sale.user_id.id,'payment_term_id':sale.payment_term_id.id,'team_id':sale.team_id.id,'product_id':sale_line.product_id.id,'product_uom_qty':sale_line.product_uom_qty,'unit_measure':sale_line.product_uom.id,'unit_price':sale_line.price_unit,'tax':sale_line.price_tax,'total':sale_line.price_reduce_taxinc}))

		if self.order_from_date and self.order_to_date and self.payment_term_id and self.filter_by == 'payment_term':
			sales_ids = self.env['sale.order'].search([('date_order','>=',self.order_from_date),('date_order','<=',self.order_to_date),('payment_term_id','=',self.payment_term_id.id)])
			for sale in sales_ids:
				for sale_line in sale.order_line:
					total_quantity = total_quantity + sale_line.product_uom_qty
					total_unit_price = total_unit_price + sale_line.price_unit
					total_taxes = total_taxes + sale_line.price_tax
					total_amount = total_amount + sale_line.price_reduce_taxinc
					sale_report_list.append((0, 0, {'order_date':sale.date_order,'order_no':sale.name,'customer_id':sale.partner_id.id,'state':sale.state,'user_id':sale.user_id.id,'payment_term_id':sale.payment_term_id.id,'team_id':sale.team_id.id,'product_id':sale_line.product_id.id,'product_uom_qty':sale_line.product_uom_qty,'unit_measure':sale_line.product_uom.id,'unit_price':sale_line.price_unit,'tax':sale_line.price_tax,'total':sale_line.price_reduce_taxinc}))


		if self.order_from_date and self.order_to_date and self.team_id and self.filter_by == 'team':
			sales_ids = self.env['sale.order'].search([('date_order','>=',self.order_from_date),('date_order','<=',self.order_to_date),('team_id','=',self.team_id.id)])
			for sale in sales_ids:
				for sale_line in sale.order_line:
					total_quantity = total_quantity + sale_line.product_uom_qty
					total_unit_price = total_unit_price + sale_line.price_unit
					total_taxes = total_taxes + sale_line.price_tax
					total_amount = total_amount + sale_line.price_reduce_taxinc
					sale_report_list.append((0, 0, {'order_date':sale.date_order,'order_no':sale.name,'customer_id':sale.partner_id.id,'state':sale.state,'user_id':sale.user_id.id,'payment_term_id':sale.payment_term_id.id,'team_id':sale.team_id.id,'product_id':sale_line.product_id.id,'product_uom_qty':sale_line.product_uom_qty,'unit_measure':sale_line.product_uom.id,'unit_price':sale_line.price_unit,'tax':sale_line.price_tax,'total':sale_line.price_reduce_taxinc}))


		self.total_quantity = total_quantity
		self.total_unit_price = total_unit_price
		self.total_taxes = total_taxes
		self.total_amount = total_amount

		self.sale_report_line_ids = sale_report_list

class SaleReportline(models.TransientModel):
	_name = 'sale.report.line'

	order_date = fields.Date('Order Date')
	order_no = fields.Char('Order No')
	customer_id = fields.Many2one('res.partner','Customer')
	state = fields.Selection([('draft','Quotation'), ('sent','Quotation Sent'), ('sale','Sales Order'), ('done','Locked'), ('cancel','Cancelled')], string='Order Status')
	user_id = fields.Many2one('res.users','Salesman')
	payment_term_id = fields.Many2one('account.payment.term','Payment Terms')
	team_id = fields.Many2one('crm.team','Sales Team')
	product_id = fields.Many2one('product.product','Product')
	product_uom_qty = fields.Float('Quantity')
	unit_measure = fields.Many2one('product.uom','UOM')
	unit_price = fields.Float('Unit Price')
	tax = fields.Float('Taxes')
	total = fields.Float('Total')
	sales_report_id = fields.Many2one('sales.report','Sales Report')