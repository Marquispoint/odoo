from odoo import models, fields, api


class ProjectProjectInherit(models.Model):
    _inherit = 'project.project'
    short_name = fields.Char(string='Short Name')
    code = fields.Char(string='Code', default="New")
    # parent_project = fields.Many2one(comodel_name='project.project', string='Parent Project')
    parent_project = fields.Many2one(
        comodel_name='project.project',
        relation='contents_found_rel',
        column1='lot_id',
        column2='content_id',
        string='Parent Project')

    def create_building(self):
        data = {
            'name': self.name,
            'project_id': self.id,
        }
        self.env['property.building'].create(data)

    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('project.task') or 'New'
        result = super(ProjectProjectInherit, self).create(vals)
        return result


class OLBuilding(models.Model):
    _name = 'property.building'

    image_1920 = fields.Binary('Image')
    name = fields.Char("Name")
    project_id = fields.Many2one("project.project", "Project")
    short_name = fields.Char(string='Short Name')
    code = fields.Char(string='Code', default="New")
    number_of_floors = fields.Integer("Number Of Floors", compute='_compute_number_of_floors')
    floor_ids = fields.One2many('property.floor', 'building_id', string='Floor')
    project_analytical = fields.Many2one(related="project_id.analytic_account_id", string="Project Analytic Account")
    building_account_analytical = fields.Many2one('account.analytic.account', string="Building Account Analytical")

    def _compute_number_of_floors(self):
        for rec in self:
            floors = self.env['property.floor'].search_count([('building_id.id', '=', rec.id)])
            if floors:
                rec.number_of_floors = floors
            else:
                rec.number_of_floors = 0

    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            buildings = self.env['property.building'].search([('project_id', '=', self.project_id.id)]).ids
            project = self.env['project.project'].search([('id', '=', vals['project_id'])])
            if project.code:
                vals['code'] = project.code + "-" + f'{len(buildings) + 1:02}' or 'New'
        result = super(OLBuilding, self).create(vals)
        return result

    # def generate_floor(self):
    #     if self.number_of_floors:
    #         floor_obj=self.env['property.floor']
    #         for i in range(self.number_of_floors):
    #             floor_obj.create({
    #                 'code':self.code+'-'+f'{i+1:02}',
    #                 'building_id':self.id
    #             })
    #     else:
    #         raise UserError("Enter Number Of Floors First")


class OLFloor(models.Model):
    _name = "property.floor"
    name = fields.Char("Name")
    project_id = fields.Many2one("project.project", "Project")
    short_name = fields.Char(string='Short Name')
    code = fields.Char(string='Code')
    units = fields.Many2many(comodel_name='product.product', string='Units')
    building_id = fields.Many2one(comodel_name='property.building', string='Building')
    unit_ids = fields.One2many('product.product', 'floor_id', string='Unit')
    project_analytical = fields.Many2one(related="building_id.project_id.analytic_account_id",
                                         string="Project Analytic Account")
    building_analytic_account = fields.Many2one(related="building_id.building_account_analytical",
                                                string="Building Analytic Account")
    floor_analytic_account = fields.Many2one('account.analytic.account', string="Floor Account Analytical")
    project_name = fields.Many2one(related="building_id.project_id", string="Project Name")


class PDC(models.Model):
    _name = "post.date.checks"

    customer_name = fields.Many2one("res.partner", string="Customer Name")
    name_of_cheque = fields.Char(string="Name of Cheque")
    date_of_cheqeu = fields.Date(string="Date of Cheque")
    Bank = fields.Char(string="Bank")
    attach = fields.Many2many('ir.attachment', 'ir_attach_rel', 'unit_ids', 'attachment_id', string="Attachments",
                              help="If any")
    type_char = fields.Char("Type")


class ProductInh(models.Model):
    _inherit = 'product.product'
    short_name = fields.Char(string='Short Name')
    code = fields.Char(string='Code', default="New")
    building = fields.Many2one(comodel_name='property.building', string='Building',
                               domain='[("project_id", "=", project)]')
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
    state = fields.Selection([
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('booked', 'Booked'),
        ('sold', 'Sold'),
        ('cancel', 'Cancel'),
    ], default='available')
    sale_order = fields.Many2one('sale.order', string='Sale Order')
    project_analytical = fields.Many2one(related="floor_id.building_id.project_id.analytic_account_id",
                                         string="Project Analytic Account")
    building_analytic_account = fields.Many2one(related="floor_id.building_id.building_account_analytical",
                                                string="Building Analytic Account")
    floor_analytic_account = fields.Many2one(related="floor_id.floor_analytic_account",
                                             string="Floor Account Analytical")
    units_analytic_account = fields.Many2one('account.analytic.account', string="Units Account Analytical")
    order = fields.Many2one(related='sale_order.order_line.product_id')
    # new fields
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


