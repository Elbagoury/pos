# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://opensource.org/licenses/LGPL-3.0).
#
#This software and associated files (the "Software") may only be used (executed,
#modified, executed after modifications) if you have purchased a valid license
#from the authors, typically via Odoo Apps, or if you have received a written
#agreement from the authors of the Software (see the COPYRIGHT section below).
#
#You may develop Odoo modules that use the Software as a library (typically
#by depending on it, importing it and using its resources), but without copying
#any source code or material from the Software. You may distribute those
#modules under the license of your choice, provided that this license is
#compatible with the terms of the Odoo Proprietary License (For example:
#LGPL, MIT, or proprietary licenses similar to this one).
#
#It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#or modified copies of the Software.
#
#The above copyright notice and this permission notice must be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#DEALINGS IN THE SOFTWARE.
#
#########COPYRIGHT#####
# © 2016 Bernard K Too<bernard.too@optima.co.ke>

import logging
_logger = logging.getLogger(__name__)

from odoo.http import route, request
from odoo.addons.web.controllers.main import content_disposition
from odoo.addons.report.controllers.main import ReportController
import json

class DownloadedReportFilename(ReportController):

	@route(['/report/download'], type='http', auth="user")
    	def report_download(self, data, token):
            """This function is used by 'qwebactionmanager.js' in order to trigger the download of
            a pdf/controller report.

            :param data: a javascript array JSON.stringified containg report internal url ([0]) and
            type [1]
            :returns: Response with a filetoken cookie and an attachment header
            """
	    response = super(DownloadedReportFilename, self).report_download(data, token)

	    requestcontent = json.loads(data)
            url, type = requestcontent[0], requestcontent[1]
            if type == 'qweb-pdf':
		   reportname = url.split('/report/pdf/')[1].split('?')[0]
		   docids = None
                   if '/' in reportname:
                       reportname, docids = reportname.split('/')

                   report = request.env['report']._get_report_from_name(reportname)
		   xreport =None
                   if docids and len(docids) == 1:
                      # Generic report:
                      xreport = request.env[report.model].browse([int(docids)])
		   filename = None
		   if xreport:
			if report.model == 'account.invoice' and xreport.number:
			   filename = ( (xreport.type in ['out_invoice'] and 'Invoice' or 'Bill') + 
				      '-' + xreport.number.replace(' ','_').replace('/', '_' ))
			elif report.model == 'purchase.order' and xreport.name:
			   filename = ( (xreport.state in ['draft', 'sent', 'to approve'] and 'RFQ' or 'Purchase_Order') + 
				       '-' + xreport.name.replace(' ', '_' ).replace('/', '_' ))
			elif report.model == 'sale.order' and xreport.name:
			   filename = ( (xreport.state in ['draft', 'sent'] and 'Quotation' or 'Sale_Order') + 
				       '-' + xreport.name.replace(' ', '_' ).replace('/', '_' ))
			elif report.model in ['stock.inventory','res.partner','mrp.production', 'stock.picking', 'stock.production.lot', 'stock.quant.package'] and xreport.name:
			   filename = ( report.name.replace(' ','_').replace('/', '_' ) + 
				       '-' +xreport.name.replace(' ', '_' ).replace('/', '_' ))
			else:
			    filename = ( report.name.replace(' ','_').replace('/', '_' ))
					
		   if filename:
		      filename = '{}.pdf'.format(filename)
		      response.headers.remove('Content-Disposition')
		      response.headers.add('Content-Disposition', content_disposition(filename))

	    return response

