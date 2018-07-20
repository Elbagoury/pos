# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'HRMSMAPOL',
    'version': '1.1',
    'category': 'HrmsMapol',
    'sequence': 71,
    'summary': 'hr',


    'depends': ['hr','project','hr_holidays'],

    'data': [
        'views/hrms_hr_view.xml',
        'security/mapol_security.xml',
        'security/ir.model.access.csv',  
	'wizard/project_details_wizard_view.xml',
	'views/hrms_holiday_view.xml',     
        
    ],
    'demo': [
        
    ],
    'css': ['static/src/css/sale.css'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
