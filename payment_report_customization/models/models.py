from odoo import models, api
from num2words import num2words


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.depends('amount', 'currency_id')
    def compute_text(self):
        return num2words(self.amount_total).upper()

    def get_dynamic_header(self):
        if self.payment_type == 'inbound' and self.journal_id.name == 'Cash':
            return '<h4>Cash Receipt Voucher</h4>'
        elif self.payment_type == 'inbound' and self.journal_id.name == 'Bank':
            return '<h4>Bank Receipt Voucher</h4>'
        elif self.payment_type == 'outbound' and self.journal_id.name == 'Cash':
            return '<h4>Cash Payment Voucher</h4>'
        elif self.payment_type == 'outbound' and self.journal_id.name == 'Bank':
            return '<h4>Bank Payment Voucher</h4>'
        else:
            return '<h4> </h6>'
        # if self.payment_type == 'receive':
        #     if self.journal_id and self.journal_id.type == 'cash':
        #         return '<h6>Cash Receipt Voucher</h6>'
        #     elif self.journal_id and self.journal_id.type == 'bank':
        #         return '<h6>Bank Receipt Voucher</h6>'
        #     else:
        #         return '<h6>Nothing</h6>'

