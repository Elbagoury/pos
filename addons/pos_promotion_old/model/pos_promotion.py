# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class pos_promotion(models.Model):
    _name = "pos.promotion"
    
    @api.model
    def create(self, values):
        res = super(pos_promotion, self).create(values)
        if res.gift_condition_ids:
            gift_condition_ids = len(res.gift_condition_ids)
            for price in res.gift_condition_ids:
                if res.gift_free_ids:
                    gift_free_ids =len(res.gift_free_ids)
                    free_total_amount = 0.0
                    for free in res.gift_free_ids:
                        free_total_amount += (free.product_id.mrp * free.quantity_free)
                        total_length = gift_free_ids + gift_condition_ids
                        add_gift_price = free_total_amount / total_length
                        price.add_gift_price = add_gift_price/price.minimum_quantity
                        free.add_gift_price = add_gift_price
        return res
    
    @api.multi
    def write(self, values):
        res = super(pos_promotion, self).write(values)
        if self.gift_condition_ids:
            gift_condition_ids = len(self.gift_condition_ids)
            for price in self.gift_condition_ids:
                if self.gift_free_ids:
                    gift_free_ids =len(self.gift_free_ids)
                    free_total_amount = 0.0
                    for free in self.gift_free_ids:
                        free_total_amount += (free.product_id.mrp * free.quantity_free)
                        total_length = gift_free_ids + gift_condition_ids
                        add_gift_price = free_total_amount / total_length
                        price.add_gift_price = add_gift_price/price.minimum_quantity
                        free.add_gift_price = add_gift_price
        return res


    name = fields.Char('Name', required=1)
    active = fields.Boolean('Active', default=1)
    start_date = fields.Datetime('Start date', default=fields.Datetime.now(), required=1)
    end_date = fields.Datetime('End date', required=1)
    type = fields.Selection([
        ('1_discount_total_order', 'Discount on total order'),
        ('2_discount_category', 'Discount on categories'),
        ('3_discount_by_quantity_of_product', 'Discount by quantity of product'),
        ('4_pack_discount', 'By pack products discount products'),
        ('5_pack_free_gift', 'By pack products free products'),
        ('6_price_filter_quantity', 'Price product filter by quantity'),
    ], 'Type', required=1)
    product_id = fields.Many2one('product.product', 'Product service', domain=[('available_in_pos', '=', True)])
    discount_order_ids = fields.One2many('pos.promotion.discount.order', 'promotion_id', 'Discounts')
    discount_category_ids = fields.One2many('pos.promotion.discount.category', 'promotion_id', 'Discounts')
    discount_quantity_ids = fields.One2many('pos.promotion.discount.quantity', 'promotion_id', 'Discounts')
    gift_condition_ids = fields.One2many('pos.promotion.gift.condition', 'promotion_id', 'Gifts condition')
    gift_free_ids = fields.One2many('pos.promotion.gift.free', 'promotion_id', 'Gifts apply')
    discount_condition_ids = fields.One2many('pos.promotion.discount.condition', 'promotion_id', 'Discounts condition')
    discount_apply_ids = fields.One2many('pos.promotion.discount.apply', 'promotion_id', 'Discounts apply')
    price_ids = fields.One2many('pos.promotion.price', 'promotion_id', 'Prices')

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


class pos_promotion_discount_category(models.Model):
    _name = "pos.promotion.discount.category"
    _order = "category_id, discount"

    category_id = fields.Many2one('pos.category', 'POS Category', required=1)
    discount = fields.Float('Discount %', required=1)
    promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)


class pos_promotion_discount_quantity(models.Model):
    _name = "pos.promotion.discount.quantity"
    _order = "product_id"

    product_id = fields.Many2one('product.product', 'Product', domain=[('available_in_pos', '=', True)], required=1)
    quantity = fields.Float('Minimum quantity', required=1)
    discount = fields.Float('Discount %', required=1)
    promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)


class pos_promotion_gift_condition(models.Model):
    _name = "pos.promotion.gift.condition"
    _order = "product_id, minimum_quantity"
    
    
    product_id = fields.Many2one('product.product', domain=[('available_in_pos', '=', True)], string='Product',required=1)
    minimum_quantity = fields.Float('Qty greater or equal', required=1, default=1.0)
    promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)
    add_gift_price = fields.Float('Gift price % ', required=1, default=1.0)


class pos_promotion_gift_free(models.Model):
    _name = "pos.promotion.gift.free"
    _order = "product_id"

    product_id = fields.Many2one('product.product', domain=[('available_in_pos', '=', True)], string='Product gift',required=1)
    quantity_free = fields.Float('Quantity free', required=1, default=1.0)
    promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)
    add_gift_price = fields.Float('Gift price % ', required=1, default=1.0)

class pos_promotion_discount_condition(models.Model):
    _name = "pos.promotion.discount.condition"
    _order = "product_id, minimum_quantity"

    product_id = fields.Many2one('product.product', domain=[('available_in_pos', '=', True)], string='Product', required=1)
    minimum_quantity = fields.Float('Qty greater or equal', required=1, default=1.0)
    promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)


class pos_promotion_discount_apply(models.Model):
    _name = "pos.promotion.discount.apply"
    _order = "product_id"

    product_id = fields.Many2one('product.product', domain=[('available_in_pos', '=', True)], string='Product', required=1)
    discount = fields.Float('Discount %', required=1, default=1.0)
    promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)


class pos_promotion_price(models.Model):
    _name = "pos.promotion.price"
    _order = "product_id, minimum_quantity"

    product_id = fields.Many2one('product.product', domain=[('available_in_pos', '=', True)], string='Product', required=1)
    minimum_quantity = fields.Float('Qty greater or equal', required=1)
    list_price = fields.Float('List Price', required=1)
    promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)
    
    
#class product_template(models.Model):
    
    #_inherit='product.template'
    
    #is_promotion = fields.Boolean("Promotion")
    #gift_price_amount = fields.Float("Extra Amount")        

#class product_product(models.Model):
    
    #_inherit='product.product'
    
    #is_promotion = fields.Boolean("Promotion")
    #gift_price_amount = fields.Float("Extra Amount")
