
from odoo import models, fields, api
class inheritincompany(models.Model):
    _inherit = 'res.company'

    image = fields.Image(string='Image')


# class ResPartnerInherited(models.Model):
#     _inherit = 'res.partner'
#
#     name_arabic = fields.Char(string='Name Arabic')