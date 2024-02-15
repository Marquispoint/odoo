# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    sequence_account = fields.Char("Sequence")


    @api.model_create_multi
    def create(self, vals_list):
        payment_done = super(AccountPayment, self).create(vals_list)
        sequence = self.env.ref('pdc_payments.pdc_account_seq')
        payment_sequence = payment_done.journal_id.code + '-'+ payment_done.branch_id.short_code+ '/'+str(payment_done.date.year)+'/'+str(payment_done.date.month)
        payment_done.sequence_account = payment_sequence+sequence.next_by_id()
        return payment_done
    @api.depends('move_id.name')
    def name_get(self):
        for rec in self:
            rec.name = rec.sequence_account
        return [(payment.id, payment.move_id.name != '/' and payment.sequence_account or _('Draft Payment')) for payment in self]


class ResBranch(models.Model):
    _inherit = "res.branch"

    short_code = fields.Char("Sequence")
