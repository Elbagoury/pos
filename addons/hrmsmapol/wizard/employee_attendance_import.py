import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

class attendance_import(models.TransientModel):
	_name="attendance.import"
	
	file_to_import_attendance = fields.Binary('Attendance File')
	
	
