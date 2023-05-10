from odoo import models, fields, api


class ResCompanyInherited(models.Model):
    _inherit = 'res.company'

    image = fields.Image(string='Image')


class ResPartnerInherited(models.Model):
    _inherit = 'res.partner'

    name_arabic = fields.Char(string='Name Arabic')
    is_unit = fields.Boolean('Is Unit')


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    partner_id = fields.Many2one(comodel_name='res.partner', domain='[("is_unit", "=", False)]')


class PurchaserCompanyInherit(models.Model):
    _inherit = 'purchaser.company'

    purchase_individual = fields.Many2one(comodel_name='res.partner', string='Individual',
                                          domain='[("is_unit", "=", False)]')


class SaleOrderInherited(models.Model):
    _inherit = 'sale.order'

    def get_first_purchaser(self):
        if self.purchaser_ids:
            return self.purchaser_ids[0]
