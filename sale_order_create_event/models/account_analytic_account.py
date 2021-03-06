# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    sale = fields.Many2one('sale.order', string='Sale order')
