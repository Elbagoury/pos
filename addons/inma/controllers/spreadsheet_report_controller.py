from openerp import http
from openerp.http import request
from odoo.api import call_kw, Environment

from openerp.addons.web.controllers.main import serialize_exception,content_disposition
import base64


class spreadsheet_report_controller(http.Controller):
	
	_cp_path = '/inma'
	
	@http.route('/inma/spreadsheet_report_controller/download_document', type='http', auth="public")
	@serialize_exception
	def download_document(self,model,field,id,filename=None, **kw):
		
		""" Download link for files stored as binary fields.
		:param str model: name of the model to fetch the binary from
		:param str field: binary field
		:param str id: id of the record from which to fetch the binary
		:param str filename: field holding the file's name, if any
		:returns: :class:`werkzeug.wrappers.Response`
		"""

		Model = request.env[model]
		attachment = Model.sudo().search_read(
           [('id', '=', int(id))],
           ["name", "file_f", "res_model", "res_id", "type", "url"])[0]
		filecontent = base64.b64decode(attachment.get('file_f') or '')
		if not filecontent:
		   return request.not_found()
		else:
		   if filename:

			   return request.make_response(filecontent,
                               [('Content-Type', 'application/octet-stream'),
                               ('Content-Disposition', content_disposition(filename))])



    
        
