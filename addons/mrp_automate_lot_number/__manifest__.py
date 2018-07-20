# -*- coding: utf-8 -*-
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Mrp Automate Lot Number",

    'summary': """
             This module is used to allocate the lot number automatically based on the product quantity""",

    'version': '10.0.1.0.0',
    'category': 'Uncategorized',
    'website': "http://sodexis.com/",
    'author': "Sodexis, Inc <dev@sodexis.com>",
    'license': 'AGPL-3',
    'installable': True,
    'depends': ['base', 'mrp'],
    'data': [
        'wizard/mrp_product_produce_view.xml',
        'views/mrp_view.xml',
    ],
    'demo': [],
    'qweb': [],
}
