from datetime import date
from odoo import api, fields, models, _
from openerp.tools.translate import _
from openerp.exceptions import UserError

class Invoice_Data(models.Model):


    _inherit='account.move'
    branch_name=fields.Char(string='Branch Name')
    source=fields.Char(string='Source')
    number= fields.Integer(string='Number')
    original_order_reference=fields.Char(string='Order Reference')
    business_date=fields.Char(string='Business Date')
    coupon_code=fields.Char(string='Coupon Code')
    coupon_name=fields.Char(string='Coupon Name')
    discount_name=fields.Char(string='Discount')
    guests=fields.Boolean(string='Guests')
    typee=fields.Selection([('Pick up','Pick up'),('Dine In','Dine In')],string="Type")
    created_at= fields.Char(string="Created at")
    created_by=fields.Char(string='Creator')
    opened_at= fields.Char(string="Opened at")
    closed_at= fields.Char(string="Closed at")
    closed_by=fields.Char(string='Closed By')
    check_number= fields.Integer(string='Check Number')
    receipt_notes=fields.Char(string='Receipt Note')
    kitchen_notes=fields.Char(string='kitchen Note')
    kitchen_recieved_at= fields.Char(string="Kitchen Recieved")
    kitchen_done_at= fields.Char(string="Kitchen Done")
    preparation_period=fields.Char(string='Preparation Period')
    invoice_date=fields.Date(string='Invoice Date')
    invoice_number=fields.Char(string='Invoice Number')
    destination=fields.Selection([('sulay','Sulay Warehouse'),('yogi','YOGi Al Mathar'),('waha','YOGi Al Waha'),('ck','YOGi CK'),('kitch','YOGi Kitch'),('magla','YOGi Magla'),('rdc','YOGi RDC'),('safarat','YOGi Safarat')],string="Destination",default='safarat')
    database_id=fields.Char(string='Database Id')
    
    @api.model
    def state_change(self): 
        account_move=self.env['account.move'].search([('state','=','draft')])
        if  account_move:
            for am in account_move:
                am.action_post()

        
    @api.model
    def outstanding_pay(self): 
        
        unpaid_inv=self.env['account.move'].search([('payment_state','=','not_paid')])
        paym=self.env['account.payment'].search([('state','=','posted')])
        for inv in unpaid_inv:
            for p in paym:
                if inv.payment_reference == p.order_reference:
                    line_id=self.env['account.move.line'].search([('move_id','=',p.move_id.id),('debit','=',0)])
                    inv.js_assign_outstanding_line(line_id.id)

              


































