{
    'name' : 'Invoice',
    'version' : '1.1',
    'summary': 'Custom module',
    'sequence': 10,
    'description': "Customization in odoo modules",
    'category': 'Services',
    'license': 'LGPL-3',
    'images' : [],
    'depends' : ['account'],
    'data': [
 
        'views/view.xml',
        'views/payment.xml',
        'data/schedule_action.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
