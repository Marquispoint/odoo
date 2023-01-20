from odoo import models, fields, api


class PropertyBuilding(models.Model):
    _inherit = 'property.building'

    branch_id = fields.Many2one(related='project_id.branch_id', string='Branch')
    # def _default_branch_id(self):
    #     branch_id = self.env['res.users'].browse(self._uid).branch_id.id
    #     return branch_id

    # branch_id = fields.Many2one('res.branch')
    #
    # @api.onchange('project_id')
    # def _onchange_project_id(self):
    #     for rec in self:
    #         if rec.project_id:
    #             rec.branch_id = rec.project_id.branch_id.id


class PropertyFloor(models.Model):
    _inherit = 'property.floor'

    branch_id = fields.Many2one(related='building_id.branch_id', string='Branch')
    # def _default_branch_id(self):
    #     branch_id = self.env['res.users'].browse(self._uid).branch_id.id
    #     return branch_id
    # branch_id = fields.Many2one('res.branch')
    # @api.onchange('building_id')
    # def _on_building_id_change(self):
    #     for rec in self:
    #         if rec.building_id:
    #             rec.branch_id = rec.building_id.branch_id.id
