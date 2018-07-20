# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.osv import expression
from openerp.tools.float_utils import float_round as round
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import UserError, ValidationError
from openerp import api, fields, models, _

import dateutil.relativedelta
import dateutil.parser
import calendar


from datetime import datetime, date, time, timedelta
import time
import dateutil
import base64
import sys

from email import _name
from openerp.http import request
import httplib
import json
from dateutil.relativedelta import relativedelta




def date_indian(date):
    date_split = date.split('-')
    date_indian = date_split[2]+'/'+date_split[1]+'/'+date_split[0] 
    return date_indian

class Employee(models.Model):


    _name = "hr.employee"
    _description = "Employee"
    _inherit = "hr.employee"


    corporate_code =  fields.Char('Corporate Code', size=64, required=True)
    employee_code =  fields.Char('Employee Code', size=64, required=True)
    employee_basic_details_id = fields.One2many('emp.basic.details', 'employee_id', 'Employee Basic Details') 
    employee_address_details_id = fields.One2many('emp.address', 'employee_id', 'Employee Address Details')  	    
    employee_personal_details_id = fields.One2many('emp.personal.details', 'employee_id', 'Employee Personal Details') 	
    hr_academic_record_id = fields.One2many('hr.academic.record', 'employee_id', 'Academic Records')  	
    hr_experience_id = fields.One2many('hr.experience', 'employee_id', 'Experience')  	
    hr_insurance_id = fields.One2many('hr.insurance', 'employee_id', 'Insurance')  		
    hr_family_id = fields.One2many('hr.family', 'employee_id', 'Family')    
    emp_salary_id = fields.One2many('emp.salary', 'employee_id', 'Salary')  	    
        



class EmployeeBasicDetails(models.Model):
    
    _name = "emp.basic.details"
    _description = "Employee Basic Details"

    date_of_birth = fields.Date('Date Of Birth')
    age = fields.Char('Age', size=12)
    gender = fields.Selection([('male','Male'), ('female','Female')], 'Gender')
    father_name =  fields.Char('Father Name', size=24)
    occupation =  fields.Char('Occupation', size=24)
    marital_status =  fields.Selection([('single', 'SINGLE'), ('married', 'MARRIED'), ('divorced', 'DIVORCED'), ('widowed', 'WIDOWED')], 'Marital Status')
    category_id = fields.Many2one('hr.employee.category', string='Employee Category', index=True)
    date_of_joining = fields.Date('Date Of Joining*')						
    date_of_confirmation = fields.Date('Date Of Confirmation')						
    employee_id = fields.Many2one('hr.employee','Employee ID')
    blood_group = fields.Selection([('O+', 'O+'), ('A+', 'A+'), ('B+', 'B+'), ('AB+', 'AB+'), ('O-', 'O-'), ('A-', 'A-'), ('B-', 'B-'), ('AB-', 'AB-'), ('A1+', 'A1+'), ('A1-', 'A1-'), ('A1B+', 'A1B+'), ('A1B+', 'A1B+'), ('A2+', 'A2+'), ('A2-', 'A2-'), ('A2B+', 'A2B+'), ('A2B-', 'A2B-'), ('B1+', 'B1+'), ('B1-', 'B1-')], 'Blood Group')



class employee_address_details(models.Model):
    _name = "emp.address"
    _description = "Employee Address Details"
    
    address1 = fields.Char('Address1', size=120)
    address2 = fields.Char('Address2', size=120)          		
    city = fields.Char('City', size=24)
    country_id = fields.Many2one('res.country', "Country") 
    state_id = fields.Many2one('res.country.state', "State")       
    pin_code = fields.Integer('Pin Code', size=10)
    employee_id = fields.Many2one('hr.employee','Employee ID')    


class employee_personal_details(models.Model):
    _name = "emp.personal.details"
    _description = "Employee Personal Details"


    extension_number = fields.Char('Extension No', size=64)
    home_number = fields.Char('Home No', size=64)
    mobile_number = fields.Char('Mobile No', size=64)
    emergency_number = fields.Char('Emergency No', size=64)
    email = fields.Char('Email ID', size=64)
    official_email = fields.Char('Official Email ID', size=64)
    religion = fields.Char('Religion', size=24)
    height = fields.Char('Height in cms', size=24)
    weight = fields.Char('Weight in kgs', size=24)
    identification_mark = fields.Char('Identification Mark', size=64)
    vision = fields.Char('Vision', size=64)
    passport_number = fields.Char('Passport No', size=64)
    passPort_validity = fields.Date('PassPort Validity')
    driving_license_number = fields.Char('Driving License No', size=64)
    hobbies = fields.Char('Hobbies', size=64)
    achievement = fields.Char('Achievement', size=64)
    notice_period = fields.Char('Notice Period', size=24)
    medical_history = fields.Char('Medical History', size=64)
    political = fields.Selection([('no','NO'), ('yes','Yes')], 'Political / Social Body')
    details = fields.Char('Details', size=64)
    pancard_number = fields.Char('Pancard No', size=64)
    aadhar_number = fields.Char('Aadhar No', size=64)
    employee_id = fields.Many2one('hr.employee','Employee ID')   


