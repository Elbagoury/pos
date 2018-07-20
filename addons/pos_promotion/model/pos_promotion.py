from odoo import api, fields, models, _

class pos_promotion(models.Model):
    _name = "pos.promotion"
    
    name = fields.Char('Name', required=1)
    active = fields.Boolean('Active', default=1)
    start_date = fields.Datetime('Start date', default=fields.Datetime.now(), required=1)
    end_date = fields.Datetime('End date', required=1)
    type = fields.Selection([
        ('1_discount_total_order', 'Percentage reduction on goods total'),
        ('2_value_reduction_on_goods_total','Value reduction on goods total'),
        ('3_specified_goods_total','Specified goods total'),
        ('4_number_of_items_price','Number of items for the price of '),
        ('5_discount_applied_specified_item','Discount applied to specified items'),], 'Type', required=1)
    product_id = fields.Many2one('product.product', 'Product service', domain=[('available_in_pos', '=', True)])
    discount_order_ids = fields.One2many('pos.promotion.discount.order', 'promotion_id', 'Discounts')
    reduction_order_ids = fields.One2many('pos.promotion.value.reduction.order', 'promotion_id', 'Reduction')
    specified_good_total_ids = fields.One2many('pos.promotion.specified.goods.total','promotion_id','Specified Goods Total')
    number_of_items_price_ids = fields.One2many('pos.promotion.number.items.price','promotion_id','Number of items for the price of ')
    discount_applied_specified_item_ids = fields.One2many('pos.promotion.discount.specified.item','promotion_id','Discount applied to specified items')

    @api.model
    def default_get(self, fields):
        res = super(pos_promotion, self).default_get(fields)
        products = self.env['product.product'].search([('name', '=', 'Promotion service')])
        if products:
            res.update({'product_id': products[0].id})
        return res

class pos_promotion_discount_order(models.Model):
    _name = "pos.promotion.discount.order"
    _order = "minimum_amount"

    minimum_amount = fields.Float('Amount total (without tax) greater or equal', required=1)
    discount = fields.Float('Discount %', required=1)
    promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)
    
class pos_promotion_value_reduction_order(models.Model):
    _name = "pos.promotion.value.reduction.order"
	
    minimum_amount = fields.Float('Amount total (without tax) greater or equal', required=1)
    value = fields.Float('Value Reduction', required=1)
    promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)

class pos_promotion_specified_goods_total(models.Model):
	_name = "pos.promotion.specified.goods.total"
	
	product_ids = fields.Many2many('product.product','promotion_specified_goods_total_rel','product_id','promotion_id','Specified Goods Total')
	price = fields.Float('Price Value')
	promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)
	
class pos_promotion_number_of_items_price(models.Model):
	_name = "pos.promotion.number.items.price"
	
	product_id = fields.Many2one('product.product','Product')
	buy_qty = fields.Float('Buy Quantity')
	offer_qty = fields.Float('Offer Quantity')
	promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)
	
class pos_promotion_discount_applied_specified_item(models.Model):
	_name = "pos.promotion.discount.specified.item"
	
	product_ids = fields.Many2many('product.product','promotion_discount_applied_specified_item_rel','product_id','promotion_id','Discount Applied Specified Items')
	product_id = fields.Many2one('product.product','Free Product')
	promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)
