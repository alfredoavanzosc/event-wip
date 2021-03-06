# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api, _
import calendar


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    product_category = fields.Many2one(
        comodel_name='product.category', string='Product category',
        required=True)
    payer = fields.Selection(
        [('school', 'School'),
         ('student', 'Student')], string='Payer', required=True)

    @api.multi
    def onchange_template_id(self, template_id, partner=False,
                             fiscal_position=False, product_category=False):
        product_obj = self.env['product.product']
        template_obj = self.env['product.template']
        if template_id and not product_category:
            return {'value': {'template_id': False},
                    'warning': {'title': _('Error in product category'),
                                'message':
                                _('You must introduce the product category')}}
        res = super(SaleOrder, self).onchange_template_id(
            template_id, partner=partner, fiscal_position=fiscal_position)
        lines = [(6, 0, [])]
        if isinstance(res, dict) and 'value' in res:
            value = res.get('value')
            order_lines = []
            if ('order_line' in value and value.get('order_line')):
                order_lines = value.get('order_line')
            for line in order_lines:
                if line[0] != 5 and line[0] == 0 and line[1] == 0:
                    if line[2].get('product_id'):
                        product = product_obj.browse(line[2].get('product_id'))
                        if product.categ_id.id == product_category:
                            line[2]['product_category'] = product.categ_id.id
                            lines.append(line)
                    elif line[2].get('product_tmpl_id'):
                        template = template_obj.browse(
                            line[2].get('product_tmpl_id'))
                        if template.categ_id.id == product_category:
                            line[2]['product_category'] = template.categ_id.id
                            lines.append(line)
            res['value']['order_line'] = lines
        return res

    @api.multi
    def action_button_confirm(self):
        for sale in self:
            if not sale.project_id:
                sale._create_automatic_contract_from_sale()
        res = super(SaleOrder, self).action_button_confirm()
        for sale in self:
            if sale.product_category.punctual_service:
                vals = {'recurring_next_date': sale.project_id.date_start,
                        'recurring_interval': 1,
                        'recurring_rule_type': 'yearly'}
            else:
                date = fields.Datetime.from_string(
                    sale.project_id.date_start).date()
                recurring_next_date = "%s-%s-%s" % (
                    date.year, date.month,
                    calendar.monthrange(date.year, date.month)[1])
                vals = {'recurring_next_date': recurring_next_date,
                        'recurring_interval': 1,
                        'recurring_rule_type': 'monthly'}
            if sale.payer == 'school':
                vals['recurring_invoices'] = True
            sale.project_id.write(vals)
        return res

    def _create_automatic_contract_from_sale(self):
        account_obj = self.env['account.analytic.account']
        min_fec = False
        max_fec = False
        for line in self.order_line:
            if not min_fec or min_fec > line.start_date:
                min_fec = line.start_date
            if not max_fec or max_fec < line.end_date:
                max_fec = line.end_date
        account_vals = {'sale': self.id,
                        'partner_id': self.partner_id.id,
                        'name': self.name,
                        'use_tasks': True,
                        'date_start': min_fec,
                        'date': max_fec}
        self.project_id = account_obj.create(account_vals)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_category = fields.Many2one(
        comodel_name='product.category', string='Product category')

    @api.multi
    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        res = super(SaleOrderLine, self).onchange_product_tmpl_id()
        if 'domain' in res:
            domain = res.get('domain')
            if 'product_id' in domain:
                cond = domain.get('product_id')
                cond.append(('categ_id', '=', self.product_category.id))
                res['domain']['product_id'] = cond
        return res
