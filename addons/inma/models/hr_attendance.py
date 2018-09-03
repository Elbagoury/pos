
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.safe_eval import safe_eval
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

from datetime import datetime, date, time, timedelta

class employee_attendance(models.Model):
	_name = 'employee.attendance'

	date = fields.Date("Date", default = fields.Date.context_today)
	shift = fields.Selection([('day','Day'),('night','Night'),('day_night','Day/Night')],'Shift')
	department_id = fields.Many2one('hr.department','Department')
	employee_attendance_line_ids = fields.One2many('employee.attendance.line','employee_attendance_id','Attendance')

	_sql_constraints = [
                        ('date_staff_id_department_id_shift_uniq', 'unique(date, department_id, shift)', 'Duplication attempt')
                       ]

	@api.onchange('department_id','shift')
	def onchange_department_id(self):
		if self.department_id and self.shift:
			employees = self.env['hr.employee'].search([('department_id','=',self.department_id.id),('work_base','=','day_basis')], order='name asc')
			employees_dict = []
			if self.shift == 'day':
				for employee in employees:
						employees_dict.append((0, 0, {'employee_id': employee.id, 'id_no': employee.cid, 'category_id':employee.category_id.id, 'shift':self.shift, 'day_shift':True}))
			elif self.shift == 'night':
				for employee in employees:
						employees_dict.append((0, 0, {'employee_id': employee.id, 'id_no': employee.cid, 'category_id':employee.category_id.id, 'shift':self.shift, 'night_shift':True}))
			elif self.shift == 'day_night':
				for employee in employees:
						employees_dict.append((0, 0, {'employee_id': employee.id, 'id_no': employee.cid, 'category_id':employee.category_id.id, 'shift':self.shift, 'day_shift':True, 'night_shift':True}))

			self.employee_attendance_line_ids = employees_dict

	@api.one
	@api.constrains('employee_attendance_line_ids')
	def constraint_attendance_line(self):
		if self.employee_attendance_line_ids:
			return True
		else:
			raise ValidationError(_("Enter Employee Attendance"))

	@api.constrains('date')
	@api.onchange('date')
	def onchange_date(self):
		today_date = datetime.today().strftime('%Y-%m-%d')
		if self.date:
			if self.date > today_date:
				raise ValidationError(_("Future Date should not allowed in Attendance"))

class employee_attendance_line(models.Model):
	_name = 'employee.attendance.line'

	employee_id = fields.Many2one('hr.employee','Employee')
	id_no = fields.Char('Id No')
	category_id = fields.Many2one('hr.employee.category','Category')
	day_shift = fields.Boolean('Day')
	night_shift = fields.Boolean('Night')
	shift = fields.Selection([('day','Day'),('night','Night'),('day_night','Day/Night')],'Shift')
	job_allocation = fields.Char('Job Allocation')
	employee_attendance_id = fields.Many2one('employee.attendance','Employee Attendance')

class workbase_employee(models.Model):
	_name = 'workbase.employee'

	date = fields.Date("Date", default = fields.Date.context_today)
	workbase_employee_line_ids = fields.One2many('workbase.employee.line','workbase_employee_id','Attendance')

	_sql_constraints = [
        ('date_uniq', 'unique(date)', 'Already Same date attendance created'),
        ]

	@api.onchange('date')
	def onchange_date(self):
		if self.date:
			today_date = datetime.today().strftime('%Y-%m-%d')
			if self.date > today_date:
				raise ValidationError(_("Future Date should not allowed in Attendance"))
			else:
				employees = self.env['hr.employee'].search([('work_base','=','hour_basis')], order='name asc')
				employees_dict = []
				for employee in employees:
					employees_dict.append((0, 0, {'employee_id': employee.id, 'id_no': employee.cid, 'category_id':employee.category_id.id}))
				self.workbase_employee_line_ids = employees_dict

	@api.constrains('date')
	def constraint_date(self):
		if self.date:
			today_date = datetime.today().strftime('%Y-%m-%d')
			if self.date > today_date:
				raise ValidationError(_("Future Date should not allowed in Attendance"))

	@api.one
	@api.constrains('workbase_employee_line_ids')
	def constraint_attendance_line(self):
		if self.workbase_employee_line_ids:
			return True
		else:
			raise ValidationError(_("Enter Employee Attendance"))

	#@api.model
	#def create(self,vals):
		#if vals.get('workbase_employee_line_ids'):
			#for line in vals.get('workbase_employee_line_ids'):
				#fore_total = abs(line.forenoon_start_time - line.forenoon_end_time)
				#noon_total = abs(line.afnoon_start_time-line.afnoon_end_time)
				#total = fore_total + noon_total
				#total_hours = total + line.extra_hours
				#line.write({'total_hours_worked':total, 'total_hours':total_hours})
		#return super(workbase_employee, self).create(vals)

class workbase_employee_line(models.Model):
	_name = 'workbase.employee.line'

	employee_id = fields.Many2one('hr.employee','Employee')
	id_no = fields.Char('Id No')
	category_id = fields.Many2one('hr.employee.category','Category')
	forenoon_start_time = fields.Float('Forenoon Start Time')
	forenoon_end_time = fields.Float('Forenoon End Time')
	afnoon_start_time = fields.Float('Afternoon Start Time')
	afnoon_end_time = fields.Float('Afternoon End Time')
	total_hours_worked = fields.Float('Total Hours Worked')
	extra_hours = fields.Float('Extra Hours')
	total_hours = fields.Float('Total Hours')
	remarks = fields.Text('Remarks')
	workbase_employee_id = fields.Many2one('workbase.employee','Work Base Employee')

	@api.onchange('forenoon_start_time','forenoon_end_time','afnoon_start_time','afnoon_end_time','extra_hours')
	def onchange_time(self):
		if self.forenoon_start_time:
			fore_total = abs(self.forenoon_start_time - self.forenoon_end_time)
			noon_total = abs(self.afnoon_start_time - self.afnoon_end_time)
			total = fore_total + noon_total
			#result = '{0:02.0f}:{1:02.0f}'.format(*divmod(total * 60, 60))
			
			if total > 8:
				self.total_hours_worked = 8
				self.extra_hours = total - 8
			else:
				self.total_hours_worked = total
				self.extra_hours = 0
				self.total_hours = total
			if self.extra_hours:
				self.total_hours = self.total_hours_worked + self.extra_hours

	@api.onchange('extra_hours')
	def onchange_extrahours(self):
		if self.extra_hours:
			self.total_hours = self.total_hours_worked + self.extra_hours

	#@api.multi
	#def write(self,vals):
		#employees_dict = []
		#for employee in self:
			#fore_total = abs(employee.forenoon_start_time - employee.forenoon_end_time)
			#noon_total = abs(employee.afnoon_start_time-employee.afnoon_end_time)
			#total_hours_worked = fore_total + noon_total
			#total_hours = total_hours_worked + employee.extra_hours
			#vals['total_hours_worked'] = total_hours_worked
			#vals['total_hours'] = total_hours
			##employees_dict.append((0, 0, {'total_hours_worked': total_hours_worked, 'total_hours': total_hours}))
		#return super(workbase_employee_line, self).write(vals)

