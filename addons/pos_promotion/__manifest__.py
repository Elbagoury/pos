# -*- coding: utf-8 -*-
{
    'name': "POS Promotions",
    'version': '3.2',
    'live_test_url': 'http://demo.posodoo.com',
    'category': 'Point of Sale',
    'author': 'TL Technology',
    'sequence': 0,
    'summary': 'POS Promotions',
    'description': 'POS Promotions',
    'depends': ['point_of_sale'],
    'data': [
       # 'security/ir.model.access.csv',
        'data/product_data.xml',
       '__import__/template.xml',
        'views/pos_promotion.xml',
        'views/pos_config.xml',
        'views/pos_order.xml',
    ],
    'qweb': [
     'static/src/xml/*.xml'
    ],
    'price': '100',
    'website': 'http://demo.posodoo.com',
    'application': True,
    'images': ['static/description/icon.png'],
    'support': 'thanhchatvn@gmail.com',
    "currency": 'EUR',
    "license": "OPL-1"
}
