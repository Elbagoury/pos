from odoo import api, fields, models
from odoo import tools, _

class generate_lot(models.TransientModel):
    _name = 'generate.lot'

    product_id = fields.Many2one('product.product','Product')
    count = fields.Integer('Count')

    def generate(self):
        lot = self.env['stock.production.lot']
        if self.product_id:
            for i in range(1, self.count+1):
                lot.create({'name': str(i),'product_id':self.product_id.id, 'product_qty':1})

    