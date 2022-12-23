from odoo import fields, models, api
from odoo.tools import float_compare
from datetime import datetime, date


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    account_payment_ids = fields.One2many(
        "account.payment", "order_id", string="Pay purchase advanced", readonly=True
    )
    amount_residual = fields.Float(
        "Residual amount",
        readonly=True,
        compute="_compute_sale_advance_payment",
        store=True,
    )
    payment_line_ids = fields.Many2many(
        "account.move.line",
        string="Payment move lines",
        compute="_compute_sale_advance_payment",
        store=True,
    )
    advance_payment_status = fields.Selection(
        selection=[
            ("not_paid", "Not Paid"),
            ("paid", "Paid"),
            ("partial", "Partially Paid"),
        ],
        store=True,
        readonly=True,
        copy=False,
        tracking=True,
        compute="_compute_sale_advance_payment",
    )

    @api.depends(
        "currency_id",
        "company_id",
        "amount_total",
        "account_payment_ids",
        "account_payment_ids.state",
        "account_payment_ids.move_id",
        "account_payment_ids.move_id.line_ids",
        "account_payment_ids.move_id.line_ids.date",
        "account_payment_ids.move_id.line_ids.debit",
        "account_payment_ids.move_id.line_ids.credit",
        "account_payment_ids.move_id.line_ids.currency_id",
        "account_payment_ids.move_id.line_ids.amount_currency",
        "order_line.invoice_lines.move_id",
        "order_line.invoice_lines.move_id.amount_total",
        "order_line.invoice_lines.move_id.amount_residual",
    )
    def _compute_sale_advance_payment(self):
        for order in self:
            mls = order.account_payment_ids.mapped("move_id.line_ids").filtered(
                lambda x: x.account_id.internal_type == "receivable"
                          and x.parent_state == "posted"
            )
            advance_amount = 0.0
            for line in mls:
                line_currency = line.currency_id or line.company_id.currency_id
                # Exclude reconciled pre-payments amount because once reconciled
                # the pre-payment will reduce bill residual amount like any
                # other payment.
                line_amount = (
                    line.amount_residual_currency
                    if line.currency_id
                    else line.amount_residual
                )
                if line_currency != order.currency_id:
                    advance_amount += line.currency_id._convert(
                        line_amount,
                        order.currency_id,
                        order.company_id,
                        line.date or fields.Date.today(),
                    )
                else:
                    advance_amount += line_amount
            # Consider payments in related invoices.
            invoice_paid_amount = 0.0
            for inv in order.invoice_ids:
                invoice_paid_amount += inv.amount_total - inv.amount_residual
            print(f'invoice_paid_amount: {invoice_paid_amount}')
            print(f'advance_amount: {advance_amount}')
            amount_residual = order.amount_total + advance_amount - invoice_paid_amount
            payment_state = "not_paid"
            if mls or order.invoice_ids:
                has_due_amount = float_compare(
                    amount_residual, 0.0, precision_rounding=order.currency_id.rounding
                )
                if has_due_amount <= 0:
                    payment_state = "paid"
                elif has_due_amount > 0:
                    payment_state = "partial"
            order.payment_line_ids = mls
            order.amount_residual = amount_residual
            order.advance_payment_status = payment_state

    # ------------------------------------------------------------------
    plan_ids = fields.One2many('payment.plan.line', 'order_id')
    installment_ids = fields.One2many('installment.line', 'order_id')
    ins_amount = fields.Float('Total', compute='_compute_installment_amount')

    def _compute_installment_amount(self):
        for rec in self:
            records = self.env['installment.line'].search([('order_id', '=', rec.id)])
            amount = sum(line.amount for line in records)
            rec.ins_amount = amount

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        product_template = self.env['product.template'].search([('name', '=', self.partner_id.name)])
        if product_template:
            product_template.status = 'available'
        return res

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        product_template = self.env['product.template'].search([('name', '=', self.partner_id.name)])
        if product_template:
            product_template.status = 'sold'
        return res

    def token_money_scheduler(self):
        today_date = date.today()
        print(today_date)
        print('outside')
        print(self.account_payment_ids)
        print(self.id)
        sale_orders = self.env['sale.order'].search([])
        print(sale_orders)
        for rec in sale_orders:
            print('token money scheduler')
            if rec.account_payment_ids:
                print(rec.account_payment_ids)
                for payment in rec.account_payment_ids:
                    print(payment)
                    if payment.state == 'draft':
                        print('Draft')
                        print(payment.due_date)
                        print(today_date)
                        print(self.env['product.template'].search(
                            [('name', '=', rec.partner_id.name)]))
                        if payment.due_date == today_date:
                            product_template = self.env['product.template'].search(
                                [('name', '=', rec.partner_id.name)])
                            if product_template:
                                product_template.status = 'available'
                                payment.state = 'cancel'


class PaymentPlanLines(models.Model):
    _name = 'payment.plan.line'
    milestone_id = fields.Many2one('payment.plan', string='Milestone')
    order_id = fields.Many2one('sale.order')
    # percentage = fields.Float('Percentage', compute='_compute_percentage')
    percentage = fields.Float('Percentage')
    # amount = fields.Float('Amount', compute='_compute_amount')
    amount = fields.Float('Amount')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    installment_no = fields.Integer('Installment No')
    installment_period = fields.Char('Installment Period')

    def _compute_percentage(self):
        for rec in self:
            rec.percentage = rec.milestone_id.percentage if rec.milestone_id else 0

    def _compute_amount(self):
        for rec in self:
            if rec.order_id.amount_untaxed:
                rec.amount = rec.order_id.amount_untaxed
            elif rec.milestone_id.amount:
                rec.amount = rec.milestone_id.amount
            else:
                rec.amount = 0

    def open_payment_plan_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Insurance Bills',
            'view_id': self.env.ref('marquespoint_overall.view_installment_wizard_form', False).id,
            'context': {
                'default_milestone_id': self.milestone_id.id,
                'default_is_booked': self.milestone_id.is_booked,
                'default_is_admin': self.milestone_id.is_admin_fee,
                'default_order_id': self.order_id.id,
                'default_percentage': self.milestone_id.percentage,
                # 'default_amount': self.order_id.amount_untaxed if self.order_id.amount_untaxed else self.milestone_id.amount,
            },
            'target': 'new',
            'res_model': 'installment.wizard',
            'view_mode': 'form',
        }

    def unlink(self):
        for rec in self:
            self.env['installment.line'].search([('milestone_id', '=', rec.milestone_id.id)]).unlink()
        return super(PaymentPlanLines, self).unlink()


class InstallmentLines(models.Model):
    _name = 'installment.line'

    milestone_id = fields.Many2one('payment.plan', string='Milestone')
    amount = fields.Float('Amount')
    move_id = fields.Many2one('account.move', string='Invoice')
    invoice_date = fields.Date('Inv Date', related='move_id.invoice_date')
    invoice_payment_date = fields.Date('Payment Due Date')
    invoice_status = fields.Selection(related='move_id.state', string='Inv Status')
    payment_status = fields.Selection(related='move_id.payment_state', string='Payment Status')
    order_id = fields.Many2one('sale.order')

    def unlink(self):
        if self.move_id:
            self.move_id.unlink()
        return super(InstallmentLines, self).unlink()
