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
        if 'project' in vals:
            self.product_tmpl_id.project = vals['project']
        self.product_tmpl_id.unit_id = self.id
        return res

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        print(res.product_tmpl_id)
        if res.product_tmpl_id:
            res.product_tmpl_id.project = res.project.id
            res.product_tmpl_id.unit_id = res.id
        return res
    def _prepare_variant_values(self, combination):
        print('_prepare_variant_values')
        variant_dict = super()._prepare_variant_values(combination)
        variant_dict['project'] = self.project.id
        variant_dict['unit_id'] = self.id
        return variant_dict
