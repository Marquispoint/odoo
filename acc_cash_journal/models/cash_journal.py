from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CashJournal(models.Model):
    _name = "cash.journal"
    _description = "Cash Journal"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'payment_type'

    payment_type = fields.Selection([
        ('send', 'Send Money'),
        ('receive', 'Receive Money')], string="Payment Type")
    company_id = fields.Many2one('res.company', string="Company", tracking=True)
    branch_id = fields.Many2one('res.branch', string="Branch", tracking=True)
    # amount = fields.Float(string='Amount')
    journal_id = fields.Many2one('account.journal', string="Bank / Cash", track_visibility='onchange')
    voucher_type = fields.Selection([
        ('cpv', 'Cash Payment Voucher'),
        ('bpv', 'Bank Payment Voucher'),
    ])
    journal_item = fields.Many2many('account.move', string="Journal Entry", track_visibility='onchange')
    state = fields.Selection([('draft', 'Darft'), ('validate', 'Validate'), ('cancel', 'Cancelled')],default='draft',
                             string="State", tracking=True)

    cash_journal_lines_id = fields.One2many('cash.lines', 'cash_journal_id')

    @api.model
    def create(self, values):
        res = super(CashJournal, self).create(values)
        if res.branch_id:
            for line in res.cash_journal_lines_id:
                line.analytical_account_id = res.branch_id.analytical_account_id.id
        return res


    def write(self, values):
        res = super(CashJournal, self).write(values)
        if 'branch_id' in values:
            for line in self.cash_journal_lines_id:
                line.analytical_account_id = self.branch_id.analytical_account_id.id
        return res

    @api.onchange('journal_id')
    def change_journal(self):
        if self.journal_id.name == 'Bank':
            self.voucher_type = 'bpv'
        else:
            self.voucher_type = 'cpv'

    # @api.onchange('branch_id')
    # def change_branch_id(self):
    #     for rec in self:
    #         if rec.branch_id:
    #             for line in rec.cash_journal_lines_id:
    #                 line.analytical_account_id = rec.branch_id.analytical_account_id.id

    def unlink(self):
        for x in self:
            if x.journal_item:
                raise ValidationError('You cannot delete an entry which has been posted once.')
            # if x.state in ["validate"]:
        rec = super(CashJournal,self).unlink()
        return rec

    def action_validate(self):
        for rec in self:
            lines = []
            lines1 = []
            records = []
            # if not rec.journal_item:
            if rec.payment_type == 'receive':
                for r in rec.cash_journal_lines_id:
                    # print(r)
                    move_dict = {
                        # 'ref': record.name,
                        'branch_id': rec.branch_id.id,
                        'move_type': 'entry',
                        'journal_id': rec.journal_id.id,
                        # 'partner_id': record.partner_id.id,
                        'date': r.date,
                        'state': 'draft',
                    }
                    debit_line = (0, 0, {
                        'name': r.description,
                        'debit': r.amount,
                        'credit': 0.0,
                        'partner_id': r.partner_id.id,
                        'account_id': rec.journal_id.default_account_id.id,
                        'analytic_account_id': r.analytical_account_id.id,
                    })
                    lines.append(debit_line)
                    credit_line = (0, 0, {
                        'name': r.description,
                        'debit': 0.0,
                        'partner_id': r.partner_id.id,
                        'credit': r.amount,
                        'account_id': r.account_id.id,
                        'analytic_account_id': r.analytical_account_id.id,
                    })
                    lines.append(credit_line)
                    move_dict['line_ids'] = lines
                    print(move_dict)
                    move = self.env['account.move'].create(move_dict)
                    # print('JV Created')
                    lines = []
                    records.append(move.id)
                    move.action_post()
            else:
                for r in rec.cash_journal_lines_id:
                    move_dict = {
                        # 'ref': record.name,
                        'branch_id': rec.branch_id.id,
                        'move_type': 'entry',
                        'journal_id': rec.journal_id.id,
                        # 'partner_id': record.partner_id.id,
                        'date': r.date,
                        'state': 'draft',
                    }
                    debit_line = (0, 0, {
                        'name': r.description,
                        'debit': 0.0,
                        'credit': r.amount,
                        'partner_id': r.partner_id.id,
                        'account_id': rec.journal_id.default_account_id.id,
                        'analytic_account_id': r.analytical_account_id.id,
                    })
                    lines1.append(debit_line)
                    credit_line = (0, 0, {
                        'name': r.description,
                        'debit': r.amount,
                        'partner_id': r.partner_id.id,
                        'credit': 0.0,
                        'account_id': r.account_id.id,
                        'analytic_account_id': r.analytical_account_id.id,
                    })
                    lines1.append(credit_line)
                    move_dict['line_ids'] = lines1
                    print(move_dict)
                    move = self.env['account.move'].create(move_dict)
                    # print('JV Created')
                    lines1 = []
                    records.append(move.id)
                    move.action_post()
            # print(records)
            rec.state = 'validate'
            rec.journal_item = records


    # def action_reset_draft(self):
    #     self.state = 'draft'
    #     self.journal_item.state = 'draft'

    def action_cancel(self):
        self.state = 'cancel'
        self.journal_item.button_cancel()

    def journal_entries_button(self):
        return {
            'name': _('Journal Enteries'),
            'domain': [('id', 'in', self.journal_item.ids)],
            'view_type': 'form',
            'res_model': 'account.move',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    journal_counter = fields.Integer(string='Journal Enteries', compute='get_journal_enteries')

    def get_journal_enteries(self):
        for rec in self:
            count = self.env['account.move'].search_count([('id', 'in', self.journal_item.ids)])
            rec.journal_counter = count


class CashJournalLines(models.Model):
    _name = "cash.lines"
    _description = "Cash Journal Lines"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    account_id = fields.Many2one('account.account', String="Account")
    analytical_account_id = fields.Many2one('account.analytic.account', string="Analytical Account",
                                            track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string="Partner", tracking=True)
    description = fields.Char(string='Description')
    cheque_no = fields.Char(string='Cheque No#')
    amount = fields.Float(string='Amount')
    date = fields.Date(string='Date')

    cash_journal_id = fields.Many2one('cash.journal')
