# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    used_coupon = fields.Many2one('sale.coupon', string="Used Coupon")

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_reward_line_values(self, program):
        self.ensure_one()
        self = self.with_context(lang=self.partner_id.lang)
        program = program.with_context(lang=self.partner_id.lang)
        if program.reward_type == 'discount':
            return self._get_reward_values_discount(program)
        elif program.reward_type == 'product':
            return [self._get_reward_values_product(program)]

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    used_coupon = fields.Many2one('sale.coupon', string="Used Coupon")

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })