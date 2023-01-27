from odoo import fields, models, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _default_branch_id(self):
        branch_id = self.env['res.users'].browse(self._uid).branch_id.id
        return branch_id

    branch_id = fields.Many2one('res.branch', default=_default_branch_id)

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        for rec in self:
            print(rec.branch_id.analytic_tag_id)
            records = self.env['account.journal'].search(
                [('is_multi_branch', '=', False), ('id', '=', rec.journal_id.id)])
            if records:
                if rec.branch_id:
                    for invoice in rec.invoice_line_ids:
                        invoice.branch_id = rec.branch_id.id
                        invoice.analytic_account_id = rec.branch_id.analytic_account_id.id
                        invoice.analytic_tag_ids = rec.branch_id.analytic_tag_id
                    for line in rec.line_ids:
                        line.branch_id = rec.branch_id.id
                        line.analytic_account_id = rec.branch_id.analytic_account_id.id
                        line.analytic_tag_ids = rec.branch_id.analytic_tag_id
                else:
                    for invoice in rec.invoice_line_ids:
                        invoice.branch_id = False
                        invoice.analytic_account_id = False
                        invoice.analytic_tag_ids = False
                    for line in rec.line_ids:
                        line.branch_id = False
                        line.analytic_account_id = False
                        line.analytic_tag_ids = False
            else:
                for invoice in rec.invoice_line_ids:
                    if not invoice.branch_id:
                        invoice.branch_id = rec.branch_id.id
                        invoice.analytic_account_id = rec.branch_id.analytic_account_id.id
                        invoice.analytic_tag_ids = rec.branch_id.analytic_tag_id
                for line in rec.line_ids:
                    if not line.branch_id:
                        line.branch_id = rec.branch_id.id
                        line.analytic_account_id = rec.branch_id.analytic_account_id.id
                        line.analytic_tag_ids = rec.branch_id.analytic_tag_id

    @api.model
    def create(self, values):
        res = super(AccountMove, self).create(values)
        records = self.env['account.journal'].search(
            [('is_multi_branch', '=', False), ('id', '=', res.journal_id.id)])
        if records:
            for line in res.invoice_line_ids:
                line.branch_id = res.branch_id
                line.analytic_account_id = res.branch_id.analytic_account_id.id
                line.analytic_tag_ids = res.branch_id.analytic_tag_id

            for line in res.line_ids:
                line.branch_id = res.branch_id
                line.analytic_account_id = res.branch_id.analytic_account_id.id
                line.analytic_tag_ids = res.branch_id.analytic_tag_id
        else:
            print("else create called")
            for line in res.invoice_line_ids:
                if not res.branch_id:
                    line.branch_id = res.branch_id
                    line.analytic_account_id = res.branch_id.analytic_account_id.id
                    line.analytic_tag_ids = res.branch_id.analytic_tag_id
            for line in res.line_ids:
                if not line.branch_id:
                    line.branch_id = res.branch_id.id
                    line.analytic_account_id = res.branch_id.analytic_account_id.id
                    line.analytic_tag_ids = res.branch_id.analytic_tag_id
        return res

    def write(self, values):
        res = super(AccountMove, self).write(values)
        records = self.env['account.journal'].search(
            [('is_multi_branch', '=', False), ('id', '=', self.journal_id.id)])
        if records:
            for line in self.invoice_line_ids:
                line.branch_id = self.branch_id.id
                line.analytic_account_id = self.branch_id.analytic_account_id.id
                line.analytic_tag_ids = self.branch_id.analytic_tag_id
            for line in self.line_ids:
                line.branch_id = self.branch_id.id
                line.analytic_account_id = self.branch_id.analytic_account_id.id
                line.analytic_tag_ids = self.branch_id.analytic_tag_id
        else:
            for line in self.invoice_line_ids:
                if not line.branch_id:
                    line.branch_id = self.branch_id.id
                    line.analytic_account_id = self.branch_id.analytic_account_id.id
                    line.analytic_tag_ids = self.branch_id.analytic_tag_id
            for line in self.line_ids:
                if not line.branch_id:
                    line.branch_id = self.branch_id.id
                    line.analytic_account_id = self.branch_id.analytic_account_id.id
                    line.analytic_tag_ids = self.branch_id.analytic_tag_id
        return res

    def action_register_payment(self):
        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.ids,
                'default_branch_id': self.branch_id.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _default_branch_id(self):
        branch_id = self.env['res.users'].browse(self._uid).branch_id.id
        return branch_id

    branch_id = fields.Many2one('res.branch', default=_default_branch_id)
    is_multi_branch = fields.Boolean(related='move_id.journal_id.is_multi_branch')

    @api.onchange('branch_id')
    def _on_branch_id_change(self):
        print('inside onchange')
        for rec in self:
            if rec.branch_id:
                print('branch id found')
                rec.analytic_account_id = rec.branch_id.analytic_account_id.id
                rec.analytic_tag_ids = rec.branch_id.analytic_tag_id
            else:
                print('branch id is not found')
                rec.analytic_account_id = False
                rec.analytic_tag_ids = False


class AccountAccountInherited(models.Model):
    _inherit = 'account.journal'
    is_multi_branch = fields.Boolean(string='Multi Branches')
