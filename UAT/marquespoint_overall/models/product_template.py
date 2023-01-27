# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    status = fields.Selection([
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('booked', 'Booked'),
        ('sold', 'Sold'),
        ('cancel', 'Cancel'),
    ], default='available')

    is_unit = fields.Boolean('Is Unit')
    project = fields.Many2one('project.project', 'Project')
    unit_id = fields.Many2one('product.product', 'Unit')
    multi_image = fields.Many2many('ir.attachment', string="Image")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        print(vals)
        if vals.get('project'):
            self.product_tmpl_id.project = vals['project']
        if vals.get('branch_id'):
            self.product_tmpl_id.branch_id = vals['branch_id']
        self.product_tmpl_id.unit_id = self.id
        return res

    @api.model
    def create(self, vals):
        print(f'create: {vals}')
        res = super(ProductProduct, self).create(vals)
        print(res.product_tmpl_id)
        if res.product_tmpl_id:
            res.product_tmpl_id.project = res.project.id
            res.product_tmpl_id.branch_id = res.branch_id.id
            res.product_tmpl_id.unit_id = res.id
            res.product_tmpl_id.is_unit = True
        return res

    def _prepare_variant_values(self, combination):
        print('_prepare_variant_values')
        variant_dict = super()._prepare_variant_values(combination)
        variant_dict['project'] = self.project.id
        variant_dict['branch_id'] = self.branch_id.id
        variant_dict['unit_id'] = self.id
        variant_dict['is_unit'] = True
        return variant_dict
