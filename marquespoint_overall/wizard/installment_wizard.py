from odoo import fields, models, api, _
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning, UserError, ValidationError


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
    is_token_money = fields.Boolean('Token Money Included')
    is_admin = fields.Boolean()
    is_admin_fee = fields.Boolean('DLD+Admin Fee')
    admin_fee = fields.Float('Amount')

    # @api.onchange('is_token_money')
    # def _onchange_token(self):
    #     print(self.is_token_money)
    #     print(self.order_id)
    #     print(self.order_id.account_payment_ids)

    @api.depends('percentage', 'order_id.amount_untaxed', 'milestone_id.amount', 'is_token_money', 'is_admin_fee',
                 'admin_fee')
    def _compute_amount(self):
        if self.is_admin_fee:
            self.amount = self.admin_fee
            self.percentage = 0
        elif self.percentage and self.order_id.amount_untaxed:
            self.amount = self.order_id.amount_untaxed * (self.percentage / 100.0)
            if self.is_token_money:
                if temp := sum(
                        payment.amount
                        for payment in self.order_id.account_payment_ids
                        if payment.state == 'post'
                ):
                    self.amount -= temp
                    product_unit = self.env['product.template'].search(
                        [('name', '=', self.order_id.partner_id.name)])
                    product_unit.state = 'reserved'
        elif self.percentage and self.milestone_id.amount:
            self.amount = self.milestone_id.amount * (self.percentage / 100.0)
            if self.is_token_money:
                if temp := sum(
                        payment.amount
                        for payment in self.order_id.account_payment_ids
                        if payment.state == 'post'
                ):
                    self.amount -= temp
                    product_unit = self.env['product.product'].search(
                        [('name', '=', self.order_id.partner_id.name)])
                    product_unit.state = 'reserved'
        else:
            self.amount = 0

    @api.depends('installment_period', 'start_date', 'end_date')
    def _compute_installment_no(self):
        delta = relativedelta(self.end_date, self.start_date)
        res_months = delta.months + (delta.years * 12)
        res_quarters = res_months // 3
        res_years = delta.years
        if self.installment_period == 'annual':
            self.installment_no = res_years + 1
        elif self.installment_period == 'quarterly':
            self.installment_no = res_quarters + 1
        elif self.installment_period == 'month':
            self.installment_no = res_months + 1
        else:
            self.installment_no = 0

    def create_installments(self):
        if self.amount == 0 or self.installment_no == 0:
            raise UserError('Amount or Installment No are Missing')
        if self.percentage < 0:
            raise ValidationError('Please Enter Positive value for Percentage')
        model = self.env.context.get('active_model')
        active_id = self.env[model].browse(self.env.context.get('active_id'))
        self.env['installment.line'].search(
            [('milestone_id', '=', self.milestone_id.id), ('order_id', '=', self.order_id.id)]).unlink()
        active_id.write({
            'amount': self.amount,
            'percentage': self.percentage,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'installment_no': self.installment_no,
            'installment_period': self.installment_period,
            'is_admin_fee': self.is_admin_fee,
        })
        # Validations
        if active_id.order_id.plan_ids:
            total_percentage = sum(percen.percentage for percen in active_id.order_id.plan_ids)
            total_amount = sum(line.amount for line in active_id.order_id.plan_ids if not line.is_admin_fee)
            print(f'total_percentage: {total_percentage}')
            print(f'total_amount: {total_amount}')
            print(f'self.order_id.amount_untaxed: {active_id.order_id.amount_untaxed}')
            remaining_percentage = 100 - (total_percentage - self.percentage)
            if total_amount > active_id.order_id.amount_untaxed:
                raise ValidationError('The amount is Exceeding the sale order')
            if total_percentage > 100:
                raise ValidationError(
                    f'Capacity: 100%\nFilled: {total_percentage - self.percentage}% \nRemaining: {remaining_percentage}%')
        #     End validations
        # amount = self.amount / self.installment_no
        for _ in range(self.installment_no):
            inv_date = self.start_date
            if self.installment_period == 'month':
                inv_date += relativedelta(months=_)
                print(f'inv date: {inv_date}')
            elif self.installment_period == 'quarterly':
                inv_date += relativedelta(months=_ * 3)
            elif self.installment_period == 'annual':
                inv_date += relativedelta(months=_ * 12)
            vals = {
                'milestone_id': self.milestone_id.id,
                # 'amount': amount,
                'order_id': self.order_id.id,
                'date': inv_date
            }
            self.env['installment.line'].create(vals)
        print('installment created')

    @api.constrains('is_token_money')
    def _is_token_money(self):
        if self.is_token_money:
            temp = sum(
                payment.amount for payment in self.order_id.account_payment_ids if payment.state == 'post')
            if not temp:
                raise UserError('Please Create a Token Money for Adjustment')
