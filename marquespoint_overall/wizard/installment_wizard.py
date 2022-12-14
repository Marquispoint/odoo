from odoo import fields, models, _, api
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning, UserError


class InstallmentWizard(models.TransientModel):
    _name = 'installment.wizard'
    _description = 'Installment Wizard'

    milestone_id = fields.Many2one('payment.plan', string='Milestone')
    is_booked = fields.Boolean()
    percentage = fields.Float('Percentage')
    amount = fields.Float('Amount', compute='_compute_amount')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    installment_period = fields.Selection([
        ('month', 'Month'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual')
    ], 'Installment Period')
    installment_no = fields.Integer('Installment No', compute='_compute_installment_no')
    order_id = fields.Many2one('sale.order')
    is_token_money = fields.Boolean('Is Token Money')

    # @api.onchange('is_token_money')
    # def _onchange_token(self):
    #     print(self.is_token_money)
    #     print(self.order_id)
    #     print(self.order_id.account_payment_ids)

    @api.depends('percentage', 'order_id.amount_untaxed', 'milestone_id.amount', 'is_token_money')
    def _compute_amount(self):
        if self.percentage:
            if self.order_id.amount_untaxed:
                self.amount = self.order_id.amount_untaxed * (self.percentage / 100.0)
                if self.is_token_money:
                    temp = sum(
                        payment.amount for payment in self.order_id.account_payment_ids if payment.state == 'post')
                    if temp:
                        self.amount -= temp
                        product_template = self.env['product.template'].search(
                            [('name', '=', self.order_id.partner_id.name)])
                        product_template.status = 'reserved'
            elif self.milestone_id.amount:
                self.amount = self.milestone_id.amount * (self.percentage / 100.0)
                if self.is_token_money:
                    temp = sum(
                        payment.amount for payment in self.order_id.account_payment_ids if payment.state == 'post')
                    if temp:
                        self.amount -= temp
                        product_template = self.env['product.template'].search(
                            [('name', '=', self.order_id.partner_id.name)])
                        product_template.status = 'reserved'
            else:
                self.amount = 0
        else:
            self.amount = 0

    @api.depends('installment_period', 'start_date', 'end_date')
    def _compute_installment_no(self):
        delta = relativedelta(self.end_date, self.start_date)
        res_months = delta.months + (delta.years * 12)
        res_quarters = res_months // 3
        res_years = delta.years
        if self.installment_period == 'annual':
            self.installment_no = res_years
        elif self.installment_period == 'quarterly':
            self.installment_no = res_quarters
        elif self.installment_period == 'month':
            self.installment_no = res_months
        else:
            self.installment_no = 0

    def create_installments(self):
        if self.amount == 0 or self.installment_no == 0:
            raise UserError('Amount or Installment No are Missing')
        model = self.env.context.get('active_model')
        active_id = self.env[model].browse(self.env.context.get('active_id'))
        self.env['installment.line'].search([('milestone_id', '=', self.milestone_id.id)]).unlink()
        active_id.write({
            'amount': self.amount,
            'percentage': self.percentage,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'installment_no': self.installment_no,
            'installment_period': self.installment_period,
        })
        dt = self.start_date
        amount = self.amount / self.installment_no
        for rec in range(self.installment_no):
            invoice = False
            if self.order_id.order_line:
                inv_lines = []
                for line in self.order_id.order_line:
                    inv_lines.append((0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'quantity': line.product_uom_qty,
                        'product_uom_id': line.product_uom.id,
                        'price_unit': amount,
                        'tax_ids': line.tax_id,
                    }))
                inv_vals = {
                    'partner_id': self.order_id.partner_id.id,
                    'invoice_date': date.today(),
                    'invoice_line_ids': inv_lines,
                    'move_type': 'out_invoice',
                    'so_ids': self.order_id.id,
                    'state': 'draft',
                    'project': self.order_id.project.id,
                    'building': self.order_id.building.id,
                    'floor': self.order_id.floor.id,
                    'unit': self.order_id.unit.id,
                }
                invoice = self.env['account.move'].create(inv_vals)
            vals = {
                'milestone_id': self.milestone_id.id,
                'amount': amount,
                'order_id': self.order_id.id,
                'move_id': invoice.id
            }
            self.env['installment.line'].create(vals)
            dt = dt + relativedelta(months=1)
        print('installment created')

    @api.constrains('is_token_money')
    def _is_token_money(self):
        if self.is_token_money:
            temp = sum(
                payment.amount for payment in self.order_id.account_payment_ids if payment.state == 'post')
            if not temp:
                raise UserError('Please Create a Token Money for Adjustment')