class AcademicRecord(models.Model):
    _name = 'hr.academic.record'
    _description = 'Employee Academic Records'
     


    degree = fields.Char('Major/Degree', size=64)
    qualification =  fields.Selection([('sslc', 'SSLC'), ('hsc', 'HSC'), ('diploma', 'DIPLOMA'), ('ug', 'UG'), ('pg', 'PG'), ('iti', 'ITI'), ('others', 'OTHERS')], 'Qualification')
    year_of_passing = fields.Date('Year of Passing')
    pass_class = fields.Selection([('first_class','FIRST CLASS'), ('second_class','SECOND CLASS'), ('distinction','DISTINCTION')], 'Class')
    board_or_university = fields.Char('Board / University', size=64)
    name_of_institution = fields.Char('Institution', size=64)
    employee_id = fields.Many2one('hr.employee','Employee ID')


class Experience(models.Model):
    _name = 'hr.experience'
    _description = 'Experience'
   
    @api.multi
    @api.depends('experience')
    def _get_experience(self):
        context = self._context or {}
        for employee in self:
            if employee.date_of_joined:
                if not employee.exit_date:
                    till_day = datetime.today()
                else:
                    till_day = datetime.strptime(employee.exit_date, "%Y-%m-%d")
                join_date = employee.date_of_joined.split('-')
                year = int(join_date[0])
                month = int(join_date[1])
                date = int(join_date[2])
                experience = dateutil.relativedelta.relativedelta(till_day, datetime(year, month, date))
                self.experience = experience.years
            else:
                self.experience = False
                
    @api.multi
    @api.depends('experience_months')
    def _get_experience_months(self):
        context = self._context or {}
        for employee in self:
            if employee.date_of_joined:
                if not employee.exit_date:
                    till_day = datetime.today()
                else:
                    till_day = datetime.strptime(employee.exit_date, "%Y-%m-%d")
                join_date = employee.date_of_joined.split('-')
                year = int(join_date[0])
                month = int(join_date[1])
                date = int(join_date[2])
                experience = dateutil.relativedelta.relativedelta(till_day, datetime(year, month, date))
                self.experience_months = experience.months
            else:
                self.experience_months = False
                
    @api.multi
    @api.depends('experience_days')
    def _get_experience_days(self):
        context = self._context or {}
        for employee in self:
            if employee.date_of_joined:
                if not employee.exit_date:
                    till_day = datetime.today()
                else:
                    till_day = datetime.strptime(employee.exit_date, "%Y-%m-%d")
                join_date = employee.date_of_joined.split('-')
                year = int(join_date[0])
                month = int(join_date[1])
                date = int(join_date[2])
                experience = dateutil.relativedelta.relativedelta(till_day, datetime(year, month, date))
                self.experience_days = experience.days
            else:
                self.experience_days = False
                
     

    Skil_type = fields.Char('Skill Type', size=64)
    salary = fields.Integer('Salary', size=10)
    previous_employer  = fields.Char('Previous Employer', size=40)
    reason_for_leaving  = fields.Char('Reason For Leaving', size=40)
    previous_designation   = fields.Char('Previous Designation', size=40)
    employee_id = fields.Many2one('hr.employee','Employee ID')
    date_of_joined = fields.Date('Date of Joined')
    exit_date = fields.Date('Date of Exit')
    experience = fields.Integer(compute='_get_experience', string='Work Experience')
    experience_months = fields.Integer(compute='_get_experience_months', string='Work Experience months')
    experience_days = fields.Integer(compute='_get_experience_days', string='Work Experience Days')


 

class Insurance(models.Model):
    _name = 'hr.insurance'
    _description = 'Insurance'
     
    lic_number = fields.Char('LIC Number', size=64)
    policy_peroid_from = fields.Date('Policy Peroid From')
    policy_peroid_to = fields.Date('Policy Peroid To')
    mediclaim = fields.Boolean('Mediclaims')
    mediclaims = fields.Integer('Mediclaim', size=10)
    gpa_coverage  = fields.Boolean('GPA Coverage')
    gpa_coverages = fields.Integer('GPA Coverages', size=10)
    employee_id = fields.Many2one('hr.employee','Employee ID')

 
