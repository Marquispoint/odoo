from odoo import fields, models, api, _
from odoo.tools import float_compare
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


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

    def _prepare_invoice(self, ):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'branch_id': self.branch_id.id,
            'project': self.project.id,
            'building': self.building.id,
            'floor': self.floor.id,
            'unit': self.unit.id,
        })
        return invoice_vals




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
        product_unit = self.env['product.product'].search([('name', '=', self.partner_id.name)])
        if product_unit:
            product_unit.state = 'available'
        if self.plan_ids:
            self.plan_ids.unlink()
        return res

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if product_unit := self.env['product.product'].search(
            [('name', '=', self.partner_id.name)]
        ):
            product_unit.state = 'sold'

        for plan in self.plan_ids:
            for installment in self.installment_ids:
                if plan.milestone_id == installment.milestone_id:
                    invoice = None
                    if self.order_line:
                        inv_lines = [
                            (
                                0,
                                0,
                                {
                                    'product_id': line.product_id.id,
                                    'name': line.name,
                                    'quantity': line.product_uom_qty,
                                    'product_uom_id': line.product_uom.id,
                                    'price_unit': installment.amount,
                                    'tax_ids': line.tax_id,
                                    'sale_line_ids': line,
                                },
                            )
                            for line in self.order_line
                        ]
                        inv_vals = {
                            'partner_id': self.partner_id.id,
                            'invoice_date': installment.date,
                            'invoice_line_ids': inv_lines,
                            'move_type': 'out_invoice',
                            'so_ids': self.id,
                            'state': 'draft',
                            'project': self.project.id,
                            'building': self.building.id,
                            'floor': self.floor.id,
                            'invoice_origin': self.name,
                            'unit': self.unit.id,
                        }
                        invoice = self.env['account.move'].create(inv_vals)
                        installment.move_id = invoice.id
        return res

    def token_money_scheduler(self):
        today_date = date.today()
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
                            product_unit = self.env['product.product'].search(
                                [('name', '=', rec.partner_id.name)])
                            if product_unit:
                                product_unit.state = 'available'
                                payment.state = 'cancel'

    def unlink(self):
        for rec in self:
            if rec.plan_ids:
                rec.plan_ids.unlink()
        return super(SaleOrder, self).unlink()

    @api.onchange('order_line')
    def _on_order_line_change(self):
        print('_on_order_line_change')
        for rec in self:
            if rec.amount_untaxed:
                for plan in rec.plan_ids:
                    if plan.percentage:
                        plan.amount = rec.amount_untaxed * (plan.percentage / 100.0)

    #     These functions are used for sale quote report
    def get_is_installments_available(self, milestone):
        return any(
            installment.milestone_id == milestone
            for installment in self.installment_ids
        )
#
# # -----------------------------------------
# # This function is used to attach custom reportd in email
#     def _find_mail_template(self, force_confirmation_template=False):
#         self.ensure_one()
#         template_id = False
#         if self.state == 'sale':
#             # template_id = int(self.env['ir.config_parameter'].sudo().get_param('sale.default_confirmation_template'))
#             # template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
#             if not template_id:
#                 template_id = self.env['ir.model.data']._xmlid_to_res_id('marquespoint_overall.mail_template_sale_confirmation', raise_if_not_found=False)
#         if not template_id:
#             template_id = self.env['ir.model.data']._xmlid_to_res_id('marquespoint_overall.email_template_edi_sale', raise_if_not_found=False)
#
#         return template_id
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
    ac_date_eng = fields.Char('Anticipated completion Date (English)', size=60)
    ac_date_arabic = fields.Char('Anticipated completion Date (Arabic)', size=60)

    # def _compute_percentage(self):
    #     for rec in self:
    #         rec.percentage = rec.milestone_id.percentage if rec.milestone_id else 0
    #
    # def _compute_amount(self):
    #     for rec in self:
    #         if rec.order_id.amount_untaxed:
    #             rec.amount = rec.order_id.amount_untaxed
    #         elif rec.milestone_id.amount:
    #             rec.amount = rec.milestone_id.amount
    #         else:
    #             rec.amount = 0

    def open_payment_plan_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Installment Lines',
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
    amount = fields.Float('Amount', compute='_compute_amount')
    move_id = fields.Many2one('account.move', string='Invoice')
    invoice_date = fields.Date('Inv Date', related='move_id.invoice_date')
    invoice_payment_date = fields.Date('Payment Due Date')
    invoice_status = fields.Selection(related='move_id.state', string='Inv Status')
    payment_status = fields.Selection(related='move_id.payment_state', string='Payment Status')
    order_id = fields.Many2one('sale.order')
    date = fields.Date('Installment Date')

    def _compute_amount(self):
        for rec in self:
            if rec.order_id.plan_ids:
                for plan in rec.order_id.plan_ids:
                    if plan.milestone_id == rec.milestone_id:
                        rec.amount = plan.amount / plan.installment_no
                        break
                    else:
                        rec.amount = 0
            else:
                rec.amount = 0

    def unlink(self):
        if self.move_id:
            self.move_id.unlink()
        return super(InstallmentLines, self).unlink()
