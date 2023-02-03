# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _prepare_invoice_values(self, order, name, amount, so_line):
        invoice_vals = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(order, name, amount, so_line)
        invoice_vals.update({
            'branch_id': order.branch_id.id,
            'project': order.project.id,
            'building': order.building.id,
            'floor': order.floor.id,
            'unit': order.unit.id,
        })
        return invoice_vals
