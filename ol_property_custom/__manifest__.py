{
    "name": "Property",

    "author": "Cognitive",
    'Maintainer': "M.Rizwan",
    "license": "OPL-1",
    'category': 'Customizations',
    "version": "15.0.1",

    "depends": [
        'project', 'sale_management', 'contacts', 'product', 'crm', 'sale_crm', 'account',
        'stock', 'sale_commission', 'ol_sales_agreement_report'],

    "data": [
        'security/ir.model.access.csv',
        'wizard/create_building.xml',
        'views/so_inherit.xml',
        'views/main_view.xml',
        'views/fields.xml',
        # 'views/installment_invoice_button.xml',

    ],

    "images": [['static/description/icon.png']],
    "auto_install": False,
    "application": True,
    "installable": True,
}
