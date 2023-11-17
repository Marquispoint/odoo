from odoo import models, api
from num2words import num2words


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.depends('amount', 'currency_id')
    def compute_text(self):
        for record in self:
            amount_without_commas = str(record.amount).replace(',', '')  # Remove commas from the amount
            text = num2words(amount_without_commas, lang='en')
            text_without_commas = text.replace(',', '')  # Remove commas from the words
            abc = 'AED'+' '+text_without_commas.upper().replace('POINT', 'AND')+' '+'FILS'
            return abc
    # @api.depends('amount', 'currency_id')
    # def compute_text(self):
    #     return num2words(self.amount_total).upper()

    def get_dynamic_header(self):
        for rec in self:
            if rec.payment_type == 'inbound' and rec.journal_id.type == 'cash':
                return '<h4>Cash Receipt Voucher</h4>'
            elif rec.payment_type == 'inbound' and rec.journal_id.type == 'bank':
                return '<h4>Bank Receipt Voucher</h4>'
            elif rec.payment_type == 'outbound' and rec.journal_id.type == 'cash':
                return '<h4>Cash Payment Voucher</h4>'
            elif rec.payment_type == 'outbound' and rec.journal_id.type == 'bank':
                return '<h4>Bank Payment Voucher</h4>'
            else:
                return '<h4></h4>'

    def customer_supplier(self):
        for rec in self:
            # if rec.payment_type == 'inbound' and rec.journal_id.type == 'cash':
            #     return '<strong>Customer</strong>'
            # elif rec.payment_type == 'inbound' and rec.journal_id.type == 'bank':
            #     return '<strong>Customer</strong>'
            # elif rec.payment_type == 'outbound' and rec.journal_id.type == 'cash':
            #     return '<strong>Customer</strong>'
            if rec.payment_type == 'outbound' and rec.journal_id.type == 'bank':
                return '<strong>Supplier:</strong>'
            else:
                return '<strong>Customer:</strong>'




