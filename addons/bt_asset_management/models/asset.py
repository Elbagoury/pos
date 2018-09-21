# -*- coding: utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2016-BroadTech IT Solutions (<http://www.broadtech-innovations.com/>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.exceptions import ValidationError
from odoo import tools
from email import _name
import string
from datetime import datetime, date, time, timedelta


class BtAsset(models.Model):   
    _name = "bt.asset"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Asset" 
    
    @api.multi
    def _get_default_location(self):
        obj = self.env['bt.asset.location'].search([('default','=',True)])
        if not obj:
            raise Warning(_("Please create asset location first"))
        loc = obj[0]
        return loc 
    
    name = fields.Char(string='Name', required=True)
    purchase_date = fields.Date(string='Purchase Date',track_visibility='always')
    purchase_value = fields.Float(string='Purchase Value', track_visibility='always')
    asset_code = fields.Char(string='Asset Code')
    is_created = fields.Boolean('Created', copy=False)
    current_loc_id = fields.Many2one('bt.asset.location', string="Current Location", default=_get_default_location, required=True)
    model_name = fields.Char(string='Model Name')
    serial_no = fields.Char(string='Serial No', track_visibility='always')
    manufacturer = fields.Char(string='Manufacturer')
    warranty_start = fields.Date(string='Warranty Start')
    warranty_end = fields.Date(string='Warranty End')
    category_id = fields.Many2one('bt.asset.category', string='Category Id')
    note = fields.Text(string='Internal Notes')
    state = fields.Selection([
            ('active', 'Active'),
            ('scrapped', 'Scrapped'), ('inactive','In Active'),('repair','Under Repair'),('maintenance','Under Maintenance')], string='State',track_visibility='onchange', default='active', copy=False)
    image = fields.Binary("Image", attachment=True,
        help="This field holds the image used as image for the asset, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized image", attachment=True,
        help="Medium-sized image of the asset. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved, "\
             "only when the image exceeds one of those sizes. Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image", attachment=True,
        help="Small-sized image of the asset. It is automatically "\
             "resized as a 64x64px image, with aspect ratio preserved. "\
             "Use this field anywhere a small image is required.")
    description = fields.Char('Description')
    is_vechile = fields.Boolean('Vechile')
    vechile_detail_ids = fields.One2many('vechile.details','asset_id','Vechile Status')
    asset_log_ids = fields.One2many('asset.log','asset_log_id','Assets')
    
    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        vals.update({'is_created':True})
        lot = super(BtAsset, self).create(vals)
        lot.message_post(body=_("Asset %s created with asset code %s")% (lot.name,lot.asset_code))
        return lot
    
    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        lot = super(BtAsset, self).write(vals)
        return lot
    
    @api.multi
    def action_move_vals(self):
        for asset in self:
            location_obj = self.env['bt.asset.location'].search([('default_scrap','=',True)])
            if not location_obj:
                raise Warning(_("Please set scrap location first"))
            move_vals = {
                'from_loc_id' : asset.current_loc_id.id,
                'asset_id' : asset.id,
                'to_loc_id' : location_obj.id
                }
            asset_log = [(0, 0, {'state_from': asset.state,'state_to': 'scrapped','user_id': asset._uid,'changed_on': datetime.now()})]
            asset_move = self.env['bt.asset.move'].create(move_vals)
            asset_move.action_move()
            asset.current_loc_id = location_obj.id
            asset.state = 'scrapped'
            if asset.state == 'scrapped':
                asset.message_post(body=_("Scrapped"))
			
            asset.write({'asset_log_ids': asset_log})

        return True 

    @api.one
    def action_inactive(self):
        
        asset_log = [(0, 0, {'state_from': self.state,'state_to': 'inactive','user_id': self._uid,'changed_on': datetime.now()})]
        self.write({'state':'inactive','asset_log_ids':asset_log})

    @api.one
    def action_repair(self):
        asset_log = [(0, 0, {'state_from': self.state,'state_to': 'repair','user_id': self._uid,'changed_on': datetime.now()})]
        self.write({'state':"repair",'asset_log_ids':asset_log})
        
    @api.one
    def action_maintenance(self):
        
        asset_log = [(0, 0, {'state_from': self.state,'state_to': 'maintenance','user_id': self._uid,'changed_on': datetime.now()})]
        self.write({'state':"maintenance",'asset_log_ids':asset_log})

    @api.one
    def action_active(self):
        
        asset_log = [(0, 0, {'state_from': self.state,'state_to': 'active','user_id': self._uid,'changed_on': datetime.now()})]
        self.write({'state':"active",'asset_log_ids':asset_log})  

class BtAssetLocation(models.Model):   
    _name = "bt.asset.location"
    _description = "Asset Location" 
    
    name = fields.Char(string='Name', required=True)
    asset_ids = fields.One2many('bt.asset','current_loc_id', string='Assets')
    default = fields.Boolean('Default', copy=False)
    default_scrap = fields.Boolean('Scrap')
    
    @api.model
    def create(self, vals):
        result = super(BtAssetLocation, self).create(vals)
        obj = self.env['bt.asset.location'].search([('default','=',True)])
        asset_obj = self.env['bt.asset.location'].search([('default_scrap','=',True)])
        if len(obj) > 1 or len(asset_obj) > 1:
            raise ValidationError(_("Default location have already set."))
        return result
    
    @api.multi
    def write(self, vals):
        res = super(BtAssetLocation, self).write(vals)
        obj = self.env['bt.asset.location'].search([('default','=',True)])
        asset_obj = self.env['bt.asset.location'].search([('default_scrap','=',True)])
        if len(obj) > 1 or len(asset_obj) > 1:
            raise ValidationError(_("Default location have already set."))
        return res

class BtAssetCategory(models.Model): 
    _name = "bt.asset.category"
    _description = "Asset Category"
    
    name = fields.Char(string='Name', required=True)  
    categ_no = fields.Char(string='Category No')
    description = fields.Char('Description')

class vechile_details(models.Model):
    _name = "vechile.details"

    name = fields.Char('Vechile Name')
    vechile_no = fields.Char('Vechile No')
    vechile_validation_ids = fields.One2many('vechile.validation','vechile_detail_id','Vechile Detail')
    asset_id = fields.Many2one('bt.asset','Asset')

class vechile_validation(models.Model):
    _name = "vechile.validation"

    vechile_valid = fields.Selection([('registration','Registration'),('insurance','Insurance'),('permit','Permit'),('fitness','Fitness'),('road_tax','Road Tax'),('pollution','Pollution'),('others','Others')],'Vechile Document')
    valid_from = fields.Date('Valid From')
    valid_to = fields.Date('Valid To')
    is_copy = fields.Boolean('Copy Available')
    copy_attach = fields.Binary('Attachment')
    vechile_detail_id = fields.Many2one('vechile.details','Vechile')


class asset_log(models.Model):
	_name = "asset.log"    
	_description = 'Change Log'
    
	user_id = fields.Many2one('res.users', 'Changed By', readonly=True)
	state_from = fields.Selection([('active', 'Active'),
            ('scrapped', 'Scrapped'), ('inactive','In Active'),('repair','Under Repair'),('maintenance','Under Maintenance')], 'From', readonly=True)
	state_to = fields.Selection([('active', 'Active'),
            ('scrapped', 'Scrapped'), ('inactive','In Active'),('repair','Under Repair'),('maintenance','Under Maintenance')], 'To', readonly=True)
	changed_on = fields.Datetime('Changed On', readonly=True)
	asset_log_id = fields.Many2one('bt.asset', 'Change')

# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:  