# -*- coding: utf-8 -*-
# from odoo import http


# class AccountSequence(http.Controller):
#     @http.route('/account_sequence/account_sequence', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_sequence/account_sequence/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_sequence.listing', {
#             'root': '/account_sequence/account_sequence',
#             'objects': http.request.env['account_sequence.account_sequence'].search([]),
#         })

#     @http.route('/account_sequence/account_sequence/objects/<model("account_sequence.account_sequence"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_sequence.object', {
#             'object': obj
#         })
