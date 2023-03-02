from odoo import fields, models


class AccountPayment(models.Model):

    _inherit = "account.payment"

    order_id = fields.Many2one(
        "sale.order",
        "Purchase",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    due_date = fields.Date('Due Date')


