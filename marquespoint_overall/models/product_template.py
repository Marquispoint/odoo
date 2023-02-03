# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    state = fields.Selection([
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('booked', 'Booked'),
        ('sold', 'Sold'),
        ('cancel', 'Cancel'),
    ], default='available')

    is_unit = fields.Boolean('Is Unit', default=True)
    project = fields.Many2one('project.project', 'Project')
    multi_image = fields.Many2many('ir.attachment', string="Image")

    #     Property Information
    short_name = fields.Char(string='Short Name')
    code = fields.Char(string='Code', default="New")
    building = fields.Many2one(comodel_name='property.building', string='Building',
                               domain="[('project_id', '=', project)]")
    unit_type = fields.Selection(string='Unit Type', selection=[('parking', 'Parking'), ('appartment', 'Appartment'), ])
    view_type = fields.Selection(string='View Type', selection=[
        ('front', 'Front View'),
        ('rear', 'Rear View'),
        ('road', 'Road View'),
        ('park', 'Park View'),
        ('golf', 'Golf View'),
    ])
    property_name = fields.Char(string='Name')
    category = fields.Selection(string='Category', selection=[('rent', 'Rent'), ('sale', 'Sale'), ])
    property_price = fields.Float(string='Property Price')
    allow_discount = fields.Float(string='Allow Discount')
    reasonable_price = fields.Float(string='Reasonable Price')
    property_owner = fields.Many2one(comodel_name='res.partner', string='Property Owner')
    construction_status = fields.Char(string='Construction Status')
    floor_id = fields.Many2one('property.floor', string='Floor', domain='[("building_id", "=", building)]')
    sale_order = fields.Many2one('sale.order', string='Sale Order')
    project_analytical = fields.Many2one(related="floor_id.building_id.project_id.analytic_account_id",
                                         string="Project Analytic Account")
    building_analytic_account = fields.Many2one(related="floor_id.building_id.building_account_analytical",
                                                string="Building Analytic Account")
    floor_analytic_account = fields.Many2one(related="floor_id.floor_analytic_account",
                                             string="Floor Account Analytical")
    units_analytic_account = fields.Many2one('account.analytic.account', string="Units Account Analytical")
    order = fields.Many2one(related='sale_order.order_line.product_id')
    # New fields
    property_type = fields.Selection([
        ('land', 'Land'),
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
    ], string='Property Type')
    furnishing = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Furnishing')
    build_up_area = fields.Float('Build Up Area')
    carpet_area = fields.Float('Carpet Area')
    bedroom = fields.Float('Bedroom')
    washroom = fields.Float('Washroom')
    balconies = fields.Float('Balconies')

    @api.onchange('property_price')
    def _on_property_price_change(self):
        for rec in self:
            if self.property_price:
                rec.list_price = self.property_price

    @api.model
    def create(self, vals):
        print(f'create: {vals}')
        res = super(ProductTemplate, self).create(vals)
        print(res.product_variant_id)
        if res.product_variant_id:
            res.product_variant_id.branch_id = res.branch_id.id
            res.product_variant_id.state = res.state
            res.product_variant_id.is_unit = res.is_unit
            res.product_variant_id.project = res.project.id
            res.product_variant_id.multi_image = res.multi_image.ids
            res.product_variant_id.short_name = res.short_name
            res.product_variant_id.code = res.code
            res.product_variant_id.building = res.building.id
            res.product_variant_id.unit_type = res.unit_type
            res.product_variant_id.view_type = res.view_type
            res.product_variant_id.property_name = res.property_name
            res.product_variant_id.category = res.category
            res.product_variant_id.property_price = res.property_price
            res.product_variant_id.allow_discount = res.allow_discount
            res.product_variant_id.reasonable_price = res.reasonable_price
            res.product_variant_id.property_owner = res.property_owner.id
            res.product_variant_id.construction_status = res.construction_status
            res.product_variant_id.floor_id = res.floor_id.id
            res.product_variant_id.sale_order = res.sale_order.id
            res.product_variant_id.project_analytical = res.project_analytical.id
            res.product_variant_id.building_analytic_account = res.building_analytic_account.id
            res.product_variant_id.floor_analytic_account = res.floor_analytic_account.id
            res.product_variant_id.units_analytic_account = res.units_analytic_account.id
            res.product_variant_id.order = res.order.id
            res.product_variant_id.property_type = res.property_type
            res.product_variant_id.furnishing = res.furnishing
            res.product_variant_id.build_up_area = res.build_up_area
            res.product_variant_id.carpet_area = res.carpet_area
            res.product_variant_id.bedroom = res.bedroom
            res.product_variant_id.washroom = res.washroom
            res.product_variant_id.balconies = res.balconies

            # res.product_tmpl_id.unit_id = res.id
        return res

    def _prepare_variant_values(self, combination):
        print('_prepare_variant_values')
        variant_dict = super()._prepare_variant_values(combination)
        variant_dict['branch_id'] = self.branch_id.id
        variant_dict['state'] = self.state
        variant_dict['is_unit'] = self.is_unit
        variant_dict['project'] = self.project.id
        variant_dict['multi_image'] = self.multi_image.ids
        variant_dict['short_name'] = self.short_name
        variant_dict['code'] = self.code
        variant_dict['building'] = self.building.id
        variant_dict['unit_type'] = self.unit_type
        variant_dict['view_type'] = self.view_type
        variant_dict['property_name'] = self.property_name
        variant_dict['category'] = self.category
        variant_dict['property_price'] = self.property_price
        variant_dict['allow_discount'] = self.allow_discount
        variant_dict['reasonable_price'] = self.reasonable_price
        variant_dict['property_owner'] = self.property_owner.id
        variant_dict['construction_status'] = self.construction_status
        variant_dict['floor_id'] = self.floor_id.id
        variant_dict['sale_order'] = self.sale_order.id
        variant_dict['project_analytical'] = self.project_analytical.id
        variant_dict['building_analytic_account'] = self.building_analytic_account.id
        variant_dict['floor_analytic_account'] = self.floor_analytic_account.id
        variant_dict['units_analytic_account'] = self.units_analytic_account.id
        variant_dict['order'] = self.order.id
        variant_dict['property_type'] = self.property_type
        variant_dict['furnishing'] = self.furnishing
        variant_dict['build_up_area'] = self.build_up_area
        variant_dict['carpet_area'] = self.carpet_area
        variant_dict['bedroom'] = self.bedroom
        variant_dict['washroom'] = self.washroom
        variant_dict['balconies'] = self.balconies
        # variant_dict['unit_id'] = self.id
        return variant_dict


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_unit = fields.Boolean('Is Unit', default=True)

    @api.onchange('property_price')
    def _on_property_price_change(self):
        print(self.property_price)
        print(self.lst_price)
        for rec in self:
            if self.property_price:
                rec.lst_price = self.property_price

    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        print(vals)
        if vals.get('branch_id'):
            self.product_tmpl_id.branch_id = vals['branch_id']
        if vals.get('state'):
            self.product_tmpl_id.state = vals['state']
        if vals.get('is_unit'):
            self.product_tmpl_id.is_unit = vals['is_unit']
        if vals.get('project'):
            self.product_tmpl_id.project = vals['project']
        if vals.get('multi_image'):
            self.product_tmpl_id.multi_image = vals['multi_image']
        if vals.get('short_name'):
            self.product_tmpl_id.short_name = vals['short_name']
        if vals.get('code'):
            self.product_tmpl_id.code = vals['code']
        if vals.get('building'):
            self.product_tmpl_id.building = vals['building']
        if vals.get('unit_type'):
            self.product_tmpl_id.unit_type = vals['unit_type']
        if vals.get('view_type'):
            self.product_tmpl_id.view_type = vals['view_type']
        if vals.get('property_name'):
            self.product_tmpl_id.property_name = vals['property_name']
        if vals.get('category'):
            self.product_tmpl_id.category = vals['category']
        if vals.get('property_price'):
            self.product_tmpl_id.property_price = vals['property_price']
        if vals.get('allow_discount'):
            self.product_tmpl_id.allow_discount = vals['allow_discount']
        if vals.get('reasonable_price'):
            self.product_tmpl_id.reasonable_price = vals['reasonable_price']
        if vals.get('property_owner'):
            self.product_tmpl_id.property_owner = vals['property_owner']
        if vals.get('construction_status'):
            self.product_tmpl_id.construction_status = vals['construction_status']
        if vals.get('floor_id'):
            self.product_tmpl_id.floor_id = vals['floor_id']
        if vals.get('sale_order'):
            self.product_tmpl_id.sale_order = vals['sale_order']
        if vals.get('project_analytical'):
            self.product_tmpl_id.project_analytical = vals['project_analytical']
        if vals.get('building_analytic_account'):
            self.product_tmpl_id.building_analytic_account = vals['building_analytic_account']
        if vals.get('floor_analytic_account'):
            self.product_tmpl_id.floor_analytic_account = vals['floor_analytic_account']
        if vals.get('units_analytic_account'):
            self.product_tmpl_id.units_analytic_account = vals['units_analytic_account']
        if vals.get('order'):
            self.product_tmpl_id.order = vals['order']
        if vals.get('property_type'):
            self.product_tmpl_id.property_type = vals['property_type']
        if vals.get('furnishing'):
            self.product_tmpl_id.furnishing = vals['furnishing']
        if vals.get('build_up_area'):
            self.product_tmpl_id.build_up_area = vals['build_up_area']
        if vals.get('carpet_area'):
            self.product_tmpl_id.carpet_area = vals['carpet_area']
        if vals.get('bedroom'):
            self.product_tmpl_id.bedroom = vals['bedroom']
        if vals.get('washroom'):
            self.product_tmpl_id.washroom = vals['washroom']
        if vals.get('balconies'):
            self.product_tmpl_id.balconies = vals['balconies']
        return res

    @api.model
    def create(self, vals):
        print(f'create: {vals}')
        res = super(ProductProduct, self).create(vals)
        print(res.product_tmpl_id)
        if res.product_tmpl_id:
            res.product_tmpl_id.branch_id = res.branch_id.id
            res.product_tmpl_id.state = res.state
            res.product_tmpl_id.is_unit = res.is_unit
            res.product_tmpl_id.project = res.project.id
            res.product_tmpl_id.multi_image = res.multi_image.ids
            res.product_tmpl_id.short_name = res.short_name
            res.product_tmpl_id.code = res.code
            res.product_tmpl_id.building = res.building.id
            res.product_tmpl_id.unit_type = res.unit_type
            res.product_tmpl_id.view_type = res.view_type
            res.product_tmpl_id.property_name = res.property_name
            res.product_tmpl_id.category = res.category
            res.product_tmpl_id.property_price = res.property_price
            res.product_tmpl_id.allow_discount = res.allow_discount
            res.product_tmpl_id.reasonable_price = res.reasonable_price
            res.product_tmpl_id.property_owner = res.property_owner.id
            res.product_tmpl_id.construction_status = res.construction_status
            res.product_tmpl_id.floor_id = res.floor_id.id
            res.product_tmpl_id.sale_order = res.sale_order.id
            res.product_tmpl_id.project_analytical = res.project_analytical.id
            res.product_tmpl_id.building_analytic_account = res.building_analytic_account.id
            res.product_tmpl_id.floor_analytic_account = res.floor_analytic_account.id
            res.product_tmpl_id.units_analytic_account = res.units_analytic_account.id
            res.product_tmpl_id.order = res.order.id
            res.product_tmpl_id.property_type = res.property_type
            res.product_tmpl_id.furnishing = res.furnishing
            res.product_tmpl_id.build_up_area = res.build_up_area
            res.product_tmpl_id.carpet_area = res.carpet_area
            res.product_tmpl_id.bedroom = res.bedroom
            res.product_tmpl_id.washroom = res.washroom
            res.product_tmpl_id.balconies = res.balconies
            # res.product_tmpl_id.unit_id = res.id
        return res

    def _prepare_variant_values(self, combination):
        print('_prepare_variant_values')
        variant_dict = super()._prepare_variant_values(combination)
        variant_dict['branch_id'] = self.branch_id.id
        variant_dict['state'] = self.state
        variant_dict['is_unit'] = self.is_unit
        variant_dict['project'] = self.project.id
        variant_dict['multi_image'] = self.multi_image.ids
        variant_dict['short_name'] = self.short_name
        variant_dict['code'] = self.code
        variant_dict['building'] = self.building.id
        variant_dict['unit_type'] = self.unit_type
        variant_dict['view_type'] = self.view_type
        variant_dict['property_name'] = self.property_name
        variant_dict['category'] = self.category
        variant_dict['property_price'] = self.property_price
        variant_dict['allow_discount'] = self.allow_discount
        variant_dict['reasonable_price'] = self.reasonable_price
        variant_dict['property_owner'] = self.property_owner.id
        variant_dict['construction_status'] = self.construction_status
        variant_dict['floor_id'] = self.floor_id.id
        variant_dict['sale_order'] = self.sale_order.id
        variant_dict['project_analytical'] = self.project_analytical.id
        variant_dict['building_analytic_account'] = self.building_analytic_account.id
        variant_dict['floor_analytic_account'] = self.floor_analytic_account.id
        variant_dict['units_analytic_account'] = self.units_analytic_account.id
        variant_dict['order'] = self.order.id
        variant_dict['property_type'] = self.property_type
        variant_dict['furnishing'] = self.furnishing
        variant_dict['build_up_area'] = self.build_up_area
        variant_dict['carpet_area'] = self.carpet_area
        variant_dict['bedroom'] = self.bedroom
        variant_dict['washroom'] = self.washroom
        variant_dict['balconies'] = self.balconies
        # variant_dict['unit_id'] = self.id
        return variant_dict
