

from odoo.exceptions import Warning
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    review_by_id = fields.Many2one('res.users', string='Reviewed By')
    approve_by_id = fields.Many2one('res.users', string='Approved By')

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to_review', 'Waiting For Review'),
        ('approve', 'Waiting For Approval'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('rejected', 'Rejected'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    def button_confirm(self):
        self.write({
            'state': 'to_review'
        })

    def button_review(self):
        if self.env.user.has_group('manager_all_approvals.group_review_purchase_order'):
            self.review_by_id = self.env.user.id
        self.write({
            'state': 'approve'
        })

    def action_reset(self):
        self.write({
            'state': 'draft'
        })

    def button_approved(self):
        if self.env.user.has_group('manager_all_approvals.group_approve_purchase_order'):
            self.approve_by_id = self.env.user.id
        for order in self:
            if order.state not in ['draft', 'sent', 'approve']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step' \
                    or (order.company_id.po_double_validation == 'two_step' \
                        and order.amount_total < self.env.company.currency_id._convert(
                        order.company_id.po_double_validation_amount, order.currency_id, order.company_id,
                        order.date_order or fields.Date.today())) \
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True

    def button_reject(self):
        self.write({
            'state': 'rejected'
        })

    def button_approve_reject(self):
        self.write({
            'state': 'rejected'
        })


class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    review_by_id = fields.Many2one('res.users', string='Reviewed By')
    approve_by_id = fields.Many2one('res.users', string='Approved By')

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('to_review', 'Waiting For Review'),
        ('approve', 'Waiting For Approval'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('rejected', 'Rejected'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    def action_confirm(self):
        self.write({
            'state': 'to_review'
        })

    def button_review(self):
        if self.env.user.has_group('manager_all_approvals.group_review_sale_order'):
            self.review_by_id = self.env.user.id
        self.write({
            'state': 'approve'
        })

    def action_reset(self):
        self.write({
            'state': 'draft'
        })

    def button_approved(self):
        if self.env.user.has_group('manager_all_approvals.group_approve_sale_order'):
            self.approve_by_id = self.env.user.id
        self.write({
            'state': 'sent'
        })

    def button_reject(self):
        self.write({
            'state': 'rejected'
        })

    def button_approve_reject(self):
        self.write({
            'state': 'rejected'
        })

    def button_client_approve(self):
        rec = super(SaleOrderInh, self).action_confirm()
        return rec

    def button_client_reset(self):
        self.write({
            'state': 'draft'
        })


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    review_by_id = fields.Many2one('res.users', string='Reviewed By')
    approve_by_id = fields.Many2one('res.users', string='Approved By')

    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('to_review', 'Waiting For Review'),
        ('approve', 'Waiting For Approval'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
        ('rejected', 'Rejected'),
    ], string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft')

    def action_post(self):
        self.write({
            'state': 'to_review'
        })

    def button_review(self):
        if self.env.user.has_group('manager_all_approvals.group_review_invoice_bill'):
            self.review_by_id = self.env.user.id
        self.write({
            'state': 'approve'
        })

    def action_reset(self):
        self.write({
            'state': 'draft'
        })

    def button_approved(self):
        if self.env.user.has_group('manager_all_approvals.group_approve_invoice_bill'):
            self.approve_by_id = self.env.user.id
        rec = super(AccountMoveInh, self).action_post()
        return rec

    def button_reject(self):
        self.write({
            'state': 'rejected'
        })

    def button_approve_reject(self):
        self.write({
            'state': 'rejected'
        })


class AccountPaymentInh(models.Model):
    _inherit = 'account.payment'

    review_by_id = fields.Many2one('res.users', string='Reviewed By')
    approve_by_id = fields.Many2one('res.users', string='Approved By')

    # state = fields.Selection([('draft', 'Draft'),
    #                           ('approve', 'Waiting For Approval'),
    #                           ('posted', 'Validated'),
    #                           ('sent', 'Sent'),
    #                           ('reconciled', 'Reconciled'),
    #                           ('cancelled', 'Cancelled'),
    #                           ('reject', 'Reject')
    #                           ], readonly=True, default='draft', copy=False, string="Status")

    def action_post(self):
        self.write({
            'state': 'to_review'
        })

    def button_review(self):
        if self.env.user.has_group('manager_all_approvals.group_review_payment'):
            self.review_by_id = self.env.user.id
        self.write({
            'state': 'approve'
        })

    def action_reset(self):
        self.write({
            'state': 'draft'
        })

    def button_approved(self):
        if self.env.user.has_group('manager_all_approvals.group_approve_payment'):
            self.approve_by_id = self.env.user.id
        rec = super(AccountPaymentInh, self).action_post()
        return rec

    def button_reject(self):
        self.write({
            'state': 'rejected'
        })

    def button_approve_reject(self):
        self.write({
            'state': 'rejected'
        })
