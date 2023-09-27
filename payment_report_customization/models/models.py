from odoo import models, api
from num2words import num2words


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.depends('amount', 'currency_id')
    def compute_text(self):
        return num2words(self.amount_total).upper()
