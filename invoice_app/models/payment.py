from datetime import date
from odoo import api, fields, models, _

class Payment_Data(models.Model):


    _inherit='account.payment'

    branch_name=fields.Char(string='Branch Name')
    branch_reference=fields.Char(string='Branch Reference')
    tendered=fields.Integer(string='Tendered')
    tip=fields.Integer(string='Tip')
    order_business_date=fields.Date(string='Order Business Date')
    paid_at=fields.Char(string='Paid At')
    business_date=fields.Char(string='Business Date')
    order_reference=fields.Char(string='Order Reference')
    order_reference=fields.Char(string='Order Reference')
    employee_name=fields.Char(string='Employee Name')
    payment_type=fields.Selection([('bank','Bank'),('cash','Cash')],string="Payment Type",related='journal_id.type')

    @api.model
    def state_posted(self): 
        account_pay=self.env['account.payment'].search([('partner_type', 'in', ['customer']),('state','=','draft')])
        if account_pay:
            for am in account_pay:
                am.action_post()
    

    
