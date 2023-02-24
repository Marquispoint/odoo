# -*- coding: utf-8 -*-
{
    'name': "marquespoint_overall",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "M.Rizwan",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'sale', 'ol_property_custom', 'project', 'crm'],

    # always loaded
    'data': [
        'wizard/installment_wizard_view.xml',
        "wizard/sale_advance_payment_wizard_view.xml",
        'security/ir.model.access.csv',
        'data/server.xml',
        'report/inherited_external_layout.xml',
        'report/sale_quote_report_template.xml',
        'report/report.xml',
        'data/mail_template_data.xml',
        'views/product_template_view.xml',
        'views/payment_plan_view.xml',
        'views/sale_order_view.xml',
        'views/payment_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
