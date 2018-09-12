# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Pos',
    'version': '1.2',
    'category': 'POS',
    'depends': ['point_of_sale','bus','purchase'],
    'description': """

    """,
    'data': [
   
        'views/pump_views.xml',
     	'wizard/operator_monitor_report_view.xml',
	'wizard/cash_drops_report_view.xml',
	'wizard/sales_report_view.xml',
	'wizard/fuel_delivery_report_view.xml',
	'wizard/update_qty_on_tank_view.xml',
	'views/product_view.xml',
	'wizard/pump_meter_reading_view.xml',
	'wizard/day_summary_report_view.xml',
	'wizard/receipts_report_view.xml',
	'wizard/sales_summary_report_view.xml',
	'wizard/payment_summary_report_view.xml',
	'views/valet_reconciliation_view.xml',
	'security/pos_security.xml',
	'security/ir.model.access.csv',
	'wizard/pay_in_out_report_view.xml',
	'wizard/wet_stock_variance_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
