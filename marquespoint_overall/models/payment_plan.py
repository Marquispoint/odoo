from odoo import fields, models, api


class PaymentPlan(models.Model):
    _name = 'payment.plan'
    _rec_name = 'name'

    name = fields.Char('Name')
    code = fields.Char('Code')
    percentage = fields.Float('Percentage')
    amount = fields.Float('Amount')
    is_booked = fields.Boolean('Is Booked')
