import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

import datetime
import dateutil.relativedelta

from datetime import datetime, date, time, timedelta

import time
import dateutil

class hr_holidays(models.Model):
	_name = "hr.holidays"
	_inherit = "hr.holidays"
	
	holiday_date = fields.Date('Date of Holiday', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}, select=True)
	is_academic_holidays = fields.Boolean(string='Is Academic Holidays')
	
	@api.model
	def default_get(self, fields):
		res = super(hr_holidays, self).default_get(fields)
		
		if 'is_academic_holidays' in self._context and self._context['is_academic_holidays'] is True:
			res['is_academic_holidays'] = True
			res['holiday_type'] = 'category'
		return res
	
	@api.onchange('holiday_date')
	def onchange_holiday_date(self):
		if self.holiday_date:
			holiday_date_start = self.holiday_date + ' 00:00:00'
			holiday_date_end = self.holiday_date + ' 23:59:59'
			holiday_date_start_in_time = datetime.strptime(holiday_date_start, "%Y-%m-%d %H:%M:%S")
			holiday_date_end_in_time = datetime.strptime(holiday_date_end, "%Y-%m-%d %H:%M:%S")
			date_from = str(holiday_date_start_in_time - timedelta(0,19800))
			date_to = str(holiday_date_end_in_time - timedelta(0,19800))
			self.date_from = date_from
			self.date_to = date_to
		else:
			self.date_from = False
			self.date_to = False 
