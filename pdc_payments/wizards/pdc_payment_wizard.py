from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PDCPaymentWizard(models.TransientModel):
    _name = 'pdc.payment.wizard'
    _description = 'PDC Payment'

    partner_id = fields.Many2one('res.partner', string='Partner', )
    payment_amount = fields.Float(string='Payment Amount')
    # cheque_ref = fields.Char(string='Commercial Name')
    commercial_bank_id = fields.Many2one('pdc.commercial.bank', string='Commercial Bank Name', tracking=True)
    memo = fields.Char(string='Memo')
    destination_account_id = fields.Many2one('account.account', string='Bank')
    journal_id = fields.Many2one('account.journal', string='Journal')
    currency_id = fields.Many2one('res.currency', string='Currency')
    pdc_type = fields.Selection([('sent', 'Sent'),
                                 ('received', 'Received'),
                                 ], string='PDC Type', )

    date_payment = fields.Date(string='Due Date')
    date_registered = fields.Date(string='Registered Date')
    cheque_no = fields.Char()
    move_id = fields.Many2one('account.move', string='Invoice/Bill Ref')
    move_ids = fields.Many2many('account.move', string='Invoices/Bills Ref')
    branch_id = fields.Many2one('res.branch', string='Branch')

    @api.onchange('journal_id')
    def _onchange_journal(self):
        for rec in self:
            if rec.journal_id:
                rec.destination_account_id = rec.journal_id.default_account_id.id

    def create_pdc_payments(self):
        # model = self.env.context.get('active_model')
        # rec = self.env[model].browse(self.env.context.get('active_id'))
        for record in self:
            if record.pdc_type == 'received':
                vals = {
                    'partner_id': record.partner_id.id,
                    'journal_id': record.journal_id.id,
                    # 'move_id': rec.id,
                    'move_ids': record.move_ids.ids,
                    'date_payment': record.date_payment,
                    'date_registered': record.date_registered,
                    # 'destination_account_id': record.journal_id.default_account_id.id,
                    'destination_account_id': record.destination_account_id.id,
                    'currency_id': record.currency_id.id,
                    'commercial_bank_id': record.commercial_bank_id.id,
                    'payment_amount': record.payment_amount,
                    'cheque_no': record.cheque_no,
                    'pdc_type': 'received',
                    'branch_id': record.branch_id.id,
                    'purchaser_id': record.purchaser_id.id,
                }
                record = self.env['pdc.payment'].create(vals)
            elif record.pdc_type == 'sent':
                vals = {
                    'partner_id': record.partner_id.id,
                    'journal_id': record.journal_id.id,
                    # 'move_id': rec.id,
                    'move_ids': record.move_ids.ids,
                    'date_payment': record.date_payment,
                    'date_registered': record.date_registered,
                    'destination_account_id': record.journal_id.default_account_id.id,
                    'currency_id': record.currency_id.id,
                    'payment_amount': record.payment_amount,
                    'cheque_no': record.cheque_no,
                    'pdc_type': 'sent',
                    'branch_id': record.branch_id.id,
                    'purchaser_id': record.purchaser_id.id,
                }
                record = self.env['pdc.payment'].create(vals)

            for r in self.move_ids:
                r.is_pdc_created = True

    # Purchaser Flow ----------------------------------------------------------------
    purchaser_ids = fields.Many2many(comodel_name='res.partner', compute="_compute_purchaser_ids")
    purchaser_id = fields.Many2one(comodel_name='res.partner', string='Purchaser',
                                   domain="[('id', 'in', purchaser_ids)]")
    is_invoice = fields.Boolean('Is invoice', compute="_compute_purchaser_ids")

    @api.depends('move_ids')
    def _compute_purchaser_ids(self):
        model = self.env.context.get('active_model')
        active_id = self.env[model].browse(self.env.context.get('active_id'))
        print(active_id.move_type)
        if active_id.purchaser_ids and active_id.move_type == 'out_invoice':
            self.is_invoice = True
            self.purchaser_ids = active_id.purchaser_ids.ids
        else:
            self.is_invoice = False
            self.purchaser_ids = []
    # -------------------------------------------------------------------------------
