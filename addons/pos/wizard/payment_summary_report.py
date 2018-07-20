import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

from datetime import datetime, date, time, timedelta
import time

class payment_report(models.TransientModel):
	_name = "payment.report"

	date = fields.Date('Date')
	day_shift = fields.Selection([('day','Day'),('shift','Shift')],'Day/Shift')
	shift_id = fields.Many2one('shift.master','Shift')
	payment_ids = fields.One2many('payment.line.report','payment_id','Payment Summary')
	
	@api.onchange('date','day_shift','shift_id')
	def onchange_date(self):
		pos_session_list = []
		if self.date and self.day_shift == 'day':
			pos_session_ids = self.env['pos.session'].search([('start_at','>=',self.date),('start_at','<=',self.date)])
			for session in pos_session_ids:
				for account in session.statement_ids:
					pos_session_list.append((0, 0, {'journal_id': account.journal_id.id, 'total': account.total_entry_encoding}))		
		elif self.date and self.day_shift == 'shift':
			pos_session_ids = self.env['pos.session'].search([('start_at','>=',self.date),('start_at','<=',self.date),('shift_id','=',self.shift_id.id)])
			for session in pos_session_ids:
				for account in session.statement_ids:
					pos_session_list.append((0, 0, {'journal_id': account.journal_id.id, 'total': account.total_entry_encoding}))
	
			
		self.payment_ids = pos_session_list
class payment_line_report(models.TransientModel):
	_name = "payment.line.report"

	journal_id = fields.Many2one('account.journal','Category')
	total = fields.Float('Revenue')
	payment_id = fields.Many2one('payment.report','Payment Summary')
