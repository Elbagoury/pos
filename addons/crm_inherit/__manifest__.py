# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'CRM Inherit',
    'version': '1.0',
    'category': 'Sales',
    'sequence': 5,
    'summary': 'Leads, Opportunities, Activities',
    'description': """

* Planned Revenue by Stage and User (graph)
* Opportunities by Stage (graph)
""",
    'website': 'https://www.odoo.com/page/crm',
    'depends': [
        'crm','purchase',
    ],
    'data': [
        'views/crm_view.xml',
    ],
    'demo': [
        
    ],
  
    'installable': True,
    'application': True,
    'auto_install': False,
}
