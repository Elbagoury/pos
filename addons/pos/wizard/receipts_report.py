import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

from datetime import datetime, date, time, timedelta
import time

class reciepts_report(models.TransientModel):
	_name = "reciepts.report"

	date = fields.Date('Date')
	day_shift = fields.Selection([('day','Day'),('shift','Shift')],'Day/Shift')
	shift_id = fields.Many2one('shift.master','Shift')
	reciepts_ids = fields.One2many('reciepts.line.report','reciept_id','Reciepts')
	
	@api.onchange('date','day_shift','shift_id')
	def onchange_date(self):
		pos_session_list = []
		if self.date and self.day_shift == 'day':
			pos_session_ids = self.env['pos.session'].search([('start_at','>=',self.date),('start_at','<=',self.date)])
			for session in pos_session_ids:
				for account in session.statement_ids:
					pos_session_list.append((0, 0, {'payment_id': account.journal_id.id, 'pos': account.total_entry_encoding}))		
		elif self.date and self.day_shift == 'shift':
			pos_session_ids = self.env['pos.session'].search([('start_at','>=',self.date),('start_at','<=',self.date),('shift_id','=',self.shift_id.id)])
			for session in pos_session_ids:
				for account in session.statement_ids:
					pos_session_list.append((0, 0, {'payment_id': account.journal_id.id, 'pos': account.total_entry_encoding}))
	
			
		self.reciepts_ids = pos_session_list
	
			
class reciepts_line_report(models.TransientModel):
	_name = "reciepts.line.report"

	payment_id = fields.Many2one('account.journal','Category')
	pos = fields.Float('POS')
	reciept_id = fields.Many2one('reciepts.report','Reciepts')
