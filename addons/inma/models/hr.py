import logging

from lxml import etree
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.safe_eval import safe_eval
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

import dateutil.relativedelta
import dateutil.parser
import calendar


from datetime import datetime, date, time, timedelta
import time
import dateutil
import base64
import sys
import re

from dateutil.relativedelta import relativedelta


def date_indian(date):
    date_split = date.split('-')
    date_indian = date_split[2]+'/'+date_split[1]+'/'+date_split[0] 
    return date_indian

_logger = logging.getLogger(__name__)


class Employee(models.Model):
	_name = 'hr.employee'
	_inherit = ['hr.employee', 'ir.needaction_mixin']

	@api.multi
	@api.depends('experience')
	def _get_experience(self):
		for employee in self:
			if employee.date_of_appointment:
				till_day = datetime.today()
				join_date = employee.date_of_appointment.split('-')
				year = int(join_date[0])
				month = int(join_date[1])
				date = int(join_date[2])
				experience = dateutil.relativedelta.relativedelta(till_day, datetime(year, month, date))
				experience_year=experience.years
				experience_month=experience.months
				experience_day=experience.days
				employee.experience = str(experience_year)+' year(s)\t'+str(experience_month)+' month(s)\t'+str(experience_day)+' day(s)'
	
	cid = fields.Char('C ID', size=10)
	parent_name = fields.Char('Parent/Spouse Name')
	birth_place = fields.Char('Birth Place')
	date_of_interview = fields.Date('Date of Interview')
	date_of_appointment = fields.Date('Date of Appointment')
	experience = fields.Char(compute='_get_experience', string='INMA Experience')
	qualification_id = fields.Many2one('hr.recruitment.degree', 'Qualification')
	job_applied_id = fields.Many2one('hr.job', 'Designation Applied for')
	job_appointed_id = fields.Many2one('hr.job', 'Designation Appointed')
	height = fields.Char('Height')
	weight = fields.Char('Weight')
	blood_group_id = fields.Many2one('employee.bloodgroup', 'Blood Group')
	waist_size = fields.Integer('Waist Size')
	shoe_size = fields.Integer('Shoe Size')
	medical_history = fields.Text('Medical History')
	adhaar_no = fields.Char('Adhaar No', size=12)
	present_address1 = fields.Char("Address Line", size=128)
	present_address2 = fields.Char("Address Line2", size=128)
	present_zip = fields.Char("PIN", size=6)
	present_city = fields.Char("City", size=24)
	present_state_id = fields.Many2one('res.country.state', "State")
	present_address_country_id = fields.Many2one('res.country', "Country")
	permanent_address1 = fields.Char("Address Line", size=128)
	permanent_address2 = fields.Char("Address Line2", size=128)
	permanent_zip = fields.Char("PIN", size=6)
	permanent_city = fields.Char("City", size=24)
	permanent_state_id = fields.Many2one('res.country.state', "State")
	permanent_address_country_id = fields.Many2one('res.country', "Country")
	original_certificate = fields.Selection([('yes', 'YES'), ('no','NO')], 'Original Certificate/ ID Submitted')
	pf_details = fields.Char('PF/ESI Details')
	insurance_details = fields.Char('Insurance Details')
	undertaking = fields.Text('Undertaking')
	hr_past_work_experience_id = fields.One2many('hr.past.work.experience', 'employee_id', 'Past Work Experience')
	nominee_ids = fields.One2many('hr.nominee', 'employee_id', 'Relations')
	project_id = fields.Many2one('project.name', 'Project Name')
	expected_salary = fields.Char('Expected Salary')
	emergency_person_ids = fields.One2many('emergency.contact.person', 'employee_id', 'Emergency Contact Person')
	adhaar_attach = fields.Binary("Adhaar copy")
	passport_attach = fields.Binary("Passport Copy")
	residential_status = fields.Selection([('residential', 'Residential'), ('non_residential', 'Non-Residential')], 'Residential Status')
	food_provided = fields.Boolean("Whether food to be provided by the company")
	original_document = fields.Boolean("Original Documents Submitted,if any")
	original_document_attach = fields.Binary('Original Document Attachment')
	copies_submitted_ids = fields.One2many('copies.submitted', 'employee_id', 'Copies Submitted')
	accomodation_allot = fields.Char(' Details of Accomodation Alloted')
	id_card = fields.Char('ID card & Validity')
	item_issued_ids = fields.Many2many('other.item.issued','employee_other_item_issued_detail','employee_id','other_item_issue_id', 'Detail of other item issued')
	expired_status = fields.Char('Expired Status')
	same_as_address = fields.Boolean('Same as Present Address')
	work_base = fields.Selection([('day_basis','Day Basis'),('hour_basis','Hour Basis')],'Work Base')
	category_id = fields.Many2one('hr.employee.category', 'Employee Category')
	identity_no = fields.Char('Identification No', size=10)
	
	_sql_constraints = [
        ('cid_uniq', 'unique(cid)', 'C ID should be unique'),
        ]
	
	@api.model
	def find_expired_id(self):
		for employee in self.env['hr.employee'].search([]):
			if employee.date_of_appointment:
				till_day = datetime.today()
				join_date = employee.date_of_appointment.split('-')
				year = int(join_date[0])
				month = int(join_date[1])
				date = int(join_date[2])
				experience = dateutil.relativedelta.relativedelta(till_day, datetime(year, month, date))
				if experience.days == 7:
					employee.expired_status = 'expired'
					
	@api.model
	def _needaction_domain_get(self):
		return [('expired_status', '=', 'expired')]
	
	@api.onchange('id_card')
	def onchange_id(self):
		if self.id_card:
			self.expired_status = 'valid'
	
	@api.onchange('same_as_address')
	def onchange_same_as_address(self):
		if self.same_as_address:
			if self.present_address1 and self.present_zip and self.present_city and self.present_state_id and self.present_address_country_id:
				self.permanent_address1 = self.present_address1
				self.permanent_address2 = self.present_address2
				self.permanent_zip = self.present_zip
				self.permanent_city = self.present_city
				self.permanent_state_id = self.present_state_id.id
				self.permanent_address_country_id = self.present_address_country_id.id
			else:
				raise ValidationError(_("First Fill all Mandatory Present Address"))
				
	@api.one
	@api.constrains('cid')
	def _check_cid_constraints(self):
		if self.cid:
			name = self.cid.strip()
			self.env.cr.execute('''select count(id) as count from hr_employee where LOWER(cid) = LOWER(%s)''',((name),))
			for name_id in self.env.cr.dictfetchall():	
				name_count = name_id['count']
				if name_count > 1:
					raise ValidationError(_("CID must be unique"))		
			#match =  re.match('^([A-Za-z-]+[0-9]+)+$',str(self.cid))
			#if match == None:
				#raise ValidationError(_("CID doesn't allow symbols"))
	
	#@api.one
	#@api.constrains('name_related')
	#def _check_name_constraints(self):
		#if self.name_related:
			#name = self.name_related.strip()
			#self.env.cr.execute('''select count(id) as count from hr_employee where LOWER(name_related) = LOWER(%s)''',((name),))
			#for name_id in self.env.cr.dictfetchall():	
				#name_count = name_id['count']
				#if name_count > 1:
					#raise ValidationError(_("Name must be unique"))
	
	@api.one
	@api.constrains('mobile_phone')
	def _check_mobile_constraints(self):
		if self.mobile_phone:
			valid_format = re.compile("[7-9]\d{9}")
			if len(str(self.mobile_phone)) == 10 and valid_format.match(str(self.mobile_phone)):
				return True
			else:
				raise ValidationError(_("Enter 10 digit Work mobile number"))
	
	@api.one
	@api.constrains('work_email')
	def _check_email_constraints(self):
		if self.work_email:
			match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', str(self.work_email))
			if match == None:
				raise ValidationError(_("Enter correct email ID"))
				
	@api.one
	@api.constrains('adhaar_no')
	def _check_aadhar_constraints(self):
		if self.adhaar_no:
			valid_format = re.compile('^\d{12}$')
			if valid_format.match(str(self.adhaar_no)):
				return True
			else:
				raise ValidationError(_("Enter correct adhaar No"))
				
	@api.one
	@api.constrains('present_zip','permanent_zip')
	def _check_pincode_constraints(self):
		if self.present_zip and self.permanent_zip:
			valid_format = re.compile('^\d{6}$')
			if valid_format.match(str(self.present_zip)) and valid_format.match(str(self.permanent_zip)):
				return True
			else:
				raise ValidationError(_("Enter correct Pincode"))
				
	@api.constrains('date_of_appointment','date_of_interview')
	@api.onchange('date_of_appointment','date_of_interview')
	def onchange_date(self):
		today_date = datetime.today().strftime('%Y-%m-%d')
		if self.date_of_appointment:
			if self.date_of_appointment > today_date:
				raise ValidationError(_("Future Date should not allowed in Date of appointment"))
		if self.date_of_interview:
			if self.date_of_interview > today_date:
				raise ValidationError(_("Future Date should not allowed in Date of Interview"))
	
	@api.one
	@api.constrains('passport_id')
	def _check_passport_id(self):
		if self.passport_id:
			if len(str(self.passport_id)) <=10:
				return True
			else:
				raise ValidationError(_("Passport size should be below 10"))
				
