# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2023 Tecnativa - Carolina Fernandez
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo.addons.base.tests.common import BaseCommon


@freeze_time("2016-02-28")
class TestContractSaleInvoicing(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.contract = cls.env["contract.contract"].create(
            {
                "name": "Test Contract",
                "partner_id": cls.partner.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.contract.group_id = cls.env["account.analytic.account"].search([], limit=1)
        cls.product_so = cls.env.ref("product.product_product_1")
        cls.product_so.invoice_policy = "order"
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product_so.name,
                            "product_id": cls.product_so.id,
                            "product_uom_qty": 2,
                            "product_uom": cls.product_so.uom_id.id,
                            "price_unit": cls.product_so.list_price,
                        },
                    )
                ],
                "pricelist_id": cls.partner.property_product_pricelist.id,
                "analytic_account_id": cls.contract.group_id.id,
            }
        )

    def test_not_sale_invoicing(self):
        self.contract.invoicing_sales = False
        self.sale_order.action_confirm()
        self.contract.recurring_create_invoice()
        self.assertEqual(self.sale_order.invoice_status, "to invoice")

    def test_sale_invoicing(self):
        self.contract.invoicing_sales = True
        self.sale_order.action_confirm()
        self.contract.recurring_create_invoice()
        self.assertEqual(self.sale_order.invoice_status, "invoiced")

    def test_contract_sale_invoicing_without(self):
        self.contract.invoicing_sales = True
        self.sale_order.analytic_account_id = False
        self.sale_order.action_confirm()
        self.contract.recurring_create_invoice()
        self.assertEqual(self.sale_order.invoice_status, "to invoice")
