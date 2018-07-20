import openerp.http as http
from openerp.http import request
from odoo.api import call_kw, Environment
import logging
from odoo import api, fields, models
from odoo import tools, _

from openerp.addons.web.controllers.main import serialize_exception,content_disposition
import base64
_logger = logging.getLogger(__name__)

class getmethodcontroller(http.Controller):
	_cp_path = '/pos'
	
	@http.route('/pos/getmethodcontroller/get_request_from_dom', type='http', auth='none')
	def get_request_from_dom(self, name, image_f, pump_value, **kw):
		filecontent = base64.b64decode(image_f or '')
		if name:
			nozle_id = request.env['dom.nozle'].sudo().search([('name','=',name)])
			nozle_state = nozle_id.state
			nozle_id.write({'state':'requested'})
			nozle_id.newstate = nozle_id.state
		name = nozle_state + "\tto\t" +nozle_id.newstate	
		return "<h1>%s</h1>"% name

	@http.route('/pos/getmethodcontroller/check_dom_approve_or_denied', type='http', auth='none')
	def check_dom_approve_or_denied(self, name, **kw):
		name = "Nozle:" + name		
		return "<h1>Approve %s</h1>"% name
		
	@http.route('/pos/getmethodcontroller/get_request_from_dom_make_order', type='http', auth='none')
	def get_request_from_dom_make_order(self, name, qty, **kw):
		name = "Nozle:" + name + "Qty:"+qty			
		return "<h1>Make Order %s</h1>"% name
