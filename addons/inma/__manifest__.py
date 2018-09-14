# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'INMA',
    'version': '1.1',
    'category': 'Inventory',
    'sequence': 79,
    'summary': 'Sales, Purchase, Inventory, Manufacturing',
    'description': """

Mapol Inventory Management
==========================

This application enables you to manage important aspects of your company's inventory and staff, other details such as their skills, contacts, working time...


You can manage:
---------------
* Sales
* Purchase
* inventory
* Manufacturing
* Employees and hierarchies : You can define your employee with User and display hierarchies
* HR Departments

    """,
    'website': 'http://www.mapolbs.com/',
    'images': [    ],
    'depends': [
        'base_setup',
        'mail',
        'resource',
        'web_kanban',
	    'sale',
	    'purchase',
	    'mrp',
	    'hr',
	    'hr_recruitment',
	    'stock',
	    'l10n_in',
	    'l10n_in_sale',
	    'l10n_in_purchase',
	    'l10n_in_stock',
    ],
    'data': [
	'security/inma_security.xml',
    'views/hr_view.xml',
    'report/purchase_order_design.xml',
	'report/purchase_quotation_design.xml',
	'report/srm_report_design.xml',
    'report/purchase_report.xml',
	'views/stock_requirement_memo_view.xml',
	'wizard/product_quantity_report.xml',
	'views/concrete_planning_schedule.xml',
	'security/ir.model.access.csv',
	'wizard/wizard_report_view.xml',
	'views/configuration_view.xml',
	'views/good_issue_slip_view.xml',
	'views/hr_attendance_view.xml',
	'views/purchase.xml',
	'wizard/production_summary_report_view.xml',
	'report/purchase_order_quotation_design.xml',
	'data/mail_template_data.xml',
	'report/report_invoice.xml',
    'wizard/lot_serial_view.xml',
    ],
    'demo': [
        'data/hr_demo.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
