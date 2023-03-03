# -*- coding: utf-8 -*-

import datetime
from lxml import etree
from odoo import models, fields, api, _
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from odoo.tools import float_compare


class PDCBank(models.Model):
    _name = 'pdc.commercial.bank'

    name = fields.Char('Name')


class PDCPayment(models.Model):
    _name = 'pdc.payment'
    _description = 'PDC Payment'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Partner', tracking=True)
    payment_amount = fields.Float(string='Payment Amount', tracking=True)
    # cheque_ref = fields.Many2one('pdc.commercial.bank', string='Commercial Bank Name', tracking=True)
    commercial_bank_id = fields.Many2one('pdc.commercial.bank', string='Commercial Bank Name', tracking=True)
    memo = fields.Char(string='Memo', tracking=True)
    destination_account_id = fields.Many2one('account.account', string='Bank', tracking=True)
    journal_id = fields.Many2one('account.journal', string='Journal', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', tracking=True)
    pdc_type = fields.Selection([('sent', 'Sent'),
                                 ('received', 'Received'),
                                 ], string='PDC Type', tracking=True)

    # Date Fields

    date_payment = fields.Date(string='Payment Date', tracking=True)
    date_registered = fields.Date(string='Registered Date', tracking=True)
    date_cleared = fields.Date(string='Cleared Date', tracking=True)
    date_bounced = fields.Date(string='Bounced Date', tracking=True)

    state = fields.Selection([('draft', 'Draft'),
                              ('registered', 'Registered'),
                              ('bounced', 'Bounced'),
                              ('cleared', 'Cleared'),
                              ('cancel', 'Cancel'),
                              ], string='State', default='draft', tracking=True, readonly=True, index=True, copy=False)

    registered_counter = fields.Integer('Registered', compute='get_registered_jv_count')
    bounce_counter = fields.Integer('Bounce', compute='get_bounce_jv_count')
    cleared_counter = fields.Integer('Cleared', compute='get_cleared_jv_count')

    move_id = fields.Many2one('account.move', string='Invoice/Bill Ref')
    move_ids = fields.Many2many('account.move', string='Invoices/Bills Ref')
    cheque_no = fields.Char()
    branch_id = fields.Many2one('res.branch', string='Branch')

    def check_balance(self):
        partner_ledger = self.env['account.move.line'].search(
            [('partner_id', '=', self.partner_id.id),
             ('move_id.state', '=', 'posted'), ('full_reconcile_id', '=', False), ('balance', '!=', 0),
             ('account_id.reconcile', '=', True), ('full_reconcile_id', '=', False), '|',
             ('account_id.internal_type', '=', 'payable'), ('account_id.internal_type', '=', 'receivable')])
        bal = 0
        for par_rec in partner_ledger:
            bal = bal + (par_rec.debit - par_rec.credit)

    @api.model
    def create(self, vals):
        sequence = self.env.ref('pdc_payments.pdc_payment_seq')
        vals['name'] = sequence.next_by_id()
        rec = super(PDCPayment, self).create(vals)
        rec.button_register()
        return rec

    def action_registered_jv(self):
        lines = []
        for record in self:
            if record.pdc_type == 'received':
                move_dict = {
                    'ref': record.name,
                    'move_type': 'entry',
                    'journal_id': record.journal_id.id,
                    'partner_id': record.partner_id.id,
                    'date': record.date_registered,
                    'state': 'draft',
                    'pdc_registered_id': self.id,
                }
                debit_line = (0, 0, {
                    'name': 'PDC Registered',
                    'debit': record.payment_amount,
                    'credit': 0.0,
                    'partner_id': record.partner_id.id,
                    'account_id': int(self.env['ir.config_parameter'].get_param('pdc_payments.pdc_bnk_customer')),
                })
                lines.append(debit_line)
                credit_line = (0, 0, {
                    'name': 'PDC Registered',
                    'debit': 0.0,
                    'partner_id': record.partner_id.id,
                    'credit': record.payment_amount,
                    'account_id': int(self.env['ir.config_parameter'].get_param('pdc_payments.pdc_receivable')),
                })
                lines.append(credit_line)
                move_dict['line_ids'] = lines
                move = self.env['account.move'].create(move_dict)
            else:
                move_dict = {
                    'ref': record.name,
                    'move_type': 'entry',
                    'journal_id': record.journal_id.id,
                    'partner_id': record.partner_id.id,
                    'date': record.date_registered,
                    'state': 'draft',
                    'pdc_registered_id': self.id,
                }
                debit_line = (0, 0, {
                    'name': 'PDC Registered',
                    'debit': 0.0,
                    'credit': record.payment_amount,
                    'partner_id': record.partner_id.id,
                    'account_id': int(self.env['ir.config_parameter'].get_param('pdc_payments.pdc_bnk_vendor')),
                })
                lines.append(debit_line)
                credit_line = (0, 0, {
                    'name': 'PDC Registered',
                    'debit': record.payment_amount,
                    'partner_id': record.partner_id.id,
                    'credit': 0.0,
                    'account_id': int(self.env['ir.config_parameter'].get_param('pdc_payments.pdc_payable')),
                })
                lines.append(credit_line)
                move_dict['line_ids'] = lines
                move = self.env['account.move'].create(move_dict)
        # self.date_registered = datetime.today().date()

    def action_bounce_jv(self):
        lines = []
        for record in self:
            if record.pdc_type == 'received':
                if not record.date_bounced:
                    record.date_bounced = datetime.today().date()
                move_dict = {
                    'ref': record.name,
                    'move_type': 'entry',
                    'journal_id': record.journal_id.id,
                    'partner_id': record.partner_id.id,
                    'date': record.date_bounced,
                    'state': 'draft',
                    'pdc_bounce_id': self.id,
                }
                debit_line = (0, 0, {
                    'name': 'PDC Bounced',
                    'debit': record.payment_amount,
                    'credit': 0.0,
                    'partner_id': record.partner_id.id,
                    'account_id': int(self.env['ir.config_parameter'].get_param('pdc_payments.pdc_receivable')),
                })
                lines.append(debit_line)
                credit_line = (0, 0, {
                    'name': 'PDC Bounced',
                    'debit': 0.0,
                    'partner_id': record.partner_id.id,
                    'credit': record.payment_amount,
                    'account_id': int(self.env['ir.config_parameter'].get_param('pdc_payments.pdc_bnk_customer')),
                })
            else:
                if not record.date_bounced:
                    record.date_bounced = datetime.today().date()
                move_dict = {
                    'ref': record.name,
                    'move_type': 'entry',
                    'journal_id': record.journal_id.id,
                    'partner_id': record.partner_id.id,
                    'date': record.date_bounced,
                    'state': 'draft',
                    'pdc_bounce_id': self.id,
                }
                debit_line = (0, 0, {
                    'name': 'PDC Bounced',
                    'debit': 0.0,
                    'credit': record.payment_amount,
                    'partner_id': record.partner_id.id,
                    'account_id': int(self.env['ir.config_parameter'].get_param('pdc_payments.pdc_payable')),
                })
                lines.append(debit_line)
                credit_line = (0, 0, {
                    'name': 'PDC Bounced',
                    'debit': record.payment_amount,
                    'partner_id': record.partner_id.id,
                    'credit': 0.0,
                    'account_id': int(self.env['ir.config_parameter'].get_param('pdc_payments.pdc_bnk_vendor')),
                })
            lines.append(credit_line)
            move_dict['line_ids'] = lines
            move = self.env['account.move'].create(move_dict)

    def action_cleared_jv(self):
        lines = []
        for record in self:
            if record.pdc_type == 'received':
                if not record.date_cleared:
                    record.date_cleared = datetime.today().date()
                move_dict = {
                    'ref': record.name,
                    'move_type': 'entry',
                    'journal_id': record.journal_id.id,
                    'partner_id': record.partner_id.id,
                    'date': record.date_cleared,
                    'state': 'draft',
                    'branch_id': record.branch_id.id,
                    'pdc_cleared_id': self.id,
                }
                debit_line = (0, 0, {
                    'name': 'PDC Cleared',
                    'debit': 0.0,
                    'credit': record.payment_amount,
                    'partner_id': record.partner_id.id,
                    'account_id': int(self.env['ir.config_parameter'].get_param('pdc_payments.pdc_bnk_customer')),
                })
                lines.append(debit_line)
                credit_line = (0, 0, {
                    'name': 'PDC Cleared',
                    'debit': record.payment_amount,
                    'partner_id': record.partner_id.id,
                    'credit': 0.0,
                    'account_id': int(self.env['ir.config_parameter'].get_param('pdc_payments.pdc_receivable')),
                })
                lines.append(credit_line)
                debit_line = (0, 0, {
                    'name': 'PDC Cleared',
                    'debit': record.payment_amount,
                    'credit': 0.0,
                    'partner_id': record.partner_id.id,
                    'account_id': record.destination_account_id.id,
                })
                lines.append(debit_line)
                credit_line = (0, 0, {
                    'name': 'PDC Cleared',
                    'debit': 0.0,
                    'partner_id': record.partner_id.id,
                    'credit': record.payment_amount,
                    'account_id': record.partner_id.property_account_receivable_id.id,
                })
                lines.append(credit_line)
                move_dict['line_ids'] = lines
                move = self.env['account.move'].create(move_dict)
                move.action_post()
            else:
                if not record.date_cleared:
                    record.date_cleared = datetime.today().date()
                move_dict = {
                    'ref': record.name,
                    'move_type': 'entry',
                    'journal_id': record.journal_id.id,
                    'partner_id': record.partner_id.id,
                    'date': record.date_cleared,
                    'state': 'draft',
                    'branch_id': record.branch_id.id,
                    'pdc_cleared_id': self.id,
                }
                debit_line = (0, 0, {
                    'name': 'PDC Cleared',
                    'debit': record.payment_amount,
                    'credit': 0.0,
                    'partner_id': record.partner_id.id,
                    'account_id': int(self.env['ir.config_parameter'].get_param('pdc_payments.pdc_bnk_vendor')),
                })
                lines.append(debit_line)
                credit_line = (0, 0, {
                    'name': 'PDC Cleared',
                    'debit': 0.0,
                    'partner_id': record.partner_id.id,
                    'credit': record.payment_amount,
                    'account_id': int(self.env['ir.config_parameter'].get_param('pdc_payments.pdc_payable')),
                })
                lines.append(credit_line)
                debit_line = (0, 0, {
                    'name': 'PDC Cleared',
                    'debit': 0.0,
                    'credit': record.payment_amount,
                    'partner_id': record.partner_id.id,
                    'account_id': record.destination_account_id.id,
                })
                lines.append(debit_line)
                credit_line = (0, 0, {
                    'name': 'PDC Cleared',
                    'debit': record.payment_amount,
                    'partner_id': record.partner_id.id,
                    'credit': 0.0,
                    'account_id': record.partner_id.property_account_payable_id.id,
                })
                lines.append(credit_line)
                move_dict['line_ids'] = lines
                move = self.env['account.move'].create(move_dict)
                move.action_post()
        self.date_cleared = datetime.today().date()

    def button_register(self):
        self.action_registered_jv()
        self.write({
            'state': 'registered'
        })

    def button_cancel(self):
        self.write({
            'state': 'cancel'
        })

    def button_bounce(self):
        self.action_bounce_jv()
        self.write({
            'state': 'bounced'
        })

    def button_cleared(self):
        self.action_cleared_jv()
        self.write({
            'state': 'cleared'
        })

    def action_get_registered_jv(self):
        return {
            'name': _('PDC Payment'),
            'domain': [('pdc_registered_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'account.move',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def get_registered_jv_count(self):
        for rec in self:
            count = self.env['account.move'].search_count([('pdc_registered_id', '=', rec.id)])
            rec.registered_counter = count

    def action_get_bounce_jv(self):
        return {
            'name': _('PDC Payment'),
            'domain': [('pdc_bounce_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'account.move',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def get_bounce_jv_count(self):
        for rec in self:
            count = self.env['account.move'].search_count([('pdc_bounce_id', '=', rec.id)])
            rec.bounce_counter = count

    def action_get_cleared_jv(self):
        return {
            'name': _('PDC Payment'),
            'domain': [('pdc_cleared_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'account.move',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def get_cleared_jv_count(self):
        for rec in self:
            count = self.env['account.move'].search_count([('pdc_cleared_id', '=', rec.id)])
            rec.cleared_counter = count

    @api.onchange('journal_id')
    def _onchange_state(self):
        for rec in self:
            if rec.journal_id:
                rec.destination_account_id = rec.journal_id.default_account_id.id


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    pdc_ref = fields.Char(string='PDC Reference', tracking=True)
    # available_partner_bank_ids = fields.Many2many('res.bank')


class AccountEdiDocument(models.Model):
    _inherit = 'account.edi.document'

    def action_export_xml(self):
        pass


class AccountMove(models.Model):
    _inherit = 'account.move'

    pdc_registered_id = fields.Many2one('pdc.payment')
    pdc_bounce_id = fields.Many2one('pdc.payment')
    pdc_cleared_id = fields.Many2one('pdc.payment')

    pdc_count = fields.Integer(string="PDC", compute='_compute_pdc_count')
    is_pdc_created = fields.Boolean()

    def action_pdc_payment_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'PDC Wizard',
            'view_id': self.env.ref('pdc_payments.view_pdc_payment_wizard_form', False).id,
            'target': 'new',
            'context': {'default_partner_id': self.partner_id.id,
                        'default_payment_amount': self.amount_residual,
                        'default_date_payment': self.invoice_date_due,
                        'default_currency_id': self.currency_id.id,
                        'default_move_id': self.id,
                        'default_move_ids': [self.id],
                        'default_branch_id': self.branch_id.id,
                        'default_memo': self.name,
                        'default_pdc_type': 'received' if self.move_type == 'out_invoice' else 'sent',
                        },
            'res_model': 'pdc.payment.wizard',
            'view_mode': 'form',
        }

    def action_combine_pdc_payment_wizard(self):
        selected_ids = self.env.context.get('active_ids', [])
        selected_records = self.env['account.move'].browse(selected_ids)
        # print(selected_records)
        if any(res.state != 'posted' for res in selected_records) or len(
                selected_records.mapped('partner_id')) > 1 or len(selected_records.mapped('journal_id')) > 1:
            raise ValidationError('Invoices must be in Posted state And Journal must be same. ')
        for res in selected_records:
            if res.is_pdc_created:
                raise UserError(_('PDC of invoice %s is already created.') % res.name)
        # if any(res.is_pdc_created):
        #     raise ValidationError('PDC of ')
        return {
            'type': 'ir.actions.act_window',
            'name': 'PDC Wizard',
            'view_id': self.env.ref('pdc_payments.view_pdc_payment_wizard_form', False).id,
            'target': 'new',
            'context': {'default_partner_id': selected_records[0].partner_id.id,
                        'default_payment_amount': sum(selected_records.mapped('amount_residual')),
                        # 'default_date_payment': self.invoice_date_due,
                        'default_currency_id': selected_records[0].currency_id.id,
                        'default_move_ids': selected_records.ids,
                        'default_pdc_type': 'received' if selected_records[0].move_type == 'out_invoice' else 'sent',
                        },
            'res_model': 'pdc.payment.wizard',
            'view_mode': 'form',
        }

    def action_show_pdc(self):
        return {
            'name': _('PDC Payments'),
            'view_mode': 'tree,form',
            'res_model': 'pdc.payment',
            'domain': [('move_ids', 'in', [self.id])],
            'context': {'default_partner_id': self.partner_id.id,
                        'default_payment_amount': self.amount_residual,
                        'default_date_payment': self.invoice_date_due,
                        'default_currency_id': self.currency_id.id,
                        'default_move_id': self.id,
                        'default_move_ids': [self.id],
                        'default_branch_id': self.branch_id.id,
                        'default_memo': self.name,
                        'default_pdc_type': 'received' if self.move_type == 'out_invoice' else 'sent',
                        },
            'type': 'ir.actions.act_window',
        }

    def _compute_pdc_count(self):
        records = self.env['pdc.payment'].search_count([('move_ids', 'in', [self.id])])
        self.pdc_count = records
