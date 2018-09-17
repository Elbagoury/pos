import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError

class assert_report(models.TransientModel):
    _name = 'assert.report'

    location = fields.Many2one('bt.asset.location','Location')
    state = fields.Selection([('active', 'Active'),
            ('scrapped', 'Scrapped'), ('inactive','In Active'),('repair','Under Repair'),('maintenance','Under Maintenance')], 'State')
    asset_ids = fields.One2many('assert.report.line','asset_id','Assets')

    @api.onchange('date','location','state')
    def onchange_state(self):
        asset_list = []
        if self.location and self.state:
            asset_ids_sr = self.env['bt.asset'].search([('current_loc_id','=',self.location.id),('state','=',self.state)])
            for asset in asset_ids_sr:
                asset_list.append((0, 0, {'date':asset.write_date,'name':asset.id,'model_name':asset.model_name}))
            self.asset_ids = asset_list
class assert_report_line(models.TransientModel):
    _name = 'assert.report.line'

    date = fields.Date('Date')
    name = fields.Many2one('bt.asset','Asset')
    model_name = fields.Char(string='Model Name')
    asset_id = fields.Many2one('assert.report','Asset')