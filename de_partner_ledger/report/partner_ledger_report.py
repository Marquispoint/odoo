# -*- coding: utf-8 -*-


from odoo import models
from datetime import datetime
from pytz import timezone


class CustomReport(models.AbstractModel):
    _name = "report.de_partner_ledger.de_partner_ledger_pdf_report"

    def get_partner_bal(self, data):
        partner_ledger = self.env['account.move.line'].search(
            [('partner_id', '=', data['partner_id']), ('date', '>=', data['start_date']),('date', '<=', data['end_date']),
             ('move_id.state', '=', 'posted'),  ('balance', '!=', 0), '|',('account_id.internal_type', '=', 'payable'), ('account_id.internal_type', '=', 'receivable')
             ,('account_id.is_pdc', '=', False)]).sorted(key=lambda r: r.date)
        return partner_ledger

    def get_opening_bal(self, data):
        open_bal = self.env['account.move.line'].search(
            [('partner_id', '=', data['partner_id']), ('date', '<', data['start_date']),
             ('move_id.state', '=', 'posted'), ('full_reconcile_id', '=', False), ('balance', '!=', 0),
             ('account_id.reconcile', '=', True), ('full_reconcile_id', '=', False), '|',
             ('account_id.internal_type', '=', 'payable'), ('account_id.internal_type', '=', 'receivable')])
        bal = 0
        for rec in open_bal:
            bal = bal + rec.balance
        return bal

    def get_foreign_opening_bal(self, data):
        for p in data['partner_id']:
            open_bal = self.env['account.move.line'].search(
                [('partner_id', '=', data['partner_id']), ('date', '<', data['start_date']),
                 ('move_id.state', '=', 'posted'), ('full_reconcile_id', '=', False), ('balance', '!=', 0),
                 ('account_id.reconcile', '=', True), ('full_reconcile_id', '=', False), '|',
                 ('account_id.internal_type', '=', 'payable'), ('account_id.internal_type', '=', 'receivable')])
        bal = 0
        for rec in open_bal:
            bal = bal + rec.amount_currency
        return bal

    def get_closing_bal(self, data):
        open_bal = self.env['account.move.line'].search(
            [('partner_id', '=', data['partner_id']), ('date', '>=', data['start_date']), ('date', '<=', data['end_date']),
             ('move_id.state', '=', 'posted'), ('full_reconcile_id', '=', False), ('balance', '!=', 0),
             ('account_id.reconcile', '=', True), ('full_reconcile_id', '=', False), '|',
             ('account_id.internal_type', '=', 'payable'), ('account_id.internal_type', '=', 'receivable'), ('account_id.is_pdc', '=', False)])
        bal = 0
        for rec in open_bal:
            bal = bal + rec.balance
        return bal

    def get_print_date(self):
        now_utc_date = datetime.now()
        now_dubai = now_utc_date.astimezone(timezone('Asia/Karachi'))
        return now_dubai.strftime('%d/%m/%Y %H:%M:%S')

    def _get_report_values(self, docids, data=None):
        dat = self.get_partner_bal(data)
        openbal = self.get_opening_bal(data)
        closingbal = self.get_closing_bal(data)
        print("opening Balance" , openbal)
        print("colsing bal" , closingbal)


        account_pdc_recieve_id = self.env['ir.config_parameter'].get_param('pdc_payments.pdc_receivable')
        account_recieve_id = self.env['account.account'].search([('id', '=', account_pdc_recieve_id)])
        print("account pdc recieve" , account_recieve_id)

        account_pdc_payable_id = self.env['ir.config_parameter'].get_param('pdc_payments.pdc_payable')
        account_payable_id = self.env['account.account'].search([('id', '=', account_pdc_payable_id)])
        print("account pdc payable", account_payable_id)

        # pdc_partner_ledger = self.env['account.move.line'].search(
        #     [('partner_id', '=', result.partner_id.id),('account_id', '=', account_recieve_id.id),('account_id', '=',account_payable_id.id)])

        pdc_partner_ledger = self.env['account.move.line'].search(
            [('partner_id', '=', data['partner_id']), ('date', '>=', data['start_date']),
             ('date', '<=', data['end_date']),
             ('move_id.state', '=', 'posted'), '|',
             ('account_id', '=', account_recieve_id.id), ('account_id', '=', account_payable_id.id)],
            order="date asc")

        print("PDC partner Ledger" , pdc_partner_ledger)

        return {
            'doc_ids': self.ids,
            'doc_model': 'partner.ledger',
            'openbal': openbal,
            'print_date': self.get_print_date(),
            'login_user': self.env.user.name,
            'foreign_openbal': self.get_foreign_opening_bal(data),
            'closingbal': closingbal + openbal,
            'dat': dat,
            'pdc_partner': pdc_partner_ledger,
            'data': data,
            'partners': data['partner_id'],
        }
