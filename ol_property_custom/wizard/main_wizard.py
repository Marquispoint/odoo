import datetime
from re import U

from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import requests
import datetime


class CreateBuildingWizard(models.TransientModel):
    _name = "create.building.wizard"

    no_of_building = fields.Integer("No of Buildings")

    def create_building(self):
        active_id = self._context.get('active_id')
        no = self._context['no_of_build']
        obj = self.env['property.building'].search([('project_id', '=', active_id)])
        obj_project = self.env['project.project'].search([('id', '=', active_id)])
        for i in range(no):
            if obj:
                idd = self.env['account.analytic.account'].create({
                    'name': obj_project.code + "-" + f'{len(obj.ids) + 1 + i:02}'
                })
                sid = self.env['property.building'].create({
                    'project_id': active_id,
                    'code': obj_project.code + "-" + f'{len(obj.ids) + 1 + i:02}',
                    'building_account_analytical': idd.id,
                    'branch_id': obj_project.branch_id.id,
                })
                s = self.env['account.analytic.account'].search(
                    [('name', '=', obj_project.code + "-" + f'{len(obj.ids) + 1 + i:02}')])
                s.write({
                    'building_id': sid.id
                })

            else:
                idd = self.env['account.analytic.account'].create({
                    'name': obj_project.code + "-" + f'{i + 1:02}'

                })
                sid = self.env['property.building'].create({
                    'project_id': active_id,
                    'code': obj_project.code + "-" + f'{i + 1:02}',
                    'building_account_analytical': idd.id,
                    'branch_id': obj_project.branch_id.id,
                })
                s = self.env['account.analytic.account'].search([('name', '=', obj_project.code + "-" + f'{i + 1:02}')])
                s.write({
                    'building_id': sid.id
                })


# create floor
class CreatFloor(models.TransientModel):
    _name = "create.floor.wizard"

    no_of_floor = fields.Integer("No of Floors")

    def create_floor(self):
        active_id = self._context.get('active_id')
        no = self._context['floor']
        model = self.env.context.get('active_model')
        # obj = self.env[model].browse(self.env.context.get('active_id'))
        obj = self.env['property.floor'].search([('building_id.id', '=', active_id)])
        obj_project = self.env['property.building'].search([('id', '=', active_id)])
        for i in range(no):
            if obj:
                idd = self.env['account.analytic.account'].create({
                    'name': obj_project.code + "-" + f'{len(obj.ids) + 1 + i:02}'

                })
                sid = self.env['property.floor'].create({
                    'building_id': active_id,
                    'code': obj_project.code + "-" + f'{len(obj.ids) + 1 + i:02}',
                    'floor_analytic_account': idd.id,
                    'branch_id': obj_project.branch_id.id,
                })
                s = self.env['account.analytic.account'].search(
                    [('name', '=', obj_project.code + "-" + f'{len(obj.ids) + 1 + i:02}')])
                s.write({
                    'floor_id': sid.id
                })
            else:
                print('Create floor else part runn')

                idd = self.env['account.analytic.account'].create({
                    'name': obj_project.code + "-" + f'{i + 1:02}'
                })
                sid = self.env['property.floor'].create({
                    'building_id': active_id,
                    'code': obj_project.code + "-" + f'{i + 1:02}',
                    'floor_analytic_account': idd.id,
                    'branch_id': obj_project.branch_id.id,
                })
                s = self.env['account.analytic.account'].search([('name', '=', obj_project.code + "-" + f'{i + 1:02}')])
                s.write({
                    'floor_id': sid.id
                })


# create units
class CreateUnits(models.TransientModel):
    _name = "create.units.wizard"

    no_of_unit = fields.Integer("No of Units")

    def create_units(self):
        active_id = self._context.get('active_id')
        no = self._context['units']
        obj = self.env['product.product'].search([('floor_id.id', '=', active_id)])
        obj_project = self.env['property.floor'].search([('id', '=', active_id)])

        for i in range(no):
            if obj:
                idd = self.env['account.analytic.account'].create({
                    'name': obj_project.code + "-" + f'{len(obj.ids) + 1 + i:02}',
                })
                sid = self.env['product.product'].create({
                    'name': obj_project.code + "-" + f'{len(obj.ids) + 1 + i:02}',
                    'floor_id': active_id,
                    'building':obj_project.building_id.id,
                    'project':obj_project.project_name.id,
                    'units_analytic_account': idd.id,
                    'branch_id': obj_project.branch_id.id,
                })
                print(f'sid: {sid}')
                sidd = self.env['res.partner'].create({
                    'name': obj_project.code + "-" + f'{len(obj.ids) + 1 + i:02}',
                    'is_unit': True,
                })
                s = self.env['account.analytic.account'].search(
                    [('name', '=', obj_project.code + "-" + f'{len(obj.ids) + 1 + i:02}')])
                s.write({
                    'unit_id': sid.id
                })
            else:
                idd = self.env['account.analytic.account'].create({
                    'name': obj_project.code + "-" + f'{i + 1:02}'

                })
                sid = self.env['product.product'].create({
                    'name': obj_project.code + "-" + f'{i + 1:02}',
                    'floor_id': active_id,
                    'units_analytic_account': idd.id,
                    'building': obj_project.building_id.id,
                    'project': obj_project.project_name.id,
                    'branch_id': obj_project.branch_id.id,
                })
                sidd = self.env['res.partner'].create({
                    'name': obj_project.code + "-" + f'{i + 1:02}',
                    'is_unit': True,
                })
                s = self.env['account.analytic.account'].search([('name', '=', obj_project.code + "-" + f'{i + 1:02}')])
                s.write({
                    'unit_id': sid.id
                })