class Family(models.Model):
    _name = 'hr.family'
    _description = 'Family'
     
    name = fields.Char('Name', size=24)
    age = fields.Integer('Age', size=3)
    location = fields.Char('Location')
    permanent_address_country_id = fields.Many2one('res.country', "Country") 
    permanent_address_state_id = fields.Many2one('res.country.state', "State")        
    relationship =  fields.Selection([('mother', 'MOTHER'), ('father', 'FATHER'), ('sister', 'SISTER'), ('brother', 'BROTHER'), ('other', 'OTHERS'), ('husband', 'HUSBAND'), ('wife', 'WIFE'), ('son', 'SON'), ('daughter', 'DAUGHTER')], 'Relationship')
    occupation = fields.Char('Occupation', size=24)
    city = fields.Char('City', size=24)
    pin_code = fields.Integer("Pin Code", size=24)
    date_of_birth = fields.Date('Date Of Birth')
    mobile_number = fields.Integer('Mobile', size=64)
    residing = fields.Boolean('Residing')
    mediclaim2 = fields.Boolean('Mediclaim')
    esi_nominee = fields.Boolean('ESi Nominee')
    relatives_with_us_or_our_subsidary  = fields.Boolean('Relatives with US or Our Subsidary')
    gpa_nominee = fields.Boolean('GPA Nominee')
    grautity_nominee  = fields.Boolean('Grautity Nominee')
    nominee = fields.Boolean('Nominee')
    pf_nominee = fields.Boolean('PF Nominee')
    employee_id = fields.Many2one('hr.employee','Employee ID')
 


class Section(models.Model):

    _name = "hr.section"
    _description = "Section"

    section_code = fields.Char(string="Section Code", required=True)
    name = fields.Char(string="Section Description", required=True)
    employee_id = fields.Many2one('hr.employee','Employee ID')


class HrSalaryCode(models.Model):

    _name = "hr.salary.code"
    _description = "Salary Code"

    name = fields.Char(string="Salary Code", required=True)


class CostCenter(models.Model):

    _name = "cost.center"
    _description = "Cost Center"

    name = fields.Char(string="Cost Centre Code", required=True)
    cost_center_description = fields.Char(string="Cost Centre Description", required=True)


    @api.multi
    @api.depends('name', 'cost_center_description')
    def name_get(self):
        result = []
        for account in self:
            name = account.cost_center_description + '/' + account.name
            result.append((account.id, name))
        return result

class Candidatecode(models.Model):

    _name = "candidate.code"
    _description = "Candidate Code"

    candidate_code = fields.Char(string="Candidate Code", required=True)
    name = fields.Char(string="Candidate Name")
    candidate_status = fields.Char(string="Candidate Status")

    @api.multi
    @api.depends('name', 'candidate_code')
    def name_get(self):
        result = []
        for account in self:
            name = account.candidate_code + '/' + account.name
            result.append((account.id, name))
        return result


class Job(models.Model):

    _name = "hr.job"
    _description = "Job Position"
    _inherit = "hr.job"


    designation_code = fields.Char(string="Designation Code", required=True)

class Empsalary(models.Model):

    _name = "emp.salary"
    _description = "Emp Salary"


    department_id = fields.Many2one('hr.department', string='Department')
    section_id = fields.Many2one('hr.section', string='Section')
    job_id = fields.Many2one('hr.job', string='Designation')
    salary_code_id = fields.Many2one('hr.salary.code', string='Salary Code')
    cost_center_id = fields.Many2one('cost.center', string=' Cost Centre')
    basic_salary = fields.Integer('Basic Salary', size=64)
    dearness_allowance = fields.Integer('Dearness Allowance', size=64)
    pf_number = fields.Char('PF Number', size=64)
    esi_number = fields.Char('ESI Number', size=64)
    effective_from = fields.Date('Effective From')
    effective_to = fields.Date('Effective To')
    employee_id = fields.Many2one('hr.employee','Employee ID')


class Task(models.Model):
	_inherit = "project.task"
	
	@api.model
	def _needaction_domain_get(self):
		
		stage = self.env['project.task.type'].search([('name','=','In Progress')])
		
		return [('stage_id', '=', stage.id)]
		
class HrAttendance(models.Model):
	_inherit = "hr.attendance"
	
	@api.onchange('check_in')
	def onchange_check_in(self):
		if self.check_in:
			print self
			for attendance in self:
				last_attendance_before_check_in = self.env['hr.attendance'].search([
					('employee_id', '=', attendance.employee_id.id),
					('check_in', '=', attendance.check_in),
					('id', '!=', attendance.id),
				], order='check_in desc', limit=1)
			print last_attendance_before_check_in
        

	