# class SalesOrderLines(models.Model):
#     _inherit = "sale.order.line"
#
#     # @api.onchange('product_id')
#     # def order_create(self):
#     #     # obj = self.env['product.product'].search([])
#     #     ids = 0
#     #     for rec in self:
#     #         if rec.product_id:
#     #             # rec.product_id.sale_order = rec.order_id.ids[0]
#     #             rec.product_id.state = "reserved"


class AnalyticAccountInherited(models.Model):
    _inherit = "account.analytic.account"
    project_id = fields.Many2one('project.project', string='Project')
    building_id = fields.Many2one('property.building', string='Building')
    floor_id = fields.Many2one("property.floor", string="Floor Analytic Account")
    unit_id = fields.Many2one("product.product", string="Units Analytic Account")


class CrmLeadInherited(models.Model):
    _inherit = "crm.lead"

    project_id = fields.Many2one('project.project', string='Project')
    building_id = fields.Many2one('property.building', string='Building', domain="[('project_id', '=', project_id)]")
    floor_id = fields.Many2one("property.floor", string="Floor", domain='[("building_id", "=", building_id)]')
    unit_id = fields.Many2one("product.product", string="Units",
                              domain="[('state', '=', 'available'), ('floor_id', '=', floor_id)]")
    # domain='[("floor_id", "=", floor_id)]')
    broker_id = fields.Many2one('res.partner', string="Broker", domain=[("agent", "=", True)])

    def action_sale_quotations_new(self):
        print('action_sale_quotations_new called')
        if not self.partner_id:
            return self.env["ir.actions.actions"]._for_xml_id("sale_crm.crm_quotation_partner_action")
        else:
            return self.action_new_quotation()

    def action_new_quotation(self):
        print('action_new_quotation called')
        print(self.env['res.partner'].search([('name', '=', self.unit_id.name)]))
        action = self.env["ir.actions.actions"]._for_xml_id("sale_crm.sale_action_quotations_new")
        action['context'] = {
            'search_default_opportunity_id': self.id,
            'default_opportunity_id': self.id,
            'search_default_partner_id': self.env['res.partner'].search([('name', '=', self.unit_id.name)]).id,
            'default_partner_id': self.env['res.partner'].search([('name', '=', self.unit_id.name)]).id,
            'default_project': self.project_id.id,
            'default_building': self.building_id.id,
            'default_floor': self.floor_id.id,
            'default_branch_id': self.branch_id.id,
            'default_purchaser_ids': [(0, 0, {
                'purchase_individual': self.partner_id.id,
                'purchase_company': self.company_id.id or self.env.company.id,
            })],
            'default_campaign_id': self.campaign_id.id,
            'default_medium_id': self.medium_id.id,
            'default_origin': self.name,
            'default_source_id': self.source_id.id,
            'default_company_id': self.company_id.id or self.env.company.id,
            'default_tag_ids': [(6, 0, self.tag_ids.ids)]
        }
        if self.team_id:
            action['context']['default_team_id'] = self.team_id.id,
        if self.user_id:
            action['context']['default_user_id'] = self.user_id.id
        return action

    def action_view_sale_quotation(self):
        print('action_view_sale_quotation called')
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action['context'] = {
            'search_default_draft': 1,
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_opportunity_id': self.id
        }
        action['domain'] = [('opportunity_id', '=', self.id), ('state', 'in', ['draft', 'sent'])]
        quotations = self.mapped('order_ids').filtered(lambda l: l.state in ('draft', 'sent'))
        if len(quotations) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = quotations.id
        return action

    def action_view_sale_order(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action['context'] = {
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_opportunity_id': self.id,
        }
        action['domain'] = [('opportunity_id', '=', self.id), ('state', 'not in', ('draft', 'sent', 'cancel'))]
        orders = self.mapped('order_ids').filtered(lambda l: l.state not in ('draft', 'sent', 'cancel'))
        if len(orders) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = orders.id
        return action
