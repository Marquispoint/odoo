from odoo import fields, models, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    purchaser_ids = fields.Many2many(comodel_name='res.partner', string='Purchaser', compute='_compute_purchaser_ids')

    @api.depends('so_ids')
    def _compute_purchaser_ids(self):
        for move in self:
            if move.so_ids:
                purchasers = [
                    (6, 0, move.mapped("so_ids.purchaser_ids.purchase_individual").ids)
                ]
                move.purchaser_ids = purchasers
            else:
                move.purchaser_ids = []


class PaymentWizardInherit(models.TransientModel):
    _inherit = "account.payment.register"

    purchaser_ids = fields.Many2many(comodel_name='res.partner', compute="_compute_purchaser_ids")
    purchaser_id = fields.Many2one(comodel_name='res.partner', string='Purchaser',
                                   domain="[('id', 'in', purchaser_ids)]")

    @api.depends('communication')
    def _compute_purchaser_ids(self):
        model = self.env.context.get('active_model')
        active_id = self.env[model].browse(self.env.context.get('active_id'))
        if active_id.purchaser_ids:
            self.purchaser_ids = active_id.purchaser_ids.ids
        else:
            self.purchaser_ids = []

    def _create_payment_vals_from_wizard(self):
        vals = super(PaymentWizardInherit, self)._create_payment_vals_from_wizard()
        vals.update({
            'purchaser_id': self.purchaser_id.id,
        })
        return vals

    def _create_payment_vals_from_batch(self):
        vals = super(PaymentWizardInherit, self)._create_payment_vals_from_batch()
        vals.update({
            'purchaser_id': self.purchaser_id.id,
        })
        return vals


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    purchaser_id = fields.Many2one(comodel_name='res.partner', string='Purchaser')
