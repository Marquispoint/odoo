from odoo import models, api
from num2words import num2words


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.depends('amount', 'currency_id')
    def compute_text(self):
        return num2words(self.amount_total).upper()

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


