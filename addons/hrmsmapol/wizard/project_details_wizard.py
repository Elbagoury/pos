import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

import time
import datetime
from datetime import timedelta as td
from dateutil.relativedelta import *
from openerp import SUPERUSER_ID

class project_details(models.TransientModel):
	_name="project.details"
	
	category = fields.Selection([('project_wise', 'Project Wise'), ('employee_wise', 'Employee Wise')], 'Category')
	user_id = fields.Many2one('res.users', 'Employee')
	date = fields.Date('Date')
	project_id = fields.Many2one('project.project', 'Project')
	project_task_ids = fields.One2many('project.task.details', 'project_details_id', 'Project Details')
	employee_project_task_ids = fields.One2many('employee.project.task.details', 'project_details_id', 'Employee Task Details')
	
	@api.onchange('project_id')
	def on_change_project(self):
		if self.project_id:
			task_list = []
			for member in self.project_id.members:
				task_ids = self.env['project.task'].search([('project_id', '=',self.project_id.id), ('user_id', '=', member.id)])
				if task_ids:
					for task in task_ids:
						if task.stage_id.name == "In Progress" or task.stage_id.name == "Testing In Progress":
							task_list.append((0, 0, {'user_id': member.id, 'project_task_id': task.id, 'state': task.stage_id.name}))
								
				else:
					task_ids = self.env['project.task'].search([('user_id', '=', member.id)])
					if task_ids:
						for task in task_ids:
							if task.stage_id.name == "In Progress" or task.stage_id.name == "Testing In Progress":
								task_list.append((0, 0, {'user_id': member.id, 'project_task_id': task.id, 'state': "("+task.project_id.name+"-"+task.stage_id.name+")"}))
							
					else:
						task_list.append((0, 0, {'user_id': member.id, 'state': 'NO TASK'}))
			
			self.project_task_ids = task_list
	
	@api.onchange('date', 'user_id')
	def on_change_employee_task(self):
		if self.user_id:		
			if self.date:
				project_analytic = self.env['account.analytic.line'].search([('date','=',self.date),('user_id','=',self.user_id.id)])
				task_list = []
				for task in project_analytic:
					task_list.append((0, 0, {'project_id': task.project_id.id, 'project_task_id': task.task_id.id, 'description': task.name, 'duration':task.unit_amount}))
				self.employee_project_task_ids = task_list
				
			
class project_task_details(models.TransientModel):
	_name="project.task.details"
	
	user_id = fields.Many2one('res.users', 'Users')
	project_task_id = fields.Many2one('project.task','Tasks')
	state = fields. Char('State')
	project_details_id = fields.Many2one('project.details', 'Project Details')

class employee_project_task_details(models.TransientModel):
	_name="employee.project.task.details"

	project_id = fields.Many2one('project.project','Projects')
	project_task_id = fields.Many2one('project.task','Tasks')
	description = fields.Char('Description')
	duration = fields.Float('Duration')
	project_details_id = fields.Many2one('project.details', 'Project Details')
	
class employee_absent_list(models.TransientModel):
	_name="employee.absent.list"
	
	employee_id = fields.Many2one('hr.employee')
	date_from = fields.Date('Date From')
	date_to = fields.Date('Date To')
	employee_leave_ids = fields.One2many('employee.leave', 'employee_absent_id', 'Leave Details')
	
	@api.onchange('date_to','employee_id')
	def onchange_date(self):
		if self.employee_id:
			if self.date_from and self.date_to:
				holidays = self.env['hr.holidays.status'].search([('name','=','holiday')])
				start_date = self.date_from
				end_date = self.date_to
				date_start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
				date_end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
				leave_list = []
				while date_start <= date_end:
					sunday = date_start.weekday()
					running_date = datetime.date.strftime(date_start, "%Y-%m-%d")
					if sunday != 6:
						self.env.cr.execute("""select DISTINCT DATE(check_in) from hr_attendance where check_in::date = %s and employee_id = %s""",(running_date, self.employee_id.id))
						if not self.env.cr.dictfetchall():
							if not self.env['hr.holidays'].search([('holiday_date','=',running_date),('holiday_status_id','=',holidays.id)]):
								leave_list.append((0, 0, {'leave_date': running_date, 'reason': 'Leave'}))
					date_start = date_start + datetime.timedelta(days=1)
				self.employee_leave_ids = leave_list
					
class employee_leave(models.TransientModel):
	_name="employee.leave"
	
	leave_date = fields.Date("Leave Date")
	reason = fields.Char("Leave")
	employee_absent_id = fields.Many2one('employee.absent.list', 'Leave Details')
