from odoo import fields, models


class ProductTemplateIn(models.Model):
    _inherit = 'product.template'

    def _default_branch_id(self):
        branch_id = self.env['res.users'].browse(self._uid).branch_id.ids
        return branch_id

    branch_id = fields.Many2one('res.branch', default=_default_branch_id)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _default_branch_id(self):
        branch_id = self.env['res.users'].browse(self._uid).branch_id.ids
        return branch_id

    branch_id = fields.Many2one('res.branch', default=_default_branch_id)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    def _default_branch_id(self):
        branch_id = self.env['res.users'].browse(self._uid).branch_id.ids
        return branch_id

    branch_id = fields.Many2one('res.branch', default=_default_branch_id)