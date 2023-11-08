# -*- coding: utf-8 -*-
{
    'name': "payment report customization",
    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '15.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account','web'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/payment_report_inherit.xml',
        'report/copy_payment_report_inherit.xml',
        'report/report_action.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/payment_report_custom_header_footer_layout.xml',

    ],
}
