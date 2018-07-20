from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pack_size = fields.Char('Pack Size')
    product_code = fields.Char('Product Code')
    vat_code = fields.Float('VAT Code', default=20.0)
    reconcilation = fields.Boolean('Reconcilation')
    token = fields.Boolean('Token')
    car_wash = fields.Boolean('Token')
    brand_id = fields.Many2one('brand.master','Brand')
    rrp = fields.Float('RRP')
    margin = fields.Float('Margin%')
    actual_margin = fields.Float('Actual Margin%')
    #margin = fields.Float(compute='_get_margin',string='Margin')
    #actual_margin = fields.Float(compute='_get_actual_margin',string='Actual Margin')
    required_margin = fields.Float('Required Margin%')
    on_hand_qty = fields.Float(compute='_get_current_qty',string='Stock Quantity')
    pack_cost = fields.Float('Pack Cost')
    unit_cost = fields.Float('Unit Cost')
    vat_id = fields.Integer('vat')
    
    @api.depends('on_hand_qty')
    def _get_current_qty(self):
		if self:
			purchase = 0
			for fuel_line in self.env['fuel.delivery.detail'].search([('grade_id','=',self.id)]):
				purchase += fuel_line.fuel_qty
			sale = 0
			for order_line in self.env['pos.order.line'].search([('product_id','=',self.id)]):
				sale += order_line.qty
			self.on_hand_qty = purchase - sale
			
    @api.onchange('list_price','standard_price')
    def onchange_rrp(self):
		if self.standard_price:
			self.margin = self.list_price - self.standard_price
			self.actual_margin = (self.margin / self.standard_price)*100
			
			
    @api.onchange('pack_size','pack_cost','vat_code')
    def onchange_pack(self):
		if self.pack_size and self.pack_cost:
			self.unit_cost = self.pack_cost / float(self.pack_size)
			self.standard_price = (self.pack_cost / float(self.pack_size)) + (self.pack_cost / float(self.pack_size)) * 20/100
	
    @api.constrains('actual_margin','required_margin')
    def constraint_margin(self):
		if self.actual_margin < self.required_margin:
			raise ValidationError(_("Actual Margin is less than the Required Margin"))
			
    #@api.onchange('pos_categ_id')
    #def onchange_pos_categ_id(self):
		#if self.pos_categ_id:
			#self.required_margin = self.pos_categ_id.required_margin
			
	
   
    #@api.depends('lst_price','standard_price','rrp')
    #def _get_margin(self):
		#if self:
			#self.margin = self.lst_price - self.rrp
			
    #@api.depends('rrp','margin')
    #def _get_actual_margin(self):
		#if self and self.rrp != 0:
			#self.actual_margin = self.margin / self.rrp*100

    
class BrandMaster(models.Model):
	_name = 'brand.master'
	
	name = fields.Char('Brand Master')
	
class PosCategory(models.Model):
	_inherit = "pos.category"
	
	required_margin = fields.Float('Required Margin%')
	
	@api.onchange('required_margin')
	def onchange_required_margin(self):
		if self.required_margin:
			product_ids = self.env['product.product'].search([('pos_categ_id','=',self._origin.id)])
			for product in product_ids:
				product.write({'required_margin':self.required_margin})
				
class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	sales = fields.Char('Sales')
	picker = fields.Char('Picker')
	
class PurchaseOrderLine(models.Model):
	_inherit = 'purchase.order.line'
	
	sku = fields.Char('SKU')
	srp = fields.Float('SRP')
	por = fields.Float('POR%')
	
class Productproduct(models.Model):
	_inherit = 'product.product'
	

	@api.onchange('lst_price','standard_price')
        def onchange_rrp(self):
		if self.standard_price:
			self.margin = self.lst_price - self.standard_price
			self.actual_margin = (self.margin / self.standard_price)*100
			
			
        @api.onchange('pack_size','pack_cost')
        def onchange_pack(self):
		if self.pack_size and self.pack_cost:
			self.unit_cost = self.pack_cost / float(self.pack_size)
			self.standard_price = (self.pack_cost / float(self.pack_size)) + (self.pack_cost / float(self.pack_size)) * 20/100
