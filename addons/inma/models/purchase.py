import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

class stock_picking(models.Model):
	_inherit = "stock.picking"
	
	delivery_number = fields.Char('Delivery Challan Number')
	quality_remarks = fields.Text('Quality Remarks')
	invoice_no = fields.Char('Invoice Number')
	srm_no = fields.Many2one('stock.requirement.memo','SRM No')
	
class PackOperation(models.Model):
	_inherit = "stock.pack.operation"
	
	remarks = fields.Text('Remarks')
	
	@api.onchange('qty_done')
	def onchange_qtydone(self):
		if self.qty_done:
			if self.qty_done > self.product_qty:
				raise ValidationError(_("Done Quantity Should be less than or equal to To Do Quantity"))
			if self.qty_done < 0:
				raise ValidationError(_("Done Quantity Should be greater than zero"))
				
	@api.one
	@api.constrains('qty_done')
	def constrains_qtydone(self):
		if self.qty_done:
			if self.qty_done > self.product_qty:
				raise ValidationError(_("Done Quantity Should be less than or equal to To Do Quantity"))
		if self.qty_done < 0:
			raise ValidationError(_("Done Quantity Should be greater than zero"))
				
class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"
    
    remarks = fields.Text('Remarks')
    
class AccountInvoiceLine(models.Model):
	_inherit = "account.invoice.line"
	
	@api.onchange('quantity')
	def onchange_quantity(self):
		if self.purchase_id:
			if self.quantity:
				order_line = self.env['purchase.order.line'].search([('order_id','=',self.purchase_id.id),('product_id','=',self.product_id.id)])
				invoice_line = self.env['account.invoice.line'].search([('id','!=',self._origin.id),('purchase_id','=',self.purchase_id.id),('product_id','=',self.product_id.id)])
				total_invoice_qty = 0
				for invoice in invoice_line:
					total_invoice_qty += invoice_line.quantity
				if self.quantity > order_line.product_qty:
					raise ValidationError(_("Invoice Quantity should be less than or eqaul to Ordered Quantity"))
				remaining_qty = order_line.product_qty - total_invoice_qty
				if self.quantity > remaining_qty:
					raise ValidationError(_("Invoice quantity should be less than the already Invoice raised"))
				if self.quantity < 0:
					raise ValidationError(_("Quantity Should be greater than zero"))
						
	@api.one
	@api.constrains('quantity')
	def constrains_quantity(self):
		if self.purchase_id:
			if self.quantity:
				order_line = self.env['purchase.order.line'].search([('order_id','=',self.purchase_id.id),('product_id','=',self.product_id.id)])
				invoice_line = self.env['account.invoice.line'].search([('id','!=',self.id),('purchase_id','=',self.purchase_id.id),('product_id','=',self.product_id.id)])
				total_invoice_qty = 0
				for invoice in invoice_line:
					total_invoice_qty += invoice_line.quantity
				if self.quantity > order_line.product_qty:
					raise ValidationError(_("Invoice Quantity should be less than or eqaul to Ordered Quantity"))
				remaining_qty = order_line.product_qty - total_invoice_qty
				if self.quantity > remaining_qty:
					raise ValidationError(_("Invoice quantity should be less than the already Invoice raised"))
				if self.quantity < 0:
					raise ValidationError(_("Quantity Should be greater than zero"))
					
	@api.onchange('price_unit')
	def onchange_price_unit(self):
		if self.purchase_id:
			if self.price_unit:
				order_line = self.env['purchase.order.line'].search([('order_id','=',self.purchase_id.id),('product_id','=',self.product_id.id)])
				if self.price_unit != order_line.price_unit:
					raise ValidationError(_("Invoice Price should be equal to Ordered Price"))
					
	@api.one
	@api.constrains('price_unit')
	def constrains_price_unit(self):
		if self.purchase_id:
			if self.price_unit:
				order_line = self.env['purchase.order.line'].search([('order_id','=',self.purchase_id.id),('product_id','=',self.product_id.id)])
				if self.price_unit != order_line.price_unit:
					raise ValidationError(_("Invoice Price should be equal to Ordered Price"))
					
