from odoo import api, models, fields, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

from datetime import datetime, date, time, timedelta
import time
from odoo.exceptions import ValidationError

class TankChangeQuantity(models.TransientModel):
    _name = "stock.change.tank.qty"
    _description = "Change Tank Quantity"
    
    # TDE FIXME: strange dfeault method, was present before migration ? to check
    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_tmpl_id = fields.Many2one('product.template', 'Template', required=True)
    product_variant_count = fields.Integer('Variant Count', related='product_tmpl_id.product_variant_count')
    new_quantity = fields.Float(
        'New Quantity on Hand', default=1,
        digits=dp.get_precision('Product Unit of Measure'), required=True,
        help='This quantity is expressed in the Default Unit of Measure of the product.')
    
    tank_id = fields.Many2one('tank.master', 'Tank', required=True)

    @api.model
    def default_get(self, fields):
        res = super(TankChangeQuantity, self).default_get(fields)
        if not res.get('product_id') and self.env.context.get('active_id') and self.env.context.get('active_model') == 'product.template' and self.env.context.get('active_id'):
            res['product_id'] = self.env['product.product'].search([('product_tmpl_id', '=', self.env.context['active_id'])], limit=1).id
        elif not res.get('product_id') and self.env.context.get('active_id') and self.env.context.get('active_model') == 'product.product' and self.env.context.get('active_id'):
            res['product_id'] = self.env['product.product'].browse(self.env.context['active_id']).id
        return res
       
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_tmpl_id = self.onchange_product_id_dict(self.product_id.id)['product_tmpl_id']
    
    def onchange_product_id_dict(self, product_id):
        return {
            'product_tmpl_id': self.env['product.product'].browse(product_id).product_tmpl_id.id,
        }
   
    @api.multi
    def change_tank_qty(self):
        """ Changes the Product Quantity by making a Physical Inventory. """
        
        tank_log = self.env['tank.log']
        
        for wizard in self:
	    #tank_master_id =self.env['tank.master'].search([('id','=',wizard.tank_id.id),('tank_type','=',wizard.product_id.id)])
            #tank_master_id.available_fuel += wizard.new_quantity
            shift_id = self.env['shift.day.master'].search([('date_from','<=', fields.Datetime.now()),('date_to','>=',fields.Datetime.now())])
	    if shift_id:	
		    tank_log = tank_log.create({
		        'date': fields.Datetime.now(),
		        'product_id': wizard.product_id.id,
		        'tank_id': wizard.tank_id.id,
		        'qty': wizard.new_quantity,
		        'shift_id':shift_id.name.id
		    })
	    else:
		   raise ValidationError(_("First Active the current day shift"))

        return {'type': 'ir.actions.act_window_close'}

