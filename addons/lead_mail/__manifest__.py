# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Lead Mail',
    'version': '1.0',
    'category': 'Sales',
    'sequence': 5,
    'summary': 'Leads mail tracking',
    'description': """
The generic Odoo Customer Relationship Management
====================================================

This application enables a group of people to intelligently and efficiently manage leads, opportunities, meetings and activities.

It manages key tasks such as communication, identification, prioritization, assignment, resolution and notification.

Odoo ensures that all cases are successfully tracked by users, customers and vendors. It can automatically send reminders, trigger specific methods and many other actions based on your own enterprise rules.

The greatest thing about this system is that users don't need to do anything special. The CRM module has an email gateway for the synchronization interface between mails and Odoo. That way, users can just send emails to the request tracker.

Odoo will take care of thanking them for their message, automatically routing it to the appropriate staff and make sure all future correspondence gets to the right place.


Dashboard for CRM will include:
-------------------------------
* Planned Revenue by Stage and User (graph)
* Opportunities by Stage (graph)
""",
    'website': 'https://www.odoo.com/page/crm',
    'depends': ['crm'],
    'data': [
       'views/mail_lead_view.xml',
    ],
    'demo': [
        
    ],
    'css': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