class PurchaseOrderLine(models.Model):
	_inherit = 'purchase.order.line'
	
	_sql_constraints = [
        ('product_order_uniq', 'unique(product_id,order_id)', 'Product should be unique'),
        ]
	
	@api.onchange('product_qty')
	def onchange_product_qty(self):
		if self.product_qty:
			if self.product_qty < 0:
				raise ValidationError(_("Quantity Should be greater than zero"))
				
				
	@api.onchange('order_id.partner_id', 'product_id')
	def onchange_product_partner_id(self):
	   domain ={}
	   domain['product_id'] = [('id','in', [])]
	   product_list = []
	   if self.order_id.partner_id:
		   vendor_ids = self.env['vendor.list'].search([('vendor_id', '=', self.order_id.partner_id.id)])
		   for vendor in vendor_ids:
			product_ids = self.env['product.product'].search([('product_tmpl_id','=',vendor.product_id.id)])
			for product in product_ids:
			   product_list.append(product.id)
		   if product_list:
			   domain['product_id'] = [('id','in', product_list)]
	   return {'domain':domain}
			
	@api.one
	@api.constrains('product_qty')			
	def constrains_product_qty(self):
		if self.product_qty:
			if self.product_qty <= 0:
				raise ValidationError(_("Quantity Should be greater than zero"))
		if self.product_qty == 0:
			raise ValidationError(_("Quantity Should not be zero"))
				
	@api.onchange('price_unit')
	def onchange_price_unit(self):
		if self.price_unit:
			if self.price_unit <= 0:
				raise ValidationError(_("Unit Price Should be greater than zero"))
	@api.one
	@api.constrains('price_unit')			
	def constrains_price_unit(self):
		if self.price_unit:
			if self.price_unit <= 0:
				raise ValidationError(_("Unit Price Should be greater than zero"))

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'
	
	@api.onchange('product_uom_qty')
	def onchange_product_uom_qty(self):
		if self.product_uom_qty and self.product_id:
			if self.product_uom_qty <= 0:
				raise ValidationError(_("Quantity Should be greater than zero"))
			if self.product_uom_qty > self.product_id.qty_available:
				raise ValidationError(_("Quantity should less than product on hand otherwise update/purchase product"))
			
	@api.one
	@api.constrains('product_uom_qty')			
	def constrains_product_uom_qty(self):
		if self.product_uom_qty:
			if self.product_uom_qty <= 0:
				raise ValidationError(_("Quantity Should be greater than zero"))
			if self.product_uom_qty > self.product_id.qty_available:
				raise ValidationError(_("Quantity should less than product on hand otherwise update/purchase product"))
		if self.product_uom_qty == 0:
			raise ValidationError(_("Quantity Should not be zero"))
				
	@api.onchange('price_unit')
	def onchange_price_unit(self):
		if self.price_unit:
			if self.price_unit <= 0:
				raise ValidationError(_("Unit Price Should be greater than zero"))
	@api.one
	@api.constrains('price_unit')			
	def constrains_price_unit(self):
		if self.price_unit:
			if self.price_unit <= 0:
				raise ValidationError(_("Unit Price Should be greater than zero"))
		if self.price_unit == 0:
			raise ValidationError(_("Unit Price Should not be zero"))
				
class MrpBom(models.Model):
	_inherit = 'mrp.bom'
	
	@api.constrains('bom_line_ids')
	def constrain_bom_line_ids(self):
		if self.bom_line_ids:
			return True
		else:
			raise ValidationError(_("Enter Bill of Material Product"))
			
class AccountInvoice(models.Model):
	_inherit = 'account.invoice'
	
	srm_no = fields.Many2one('stock.requirement.memo','SRM No')
	
class account_payment(models.Model):
	_inherit = 'account.payment'
	
	cheque_payment = fields.Char('Cheque Payment')
	voucher = fields.Char('Voucher')

