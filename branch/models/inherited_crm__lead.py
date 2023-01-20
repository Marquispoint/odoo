from odoo import fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def _default_branch_id(self):
        branch_id = self.env['res.users'].browse(self._uid).branch_id.id
        return branch_id

    branch_id = fields.Many2one('res.branch', default=_default_branch_id)
