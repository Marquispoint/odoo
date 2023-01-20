{
    "name": "Property",

    "author": "Huzaifa",
    "category": "sale",

    "license": "OPL-1",

    "version": "15.0.1",

    "depends": [
        'project', 'sale_management', 'contacts', 'product', 'crm', 'sale_crm', 'ol_sales_agreement_report', 'account',
        'stock'],

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