class EmployeeBloodgroup(models.Model):
	_description="Blood Group"
	_name = 'employee.bloodgroup'
	
	name = fields.Char('Blood Group Name', size=12, required=True)
	
	_sql_constraints = [('name_uniq', 'unique (name)', 'The name of the blood group must be unique !')]
	
	_order = 'name'
	
	@api.model
	def create(self,vals):
		name = (vals.get('name')).strip().upper()
		vals['name'] = name
		return super(EmployeeBloodgroup, self).create(vals)
		
	@api.one
	@api.constrains('name')
	def _check_name_constraints(self):
		if self.name:
			name = self.name.strip()
			self.env.cr.execute('''select count(id) as count from employee_bloodgroup where LOWER(name) = LOWER(%s)''',((name),))
			for name_id in self.env.cr.dictfetchall():
				name_count = name_id['count']
				if name_count > 1:
					raise ValidationError(_("Blood Group must be unique"))
					
	@api.multi
	def write(self, vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(EmployeeBloodgroup, self).write(vals)
		
class HrRelation(models.Model):
	_description="Relation Master"
	_name = 'hr.employee.relation'
	
	name = fields.Char('Relation Name', size=12, required=True)
	
	_sql_constraints = [('name_uniq', 'unique (name)','The name of the relation must be unique !')]
	
	_order = 'name'
	
	@api.model
	def create(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(HrRelation, self).create(vals)
		
	@api.one
	@api.constrains('name')
	def _check_name_constraints(self):
		if self.name:
			name = self.name.strip()
			self.env.cr.execute('''select count(id) as count from hr_employee_relation where LOWER(name) = LOWER(%s)''',((name),))
			for name_id in self.env.cr.dictfetchall():
				name_count = name_id['count']
				if name_count > 1:
					raise ValidationError(_("Given relation name already exist"))
	
	@api.multi
	def write(self, vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(HrRelation, self).write(vals)
		
class HrNominee(models.Model):    
    _name = "hr.nominee" 
    
    name =  fields.Char('Name', size=64)
    relation = fields.Many2one('hr.employee.relation', 'Relation')
    address = fields.Char('Address Line')
    address1 = fields.Char('Address Line2')
    city = fields.Char('City')
    pincode = fields.Char('Pincode', size=6)
    mobile_phone =  fields.Char('Mobile number', size=10)
    employee_id =  fields.Many2one('hr.employee', 'Employee', ondelete='cascade')
    
    @api.one
    @api.constrains('mobile_phone')
    def _check_mobile_constraints(self):
		if self.mobile_phone:
			valid_format = re.compile("[7-9]\d{9}")
			if len(str(self.mobile_phone)) == 10 and valid_format.match(str(self.mobile_phone)):
				return True
			else:
				raise ValidationError(_("Enter correct Mobile number in Nominee"))
    @api.one
    @api.constrains('pincode')
    def _check_pincode_constraints(self):
		if self.pincode:
			valid_format = re.compile('^\d{6}$')
			if valid_format.match(str(self.pincode)):
				return True
			else:
				raise ValidationError(_("Enter correct Pincode in Nominee"))
		
class HRPastExperience(models.Model):
    _name = 'hr.past.work.experience'
    
    @api.multi
    @api.depends('experience')
    def _get_experience(self):
		
		for employee in self:
			if employee.period_from:
				if not employee.period_to:
					till_day = datetime.today()
				else:
					till_day = datetime.strptime(employee.period_to, "%Y-%m-%d")
					join_date = employee.period_from.split('-')
					year = int(join_date[0])
					month = int(join_date[1])
					date = int(join_date[2])
					experience = dateutil.relativedelta.relativedelta(till_day, datetime(year, month, date))
					experience_year=experience.years
					experience_month=experience.months
					experience_day=experience.days
					employee.experience = str(experience_year)+' year(s)\t'+str(experience_month)+' month(s)\t'+str(experience_day)+' day(s)'
					     
    employee_id = fields.Many2one('hr.employee','Employee ID', ondelete='cascade')
    job_id = fields.Many2one('hr.job', 'Post held')
    employer = fields.Char('Employer', size=128)
    address = fields.Char('Address', size=256)
    period_from = fields.Date('Period From')
    period_to = fields.Date('Period To')
    experience = fields.Char(compute='_get_experience', string='Work Experience')
    last_drawn_salary = fields.Char("Last Drawn Salary")
    
    @api.constrains('period_from','period_to')
    @api.onchange('period_from','period_to')
    def onchange_date(self):
		if self.period_from and self.period_to:
			if self.period_from > self.period_to:
				raise ValidationError(_("Period From should less than Period To"))
    
class ResCity(models.Model):
	_name = "res.city"
	
	name = fields.Char('City')
	state_id = fields.Many2one('res.country.state','State')
	
	@api.model
	def create(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(ResCity, self).create(vals)
	
	@api.one
	@api.constrains('name')
	def _check_name_constraints(self):
		if self.name:
			name = self.name.strip()
			self.env.cr.execute('''select count(id) as count from res_city where LOWER(name) = LOWER(%s)''',((name),))
			for name_id in self.env.cr.dictfetchall():
				name_count = name_id['count']
				if name_count > 1:
					raise ValidationError(_("City already exist"))
	
	@api.multi
	def write(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(ResCity, self).write(vals)
	
class Partner(models.Model):
	_inherit = "res.partner"
    
	city_id = fields.Many2one('res.city','City')
	business_structure_id = fields.Many2one('business.structure','Business Structure')
	nature_business_ids = fields.Many2many('nature.business.structure', 'vendor_nature_business_rel', 'partner_id', 'nature_business_id', 'Nature of Business')
	owner_name = fields.Char('Name of Owner/Director')
	type_of_material_ids = fields.Many2many('type.of.material', 'product_data_type_of_material_rel', 'partner_id','product_data_id', 'Type of Material')
	product_detail_description = fields.Text("Detail Description of Product")
	product_standard = fields.Char("Product Specification")
	stock_status = fields.Selection([('immediate', 'Immediate'), ('not_immediate', 'Not Immediate')], 'Stock Status')
	state_period_of_order = fields.Char("Please State Period of Order")
	location_stock = fields.Char('Location of Stock')
	iso_certificate = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'ISO Certificate')
	company_registration_no = fields.Char('Company Registration No')
	pan_no = fields.Char('PAN No', size=10)
	service_tax_code = fields.Char('Service Tax Access Code')
	declaration = fields.Binary('Declaration')
	contact_person = fields.Char('Contact Person')
	transport = fields.Selection([('free','Free'),('cost','Cost')], 'Transport')
	
	@api.onchange('city_id')
	def onchange_city_id(self):
		if self.city_id:
			self.city = self.city_id.name
			self.state_id = self.city_id.state_id.id
			self.country_id = self.city_id.state_id.country_id.id
	
	@api.one
	@api.constrains('mobile')
	def _check_mobile_constraints(self):
		if self.mobile:
			valid_format = re.compile("[7-9]\d{9}")
			if len(str(self.mobile)) == 10 and valid_format.match(str(self.mobile)):
				return True
			else:
				raise ValidationError(_("Enter 10 digit Work mobile number"))
	
	#@api.one
	#@api.constrains('email')
	#def _check_email_constraints(self):
		#if self.email:
			#match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', str(self.email))
			#if match == None:
				#raise ValidationError(_("Enter correct email ID"))
	
	@api.one
	@api.constrains('pan_no')
	def _check_pan_constraints(self):
		if self.pan_no:
			if re.match('^[A-Za-z]{5}\d{4}[A-Za-z]{1}$',str(self.pan_no)) == None:
				raise ValidationError(_("Enter valid PAN number eg.AAAAA12345A"))
	
	@api.one
	@api.constrains('website')
	def _check_website_constraints(self):
		if self.website:
			if re.match('^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$', str(self.website)) == None:
				print "error"
	
	@api.one
	@api.constrains('fax')
	def _check_fax_constraints(self):
		if self.fax:
			if re.match('^(\+?\d{1,}(\s?|\-?)\d*(\s?|\-?)\(?\d{2,4}\)?(\s?|\-?)\d{6,8})$',str(self.fax)) == None:
				raise ValidationError(_("Enter valid fax eg+91 234 230344"))
				
	@api.one
	@api.constrains('zip')
	def _check_pincode_constraints(self):
		if self.zip:
			valid_format = re.compile('^\d{6}$')
			if valid_format.match(str(self.zip)):
				return True
			else:
				raise ValidationError(_("Enter correct Pincode"))
	
	@api.one
	@api.constrains('vat')
	def _check_vat_constraints(self):
		if self.vat:
			if re.match('^\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d[Z]{1}[A-Z\d]{1}$',str(self.vat)) == None:
				raise ValidationError(_("Enter valid GSTNo"))

class business_structure(models.Model):
	_name = "business.structure"
	
	name = fields.Char('Name')
	
	@api.model
	def create(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(business_structure, self).create(vals)
	
	@api.one
	@api.constrains('name')
	def _check_name_constraints(self):
		if self.name:
			name = self.name.strip()
			self.env.cr.execute('''select count(id) as count from business_structure where LOWER(name) = LOWER(%s)''',((name),))
			for name_id in self.env.cr.dictfetchall():
				name_count = name_id['count']
				if name_count > 1:
					raise ValidationError(_("Business Structure already exist"))
	
	@api.multi
	def write(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(business_structure, self).write(vals)

class nature_business_structure(models.Model):
	_name = "nature.business.structure"
	
	name = fields.Char('Name')
	
	@api.model
	def create(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(nature_business_structure, self).create(vals)
	
	@api.one
	@api.constrains('name')
	def _check_name_constraints(self):
		if self.name:
			name = self.name.strip()
			self.env.cr.execute('''select count(id) as count from nature_business_structure where LOWER(name) = LOWER(%s)''',((name),))
			for name_id in self.env.cr.dictfetchall():
				name_count = name_id['count']
				if name_count > 1:
					raise ValidationError(_("Nature of Business Structure already exist"))
	
	@api.multi
	def write(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(nature_business_structure, self).write(vals)


class type_of_material(models.Model):
	_name = "type.of.material"
	
	name = fields.Char('Name')
	
	@api.model
	def create(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(type_of_material, self).create(vals)
	
	@api.one
	@api.constrains('name')
	def _check_name_constraints(self):
		if self.name:
			name = self.name.strip()
			self.env.cr.execute('''select count(id) as count from type_of_material where LOWER(name) = LOWER(%s)''',((name),))
			for name_id in self.env.cr.dictfetchall():
				name_count = name_id['count']
				if name_count > 1:
					raise ValidationError(_("Type of Material already exist"))
	
	@api.multi
	def write(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(type_of_material, self).write(vals)	
	
class emergency_contact_person(models.Model):    
    _name = "emergency.contact.person" 
    
    name =  fields.Char('Name', size=64)
    relation = fields.Many2one('hr.employee.relation', 'Relation')
    address = fields.Char('Address Line')
    address1 = fields.Char('Address Line2')
    city = fields.Char('City')
    pincode = fields.Char('Pincode', size=6)
    mobile_phone =  fields.Char('Mobile number', size=10)
    employee_id =  fields.Many2one('hr.employee', 'Employee', ondelete='cascade')
    
    @api.one
    @api.constrains('mobile_phone')
    def _check_mobile_constraints(self):
		if self.mobile_phone:
			valid_format = re.compile("[7-9]\d{9}")
			if len(str(self.mobile_phone)) == 10 and valid_format.match(str(self.mobile_phone)):
				return True
			else:
				raise ValidationError(_("Enter correct Mobile number in Emergency Contact Person"))
				
    @api.one
    @api.constrains('pincode')
    def _check_pincode_constraints(self):
		if self.pincode:
			valid_format = re.compile('^\d{6}$')
			if valid_format.match(str(self.pincode)):
				return True
			else:
				raise ValidationError(_("Enter correct Pincode in Emergency Contact Person"))
				
				
class copies_submitted(models.Model):
	_name = "copies.submitted"
	
	card_name_id = fields.Many2one('card.name','Copy Name')
	attachment = fields.Binary('Attachment')
	employee_id =  fields.Many2one('hr.employee', 'Employee', ondelete='cascade')
	
class card_name(models.Model):
	_name = "card.name"
	
	name = fields.Char("Proof Id name", size=20)
	
	@api.model 
	def create(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(card_name, self).create(vals)
	
	@api.one
	@api.constrains('name')
	def _check_name_constraints(self):
		if self.name:
			name = self.name.strip()
			self.env.cr.execute('''select count(id) as count from card_name where LOWER(name) = LOWER(%s)''',((name),))
			for name_id in self.env.cr.dictfetchall():
				name_count = name_id['count']
				if name_count > 1:
					raise ValidationError(_("Name already exist"))
					
	@api.multi
	def write(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(card_name, self).write(vals)
	
class other_items_issued(models.Model):
	_name = "other.item.issued"
	
	name = fields.Char('Item name', size=20)
	
	@api.model
	def create(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(other_items_issued, self).create(vals)
	
	@api.one
	@api.constrains('name')
	def _check_name_constraints(self):
		if self.name:
			name = self.name.strip()
			self.env.cr.execute('''select count(id) as count from other_item_issued where LOWER(name) = LOWER(%s)''',((name),))
			for name_id in self.env.cr.dictfetchall():
				name_count = name_id['count']
				if name_count > 1:
					raise ValidationError(_("Name already exist"))
					
	@api.multi
	def write(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(other_items_issued, self).write(vals)
	
class ProductTemplate(models.Model):
	_name = "product.template"
	_inherit = "product.template"
	
	inma_code_no = fields.Char('INMA Code No')
	is_complaince = fields.Boolean('Any Compliance')
	complaince_detail = fields.Char('Details of Compliance')
	approved_manufacturer_ids = fields.Many2many('approved.manufacturer','approved_manufacturer_rel','product_id','approved_manufacturer_id','Approved Manufacturer')
	est_qty_ring = fields.Char('Est Qty/Ring')
	rol_in_unit = fields.Char('ROL in Unit')
	rol_in_days = fields.Char('ROL in Days')
	lead_time = fields.Char('Lead Time')
	category_ids = fields.Many2many('product.category.tag', 'product_category_tag_rel', 'product_id', 'category_id', string='Tags')
	product_type = fields.Selection([('all','All'),('segment','Segment')], 'Product Tag')
	vendor_list_id = fields.One2many('vendor.list','product_id','Vendor')
	project_id = fields.Many2one('project.name', 'Project Name')
	
	@api.one
	@api.constrains('inma_code_no')
	def _check_cid_constraints(self):
		if self.inma_code_no:
			name = self.inma_code_no.strip()
			self.env.cr.execute('''select count(id) as count from product_template where LOWER(inma_code_no) = LOWER(%s)''',((name),))
			for name_id in self.env.cr.dictfetchall():	
				name_count = name_id['count']
				if name_count > 1:
					raise ValidationError(_("INMA Code No must be unique"))
					
	@api.one
	@api.constrains('name')
	def _check_name_constraints(self):
		if self.name:
			name = self.name.strip()
			self.env.cr.execute('''select count(id) as count from product_template where LOWER(name) = LOWER(%s)''',((name),))
			for name_id in self.env.cr.dictfetchall():
				name_count = name_id['count']
				if name_count > 1:
					raise ValidationError(_("Product already exist"))
	
	
	@api.one
	@api.constrains('seller_ids')
	def _check_quantity_price_constraints(self):
	
		if self.seller_ids:
			print self.seller_ids
			for seller in self.seller_ids:
				#if seller.min_qty <= 0:
					#raise ValidationError(_("In Vendors Tab Minimum Quantity should not be Zero"))
				#if seller.price <= 0:
					#raise ValidationError(_("In Vendors Tab Price should not be Zero"))
				if seller.date_start > seller.date_end:
					raise ValidationError(_("In Vendors TAB From date should not be greaterthan To date"))
		
class approved_manufacturer(models.Model):
	_name  = 'approved.manufacturer'
	
	name = fields.Char('Name')
	model = fields.Char('Model')
	
	@api.model
	def create(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(approved_manufacturer, self).create(vals)
	
	@api.one
	@api.constrains('name')
	def _check_name_constraints(self):
		if self.name:
			name = self.name.strip()
			self.env.cr.execute('''select count(id) as count from approved_manufacturer where LOWER(name) = LOWER(%s)''',((name),))
			for name_id in self.env.cr.dictfetchall():
				name_count = name_id['count']
				if name_count > 1:
					raise ValidationError(_("Approved Manufactured already exist"))
	
	@api.multi
	def write(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(approved_manufacturer, self).write(vals)

class product_category_tag(models.Model):
    _name = "product.category.tag"

    name = fields.Char("Tag")
    
    @api.model
    def create(self,vals):
	name = (vals.get('name')).strip()
	vals['name'] = name
	return super(product_category_tag, self).create(vals)
	
    @api.one
    @api.constrains('name')
    def _check_name_constraints(self):
	if self.name:
		name = self.name.strip()
		self.env.cr.execute('''select count(id) as count from product_category_tag where LOWER(name) = LOWER(%s)''',((name),))
		for name_id in self.env.cr.dictfetchall():
			name_count = name_id['count']
			if name_count > 1:
				raise ValidationError(_("Product Category already exist"))
	
    @api.multi
    def write(self,vals):
	name = (vals.get('name')).strip()
	vals['name'] = name
	return super(product_category_tag, self).write(vals)
    
class SaleOrder(models.Model):
	_inherit = 'sale.order'
	
	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			if vals.get('order_line'):
				if 'company_id' in vals:
					vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('sale.order')
				else:
					vals['name'] = self.env['ir.sequence'].next_by_code('sale.order')
			else:
				raise ValidationError(_("Choose Product for Quotation"))
		
		 # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
		if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
			partner = self.env['res.partner'].browse(vals.get('partner_id'))
			addr = partner.address_get(['delivery', 'invoice'])
			vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
			vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
			vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)
		result = super(SaleOrder, self).create(vals)
		return result
	
class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'
	
	rfq_no = fields.Char('RFQ No')
	srm_id = fields.Many2one('stock.requirement.memo','SRM No')
	
	@api.model
	def create(self,vals):
		if vals.get('name', 'New') == 'New':
			#if vals.get('order_line'):
			number = self.env['ir.sequence'].search([('code','=','purchase.order')])
			vals['rfq_no'] = 'RFQ'+'%%0%sd' % number.padding % number.number_next_actual
			vals['name'] = self.env['ir.sequence'].next_by_code('purchase.order') or '/'
			#else:
				#raise ValidationError(_("Choose Product for Quotation"))
		return super(PurchaseOrder, self).create(vals)
				
	@api.multi
	def print_quotation(self):
		self.write({'state': "sent"})
		return self.env['report'].get_action(self, 'inma.report_purchasequotation')
		
	@api.multi
	def print_purchase_order(self):
		return self.env['report'].get_action(self, 'inma.report_purchaseorder_document')
			
class ResPartnerBank(models.Model):
	_inherit = 'res.partner.bank'
	
	category_ids = fields.Many2one('hr.employee.category', 'Employee Category')
	
	@api.one
	@api.constrains('acc_number')
	def _check_account_number(self):
		if self.acc_number:
			if (re.match('^[0-9]+$', str(self.acc_number))) and len(str(self.acc_number)) <=20:
				return True
			else:
				raise ValidationError(_("Account Number is only in numeric format and length should be below 20"))
		
class EmployeeCategory(models.Model):
	_inherit = "hr.employee.category"
	
	@api.model
	def create(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(EmployeeCategory, self).create(vals)
	
	@api.one
	@api.constrains('name')
	def _check_name_constraints(self):
		if self.name:
			name = self.name.strip()
			self.env.cr.execute('''select count(id) as count from hr_employee_category where LOWER(name) = LOWER(%s)''',((name),))
			for name_id in self.env.cr.dictfetchall():
				name_count = name_id['count']
				if name_count > 1:
					raise ValidationError(_("Name already exist"))
					
	@api.multi
	def write(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(EmployeeCategory, self).write(vals)
					
class Department(models.Model):
	_inherit = "hr.department"
	
	#@api.model
	#def create(self,vals):
		#name = (vals.get('name')).strip()
		#vals['name'] = name
		#return super(Department, self).create(vals)
	
	@api.one
	@api.constrains('name')
	def _check_name_constraints(self):
		if self.name:
			name = self.name.strip()
			self.env.cr.execute('''select count(id) as count from hr_department where LOWER(name) = LOWER(%s)''',((name),))
			for name_id in self.env.cr.dictfetchall():
				name_count = name_id['count']
				if name_count > 1:
					raise ValidationError(_("Department already exist"))
	#@api.multi
	#def write(self,vals):
		#name = (vals.get('name')).strip()
		#vals['name'] = name
		#return super(Department, self).write(vals)
	
class Job(models.Model):
	_inherit = "hr.job"
	
	#@api.model
	#def create(self,vals):
		#name = (vals.get('name')).strip()
		#vals['name'] = name
		#return super(Job, self.with_context(mail_create_nosubscribe=True)).create(vals)
	
	@api.one
	@api.constrains('name')
	def _check_name_constraints(self):
		if self.name:
			name = self.name.strip()
			self.env.cr.execute('''select count(id) as count from hr_job where LOWER(name) = LOWER(%s)''',((name),))
			for name_id in self.env.cr.dictfetchall():
				name_count = name_id['count']
				if name_count > 1:
					raise ValidationError(_("Job already exist"))
					
	#@api.multi
	#def write(self,vals):
		#name = (vals.get('name')).strip()
		#vals['name'] = name
		#return super(Job, self).write(vals)
		
class RecruitmentDegree(models.Model):
	_inherit = "hr.recruitment.degree"
	
	@api.model
	def create(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(RecruitmentDegree, self).create(vals)
	
	@api.one
	@api.constrains('name')
	def _check_name_constraints(self):
		if self.name:
			name = self.name.strip()
			self.env.cr.execute('''select count(id) as count from hr_recruitment_degree where LOWER(name) = LOWER(%s)''',((name),))
			for name_id in self.env.cr.dictfetchall():
				name_count = name_id['count']
				if name_count > 1:
					raise ValidationError(_("Degree already exist"))
					
	@api.multi
	def write(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(RecruitmentDegree, self).write(vals)
		
#class SuppliferInfo(models.Model):
	#_inherit = "product.supplierinfo"
	
	#@api.onchange('min_qty')
	#def onchange_min_qty(self):
		#if self.min_qty:
			#raise ValidationError(_("Unit Price Should be greater than zero"))
			
	#@api.one
	#@api.constrains('min_qty')
	#def constrains_min_qty(self):
		#print "?HAI"
		#if self.min_qty:
			#raise ValidationError(_("Unit Price Should be greater than zero"))
		
class Country(models.Model):
	_inherit = 'res.country'
	
	@api.one
	@api.constrains('name')
	def _check_name_constraints(self):
		if self.name:
			name = self.name.strip()
			self.env.cr.execute('''select count(id) as count from res_country where LOWER(name) = LOWER(%s)''',((name),))
			for name_id in self.env.cr.dictfetchall():
				name_count = name_id['count']
				if name_count > 1:
					raise ValidationError(_("Country already exist"))
					
class CountryState(models.Model):
	_inherit = 'res.country.state'
	
	@api.model
	def create(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(CountryState, self).create(vals)
	
	@api.one
	@api.constrains('name')
	def _check_name_constraints(self):
		if self.name:
			name = self.name.strip()
			self.env.cr.execute('''select count(id) as count from res_country_state where LOWER(name) = LOWER(%s)''',((name),))
			for name_id in self.env.cr.dictfetchall():
				name_count = name_id['count']
				if name_count > 1:
					raise ValidationError(_("State already exist"))
	
	@api.multi
	def write(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(CountryState, self).write(vals)
		
class PartnerTitle(models.Model):
	_inherit = 'res.partner.title'
	
	@api.model
	def create(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(PartnerTitle, self).create(vals)
	
	@api.one
	@api.constrains('name')
	def _check_name_constraints(self):
		if self.name:
			name = self.name.strip()
			self.env.cr.execute('''select count(id) as count from res_partner_title where LOWER(name) = LOWER(%s)''',((name),))
			for name_id in self.env.cr.dictfetchall():
				name_count = name_id['count']
				if name_count > 1:
					raise ValidationError(_("Title already exist"))
	
	@api.multi
	def write(self,vals):
		name = (vals.get('name')).strip()
		vals['name'] = name
		return super(PartnerTitle, self).write(vals)
		
class vendor_list(models.Model):
	_name = 'vendor.list'

	vendor_id = fields.Many2one('res.partner', 'Vendor')
	product_id = fields.Many2one('product.template', 'Product')
