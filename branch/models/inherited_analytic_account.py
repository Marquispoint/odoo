from odoo import api, fields, models


class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    branch_id = fields.Many2one('res.branch', string='Branch')


class AccountAnalyticTag(models.Model):
    _inherit = 'account.analytic.tag'

    branch_id = fields.Many2one('res.branch', string='Branch')
