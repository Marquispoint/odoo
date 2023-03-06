# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order.line'

    def _default_branch_id(self):
        branch_id = self.env['res.users'].browse(self._uid).branch_id.id
        return branch_id

    branch_id = fields.Many2one('res.branch', related='order_id.branch_id', default=_default_branch_id)

    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            for val in line._prepare_stock_moves(picking):
                val.update({
                    'branch_id': line.branch_id.id,
                })

                done += moves.create(val)
        return done


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _default_branch_id(self):
        branch_id = self.env['res.users'].browse(self._uid).branch_id.id
        return branch_id

    branch_id = fields.Many2one('res.branch', default=_default_branch_id)

    @api.onchange('branch_id')
    def _onchange_branch_id_tag_change(self):
        print('on_branch_change')
        for line in self.order_line:
            # line.account_analytic_id = self.branch_id.analytic_account_id.id
            line.analytic_tag_ids = self.branch_id.analytic_tag_id
