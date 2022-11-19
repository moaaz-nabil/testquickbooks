from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class Purchase_Order(models.Model):
    _inherit = "purchase.order"

    @api.model
    def _prepare_purchaseorder_export_line_dict(self, line):
        vals = {
            'Description': line.name,
            'Amount': line.price_subtotal,
        }

        if line.taxes_id:
            raise UserError(
                "QBO does not have taxable purchase orders, Taxable purchase orders cannot be exported.")

        if self.partner_id.supplier_rank:
            vals.update({
                'DetailType': 'ItemBasedExpenseLineDetail',
                'ItemBasedExpenseLineDetail': {
                    'ItemRef': {'value': self.env['product.template'].get_qbo_product_ref(line.product_id)},
                    'UnitPrice': line.price_unit,
                    'Qty': line.product_qty,
                },
            })

        return vals

    @api.model
    def _prepare_purchaseorder_export_dict(self):
        vals = {
            'DocNumber': self.name,
            'TxnDate': str(self.date_order)
        }

        if self.partner_id.supplier_rank:
            vals.update({'VendorRef': {
                        'value': self.env['res.partner'].get_qbo_partner_ref(self.partner_id)}})
        lst_line = []
        for line in self.order_line:
            line_vals = self._prepare_purchaseorder_export_line_dict(line)
            lst_line.append(line_vals)
        vals.update({'Line': lst_line})
        if self.partner_id.property_account_payable_id:
            account_payable = self.partner_id.property_account_payable_id
            if account_payable.qbo_id:
                _logger.info("ACCOUNT IS SYNCED FROM QBO!")
                vals.update({"APAccountRef": {
                    "name": account_payable.name,
                    "value": account_payable.qbo_id,
                }})
            else:
                raise ValidationError(
                    _("Please export the Account Payable associated with vendor to QBO,and then export Purchase Order"))
        return vals

    @api.model
    def exportPurchaseOrder(self):
        """export Purchase Order to QBO"""
        quickbook_config = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        access_token = None
        realmId = None
        headers = {}
        try:
            if quickbook_config.access_token:
                access_token = quickbook_config.access_token
            if quickbook_config.realm_id:
                realmId = quickbook_config.realm_id

            if not realmId or not access_token:
                raise ValidationError('Refresh token again...!')

            if access_token:
                headers['Authorization'] = 'Bearer ' + str(access_token)
                headers['Content-Type'] = 'application/json'
                _logger.info("Headers : -------------->{}".format(headers))

            if self._context.get('active_ids'):
                purchase_orders = self.browse(self._context.get('active_ids'))
            else:
                purchase_orders = self

            for purchase_order in purchase_orders:
                if purchase_order.state == 'purchase':
                    vals = purchase_order._prepare_purchaseorder_export_dict()
                    if purchase_order.quickbook_id:
                        """
                            Update Info for Record
                        """
                        SyncToken = self.read_QBO_record_object(quickbook_config, realmId, headers,
                                                                purchase_order.quickbook_id)
                        _logger.info(
                            'SyncToken : ------> {}'.format(SyncToken))
                        vals.update({
                            'Id': str(purchase_order.quickbook_id),
                            "SyncToken": SyncToken,
                            'CurrencyRef': {
                                'value': str(purchase_order.currency_id.name)
                            },
                        })

                    parsed_dict = json.dumps(vals)
                    if purchase_order.partner_id.supplier_rank:
                        _logger.info(
                            "Dict For Create/Update Record=================> {} ".format(parsed_dict))
                        result = requests.request('POST', quickbook_config.url + str(realmId) + "/purchaseorder",
                                                  headers=headers, data=parsed_dict)
                        if result.status_code == 200:
                            response = quickbook_config.convert_xmltodict(
                                result.text)
                            # update QBO invoice id
                            if purchase_order.partner_id.supplier_rank:
                                purchase_order.quickbook_id = response.get('IntuitResponse').get(
                                    'PurchaseOrder').get('Id')
                                self._cr.commit()
                            _logger.info(
                                _("%s exported successfully to QBO" % (purchase_order.name)))
                        else:
                            _logger.info(
                                _("STATUS CODE : %s" % (result.status_code)))
                            _logger.info(
                                _("RESPONSE DICT : %s" % (result.text)))
                            response = json.loads(result.text)
                            if response.get('Fault'):
                                if response.get('Fault').get('Error'):
                                    for message in response.get('Fault').get('Error'):
                                        if message.get('Detail') and message.get('Message'):
                                            raise UserError(
                                                message.get('Message') + "\n\n" + message.get('Detail'))
                else:
                    if len(purchase_orders) == 1:
                        raise ValidationError(
                            _("Only Confirmed Purchase Order is exported to QBO."))
            success_form = self.env.ref(
                'pragmatic_quickbooks_connector.export_successfull_view', False)
            return {
                'name': _('Notification'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'res.company.message',
                'views': [(success_form.id, 'form')],
                'view_id': success_form.id,
                'target': 'new',
            }
        except Exception as e:
            _logger.info('{}'.format(e))
            raise ValidationError('{}'.format((e)))

    def read_QBO_record_object(self, quickbook_config, realmId, headers, quickbooks_id):
        try:
            result = requests.request('GET',
                                      quickbook_config.url +
                                      str(realmId) + "/purchaseorder/" +
                                      str(quickbooks_id),
                                      headers=headers)
            if result.status_code == 200:
                response = quickbook_config.convert_xmltodict(result.text)
                SyncToken = response.get('IntuitResponse').get(
                    'PurchaseOrder').get('SyncToken') or 0
                print('SyncToken Dict : {}'.format(SyncToken))
                return SyncToken
            else:
                _logger.info(_("STATUS CODE : %s" % (result.status_code)))
                _logger.info(_("RESPONSE DICT : %s" % (result.text)))
                response = json.loads(result.text)
                if response.get('Fault'):
                    if response.get('Fault').get('Error'):
                        for message in response.get('Fault').get('Error'):
                            if message.get('Detail') and message.get('Message'):
                                raise UserError(
                                    message.get('Message') + "\n\n" + message.get('Detail'))
        except Exception as e:
            raise ValidationError('{}'.format(e))
