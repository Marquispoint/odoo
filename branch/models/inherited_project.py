from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    def _default_branch_id(self):
        branch_id = self.env['res.users'].browse(self._uid).branch_id.id
        return branch_id

    branch_id = fields.Many2one('res.branch', default=_default_branch_id)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    branch_id = fields.Many2one(related="project_id.branch_id")