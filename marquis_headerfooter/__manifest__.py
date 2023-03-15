# -*- coding: utf-8 -*-
{
    'name': "marquis_headerfooter",

    'summary': """
        This module change the Default external layout to custom""",

    'description': """
        Long description of module's purpose
    """,

    'author': "M.Rizwan",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Customizations',
    'version': '15',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'branch'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/inherited_external_layout.xml',
        'views/account_move_document.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
