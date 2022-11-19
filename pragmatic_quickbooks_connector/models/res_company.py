# -*- coding: utf-8 -*-
import base64
import json
import logging
from datetime import datetime, timedelta, date
import requests
import xmltodict
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning, AccessError
from xmltodict import ParsingInterrupted
import traceback

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    def import_all(self):
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        _logger.info("Cron company is-> {}".format(company))

        '''
        This function will call other functions for importing all functionalities
        '''

        # 1.For importing chart_of_accounts
        company.import_chart_of_accounts()
        _logger.info("Chart of accounts imported successfully.")
        self._cr.commit()
        # 2.For importing Account Tax
        company.import_tax()
        _logger.info("Taxes imported successfully.")
        self._cr.commit()
        # 3 For importing customers
        company.import_customers()
        _logger.info("Customers imported successfully.")
        self._cr.commit()
        # 4.For importing vendors
        company.import_vendors()
        _logger.info("Vendors imported successfully.")
        self._cr.commit()
        # 5.For importing product category
        company.import_product_category()
        _logger.info("Product Categories imported successfully.")
        self._cr.commit()
        # 6.For importing products
        company.import_product()
        _logger.info("Product imported successfully.")
        self._cr.commit()
        # 7.for importing inventory
        company.import_inventory()
        _logger.info("Inventory imported successfully.")
        self._cr.commit()

        # 8.For importing payment method
        company.import_payment_method()
        _logger.info("Payment methods imported successfully.")
        self._cr.commit()

        # 9.For importing payment terms from quickbooks
        company.import_payment_term_from_quickbooks()
        _logger.info("Payment terms imported successfully.")
        self._cr.commit()

        # 10.For importing sale order
        company.import_sale_order()
        _logger.info("Sale Orders imported successfully.")
        self._cr.commit()

        # 11.For importing invoice
        invoice_obj = self.env['account.move']
        invoice_obj.import_invoice()
        _logger.info("Invoice imported successfully.")
        self._cr.commit()

        creditmemo_obj = self.env['account.move']
        creditmemo_obj.import_credit_memo()
        _logger.info("Credit Memo imported successfully.")
        self._cr.commit()

        # 12.For importing purchase order
        company.import_purchase_order()
        _logger.info("Purchase Order imported successfully.")
        self._cr.commit()

        # 13.For importing vendor bill
        vendorbill_obj = self.env['account.move']
        vendorbill_obj.import_vendor_bill()
        _logger.info("Vendor Bills imported successfully.")
        self._cr.commit()

        # 14.For importing payment
        company.import_payment()
        _logger.info("Vendors imported successfully.")
        self._cr.commit()

        # 15.For importing bill payment
        company.import_bill_payment()
        _logger.info("Bill payments imported successfully.")
        self._cr.commit()

        # 16.For importing department
        company.import_department()
        _logger.info("Department imported successfully.")
        self._cr.commit()

        # 17.For importing Employee
        company.import_employee()
        _logger.info("Employees imported successfully.")
        self._cr.commit()

        success_form = self.env.ref(
            'pragmatic_quickbooks_connector.import_successfull_view', False)
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

    def import_customer_vendor_cron(self):
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        _logger.info("Cron company is-> {}".format(company))

        '''
        This function will import customers and vendors from qbo
        '''
        # For importing customers
        company.import_customers()
        _logger.info("Customers imported successfully.")
        self._cr.commit()
        # For importing vendors
        company.import_vendors()
        _logger.info("Vendors imported successfully.")
        self._cr.commit()

    def import_product_cron(self):
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        _logger.info("Cron company is-> {}".format(company))

        '''
        This function will import products from qbo
        '''
        # For importing customers
        company.import_product()
        _logger.info("Products imported successfully.")
        self._cr.commit()

    def import_customer_invoice_cron(self):
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        _logger.info("Cron company is-> {}".format(company))

        '''
        This function will import invoices from qbo
        '''
        # For importing invoices
        invoice_obj = self.env['account.move']
        invoice_obj.import_invoice(call_from='cron')
        _logger.info("Invoice imported successfully.")
        self._cr.commit()

    def import_purchase_order_cron(self):
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        _logger.info("Cron company is-> {}".format(company))

        '''
        This function will import purchase orders from qbo
        '''
        # For importing purchase order from qbo
        company.import_purchase_order()
        _logger.info("Purchase Order imported successfully.")
        self._cr.commit()

    def import_vendor_bill_cron(self):
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        _logger.info("Cron company is-> {}".format(company))
        # 13.For importing vendor bill
        vendorbill_obj = self.env['account.move']
        vendorbill_obj.import_vendor_bill(call_from='cron')
        _logger.info("Vendor Bills imported successfully.")
        self._cr.commit()

    def import_customer_payment_cron(self):
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        _logger.info("Cron company is-> {}".format(company))
        # For importing payment
        company.import_payment()
        _logger.info("Customer Payments imported successfully.")
        self._cr.commit()

    def import_vendor_payment_cron(self):
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        _logger.info("Cron company is-> {}".format(company))
        # .For importing bill payment
        company.import_bill_payment()
        _logger.info("Bill payments imported successfully.")
        self._cr.commit()

    def export_customer_payment_cron(self):
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        company.export_customer_payment()

    def export_vendor_payment_cron(self):
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        company.export_vendor_payment()

    def export_customer_vendor_cron(self):
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        company.export_customers()
        company.export_vendors()
        # company.export_products()

    def export_product_cron(self):
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        company.export_products()

    # def export_account_cron(self):
    #     company = self.env['res.users'].search([('id', '=', self._uid)]).company_id
    #     company.export_accounts()
    #     company.tax()

    def export_saleorder_cron(self):
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        company.export_sale_order()

    def export_purchaseorder_cron(self):
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        company.export_purchase_order()

    def export_customer_invoice_cron(self):
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        company.export_invoice()

    def export_vendor_bill_cron(self):
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        company.export_vendor_bill()

    def import_invoice_custom(self):
        invoice_obj = self.env['account.move']
        try:
            company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
            if self.import_mapping_inv_field and self.env.context.get('mapping'):
                headers = {}
                headers['Authorization'] = 'Bearer ' + self.access_token
                headers['accept'] = 'application/json'
                headers['Content-Type'] = 'text/plain'

                if self.env.context.get('credit'):
                    if company.import_credit_memo_by_date:
                        query = "select * from CreditMemo WHERE Metadata.LastUpdatedTime > '%s' order by Id STARTPOSITION %s MAXRESULTS %s " % (
                            self.import_credit_memo_date, self.start, self.limit)
                    else:
                        query = "select * from CreditMemo WHERE Id > '%s' order by Id STARTPOSITION %s MAXRESULTS %s " % (
                        self.quickbooks_last_invoice_imported_id, self.start, self.limit)
                else:
                    if company.import_invoice_by_date:
                        query = "select * from CreditMemo WHERE Metadata.LastUpdatedTime >= '%s' order by Id STARTPOSITION %s MAXRESULTS %s " % (
                            self.import_invoice_date, self.start, self.limit)
                    else:
                        query = "select * from invoice WHERE Id > '%s' order by Id STARTPOSITION %s MAXRESULTS %s " % (
                            self.quickbooks_last_invoice_imported_id, self.start, self.limit)
                data = requests.request('GET', self.url + str(self.realm_id) + "/query?query=" + query,headers=headers)
                if data:
                    parsed_data = json.loads(str(data.text))
                    if parsed_data:
                        if self.env.context.get('credit'):
                            if parsed_data.get('QueryResponse') and parsed_data.get('QueryResponse').get('CreditMemo'):
                                self.import_mapping_credit_id.with_context({'import': True}).json_data = parsed_data.get('QueryResponse').get('CreditMemo')
                        else:
                            if parsed_data.get('QueryResponse') and parsed_data.get('QueryResponse').get('Invoice'):
                                self.import_mapping_inv_id.with_context({'import': True}).json_data = parsed_data.get('QueryResponse').get('Invoice')
                return
            invoice_obj.import_invoice()
            _logger.info("Invoice imported successfully.")
            self._cr.commit()
            success_form = self.env.ref(
                'pragmatic_quickbooks_connector.import_successfull_view', False)
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
            _logger.error('Error : {}'.format(e))
            raise UserError(e)

    def import_credit_memo_custom(self):
        creditmemo_obj = self.env['account.move']
        creditmemo_obj.import_credit_memo()
        _logger.info("Credit Memo imported successfully.")
        self._cr.commit()
        success_form = self.env.ref(
            'pragmatic_quickbooks_connector.import_successfull_view', False)
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

    def import_vendor_bill_custom(self):
        try:
            if self.import_mapping_bill_field and self.env.context.get('mapping'):
                headers = {}
                headers['Authorization'] = 'Bearer ' + self.access_token
                headers['accept'] = 'application/json'
                headers['Content-Type'] = 'text/plain'

                query = "select * from Bill WHERE Id > '%s' order by Id STARTPOSITION %s MAXRESULTS %s " % (
                    self.quickbooks_last_vendor_bill_imported_id, self.start, self.limit)
                data = requests.request('GET', self.url + str(self.realm_id) + "/query?query=" + query, headers=headers)
                if data:
                    recs = []
                    parsed_data = json.loads(str(data.text))
                    if parsed_data:
                        if parsed_data.get('QueryResponse') and parsed_data.get('QueryResponse').get('Bill'):
                            self.import_mapping_bill_id.with_context({'import': True}).json_data = parsed_data.get('QueryResponse').get('Bill')

                return
            vendorbill_obj = self.env['account.move']
            vendorbill_obj.import_vendor_bill()
            _logger.info("Vendor Bill imported successfully.")
            self._cr.commit()
            success_form = self.env.ref(
                'pragmatic_quickbooks_connector.import_successfull_view', False)
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
            _logger.error('Error : {}'.format(e))
            raise UserError(e)

    @api.model
    def convert_xmltodict(self, response):
        """Return dictionary object"""
        try:
            # convert xml response to OrderedDict collections, return collections.OrderedDict type
            # print("Response :  ",response)
            if type(response) != dict:
                order_dict = xmltodict.parse(response)
            else:
                order_dict = response
        except ParsingInterrupted as e:
            _logger.error(e)
            raise e
        # convert OrderedDict to regular dictionary object
        response_dict = json.loads(json.dumps(order_dict))
        return response_dict

    # Company level QuickBooks Configuration fields
    client_id = fields.Char(
        'Client Id', copy=False, help="The client ID you obtain from the developer dashboard.")
    client_secret = fields.Char('Client Secret', copy=False,
                                help="The client secret you obtain from the developer dashboard.")

    auth_base_url = fields.Char('Authorization URL', default="https://appcenter.intuit.com/connect/oauth2",
                                help="User authenticate uri")
    access_token_url = fields.Char('Authorization Token URL',
                                   default="https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer",
                                   help="Exchange code for refresh and access tokens")
    request_token_url = fields.Char('Redirect URL', default="http://localhost:5000/get_auth_code",
                                    help="One of the redirect URIs listed for this project in the developer dashboard.")
    url = fields.Char('API URL', default="https://sandbox-quickbooks.api.intuit.com/v3/company/",
                      help="Intuit API URIs, use access token to call Intuit API's")

    # used for api calling, generated during authorization process.
    realm_id = fields.Char('Company Id/ Realm Id', copy=False, help="A unique company Id returned from QBO",
                           company_dependent=False)
    auth_code = fields.Char(
        'Auth Code', copy=False, help="An authenticated code", company_dependent=False)
    access_token = fields.Char('Access Token', copy=False, company_dependent=False,
                               help="The token that must be used to access the QuickBooks API. Access token expires in 3600 seconds.")
    minorversion = fields.Char('Minor Version', copy=False, default="8",
                               help="QuickBooks minor version information, used in API calls.")
    access_token_expire_in = fields.Datetime(
        'Access Token Expire In', copy=False, help="Access token expire time.")
    qbo_refresh_token = fields.Char('Refresh Token', copy=False, company_dependent=False,
                                    help="The token that must be used to access the QuickBooks API. Refresh token expires in 8726400 seconds.")
    refresh_token_expire_in = fields.Datetime(
        'Refresh Token Expire In', copy=False, help="Refresh token expire time.")

    #     '''  Tracking Fields for Customer'''
    #     x_quickbooks_last_customer_sync = fields.Datetime('Last Synced On', copy=False,)
    #     x_quickbooks_last_customer_imported_id = fields.Integer('Last Imported ID', copy=False,)
    '''  Tracking Fields for Account'''
    # last_customer_imported_id = fields.Char('Last Imported Customer Id', copy=False, default=0)
    last_acc_imported_id = fields.Char(
        'Last Imported Account Id', copy=False, default=0)
    last_imported_tax_id = fields.Char(
        'Last Imported Tax Id', copy=False, default=0)
    last_imported_tax_agency_id = fields.Char(
        'Last Imported Tax Agency Id', copy=False, default=0)
    last_imported_product_category_id = fields.Char(
        'Last Imported Product Category Id', copy=False, default=0)
    last_imported_product_id = fields.Char('Last Imported Product Id', copy=False, default=0,
                                           help="SKU ID should be Unique in QBO")
    last_imported_customer_id = fields.Char(
        'Last Imported Customer Id', copy=False, default=0)
    last_imported_vendor_id = fields.Char(
        'Last Imported Vendor Id', copy=False, default=0)
    last_imported_payment_method_id = fields.Char(
        'Last Imported Payment Method Id', copy=False, default=0)
    last_imported_payment_id = fields.Char(
        'Last Imported Payment Id', copy=False, default=0)
    last_imported_bill_payment_id = fields.Char(
        'Last Imported Bill Payment Id', copy=False, default=0)
    quickbooks_last_employee_imported_id = fields.Integer('Last Employee Id')
    quickbooks_last_dept_imported_id = fields.Integer('Last Department Id')
    quickbooks_last_sale_imported_id = fields.Integer('Last Sale Order Id')
    quickbooks_last_invoice_imported_id = fields.Integer('Last Invoice Id')
    quickbooks_last_purchase_imported_id = fields.Integer(
        'Last Purchase Order Id')
    quickbooks_last_vendor_bill_imported_id = fields.Integer(
        'Last Vendor Bill Id')
    quickbooks_last_credit_note_imported_id = fields.Integer(
        'Last Credit Note Id')
    quickbooks_last_journal_entry_imported_id = fields.Integer(
        'Last Journal Entry Id')

    start = fields.Integer('Start', default=1)
    limit = fields.Integer('Limit', default=100)
    '''  Tracking Fields for Payment Term'''
    x_quickbooks_last_paymentterm_sync = fields.Datetime(
        'Last Synced On', copy=False)
    x_quickbooks_last_paymentterm_imported_id = fields.Integer(
        'Last Imported ID', copy=False)

    # suppress_warning = fields.Boolean('Suppress Warning', default=False, copy=False,help="If you all Suppress Warnings,all the warnings will be suppressed and logs will be created instead of warnings")
    qbo_domain = fields.Selection([('sandbox', 'Sandbox'), ('production', 'Production')],
                                  string='QBO Domain', default='sandbox')
    qb_account_recievable = fields.Many2one(
        'account.account', 'Account Recievable')
    qb_account_payable = fields.Many2one('account.account', 'Account Payable')
    qb_income_account = fields.Many2one('account.account', 'Income Account')
    qb_expense_account = fields.Many2one('account.account', 'Expense Account')
    journal_entry = fields.Many2one('account.journal', help="Journal Entry")

    # Quickbooks config
    update_customer_export = fields.Boolean('Update Customer While Export', default=True)
    update_customer_import = fields.Boolean('Update Customer While Import', default=True)
    update_vendor_export = fields.Boolean('Update Vendor While Export', default=True)
    update_vendor_import = fields.Boolean('Update Vendor While Import', default=True)
    update_product_export = fields.Boolean('Update Product While Export', default=True)
    update_product_import = fields.Boolean('Update Product While Import', default=True)
    update_account_import = fields.Boolean('Update Account While Import', default=False)
    update_account_export = fields.Boolean('Update Account While Export', default=False)

    import_mapping_customer_field = fields.Boolean('Import Mapping Customer?')
    import_mapping_customer_id = fields.Many2one('mapping.fields', 'Import Customer Mapping')
    import_mapping_vendor_field = fields.Boolean('Import Mapping Vendor?')
    import_mapping_vendor_id = fields.Many2one('mapping.fields', 'Import Vendor Mapping')
    import_mapping_so_field = fields.Boolean('Import Mapping Sale Order?')
    import_mapping_so_id = fields.Many2one('mapping.fields', 'Import Sale Order')
    import_mapping_po_field = fields.Boolean('Import Mapping Purchase Order?')
    import_mapping_po_id = fields.Many2one('mapping.fields', 'Import Purchase Order')
    import_mapping_inv_field = fields.Boolean('Import Mapping Invoice?')
    import_mapping_inv_id = fields.Many2one('mapping.fields', 'Import Invoice')
    import_mapping_bill_field = fields.Boolean('Import Mapping Bills?')
    import_mapping_bill_id = fields.Many2one('mapping.fields', 'Import Bills')

    export_mapping_customer_field = fields.Boolean('Export Mapping Customer?')
    export_mapping_customer_id = fields.Many2one('mapping.fields', 'Export Customer Mapping')
    last_customer_mapping_export = fields.Datetime('Last Customer Export Mapping On')

    export_mapping_vendor_field = fields.Boolean('Export Mapping Vendor?')
    export_mapping_vendor_id = fields.Many2one('mapping.fields', 'Export Vendor Mapping')
    last_vendor_mapping_export = fields.Datetime('Last Customer Export Mapping On')

    export_mapping_so_field = fields.Boolean('Export Mapping Sale Order?')
    export_mapping_so_id = fields.Many2one('mapping.fields', 'Export Sale Order')
    last_so_mapping_export = fields.Datetime('Last SO Export Mapping On')

    export_mapping_po_field = fields.Boolean('Export Mapping Purchase Order?')
    export_mapping_po_id = fields.Many2one('mapping.fields', 'Export Purchase Order')
    last_po_mapping_export = fields.Datetime('Last PO Export Mapping On')

    export_mapping_inv_field = fields.Boolean('Export Mapping Invoice?')
    export_mapping_inv_id = fields.Many2one('mapping.fields', 'Export Invoice')
    last_inv_mapping_export = fields.Datetime('Last Invoice Export Mapping On')

    export_mapping_bill_field = fields.Boolean('Export Mapping Bill?')
    export_mapping_bill_id = fields.Many2one('mapping.fields', 'Export Bill')
    last_bill_mapping_export = fields.Datetime('Last Bill Export Mapping On')

    import_mapping_product_field = fields.Boolean('Import Mapping Product?')
    import_mapping_product_id = fields.Many2one('mapping.fields', 'Import Product')
    export_mapping_product_field = fields.Boolean('Export Mapping Product?')
    export_mapping_product_id = fields.Many2one('mapping.fields', 'Export Product')
    last_product_mapping_export = fields.Datetime('Last Product Export Mapping On')

    import_mapping_account_field = fields.Boolean('Import Mapping Account?')
    import_mapping_account_id = fields.Many2one('mapping.fields', 'Import Account')
    export_mapping_account_field = fields.Boolean('Export Mapping Account?')
    export_mapping_account_id = fields.Many2one('mapping.fields', 'Export Account')
    last_account_mapping_export = fields.Datetime('Last Account Export Mapping On')

    import_mapping_tax_field = fields.Boolean('Import Mapping Tax?')
    import_mapping_tax_id = fields.Many2one('mapping.fields', 'Import Tax')
    export_mapping_tax_field = fields.Boolean('Export Mapping Tax?')
    export_mapping_tax_id = fields.Many2one('mapping.fields', 'Export Tax')
    last_tax_mapping_export = fields.Datetime('Last Tax Export Mapping On')

    import_mapping_product_category_field = fields.Boolean('Import Mapping Product Category?')
    import_mapping_product_category_id = fields.Many2one('mapping.fields', 'Import Product Category')
    export_mapping_product_category_field = fields.Boolean('Export Mapping Product Category?')
    export_mapping_product_category_id = fields.Many2one('mapping.fields', 'Export Product Category')
    last_product_category_mapping_export = fields.Datetime('Last Product Category Export Mapping On')

    import_mapping_payment_term_field = fields.Boolean('Import Mapping Payment Term Category?')
    import_mapping_payment_term_id = fields.Many2one('mapping.fields', 'Import Payment Term')
    export_mapping_payment_term_field = fields.Boolean('Export Mapping Payment Term?')
    export_mapping_payment_term_id = fields.Many2one('mapping.fields', 'Export Payment Term')
    last_payment_term_mapping_export = fields.Datetime('Last Payment Term Export Mapping On')

    import_mapping_credit_field = fields.Boolean('Import Mapping Credit Memo?')
    import_mapping_credit_id = fields.Many2one('mapping.fields', 'Import Credit Memo')
    export_mapping_credit_field = fields.Boolean('Export Mapping Credit Memo?')
    export_mapping_credit_id = fields.Many2one('mapping.fields', 'Export Credit Memo')
    last_credit_mapping_export = fields.Datetime('Last Credit Memo Export Mapping On')

    import_mapping_cust_payment_field = fields.Boolean('Import Mapping Customer Payment?')
    import_mapping_cust_payment_id = fields.Many2one('mapping.fields', 'Import Customer Payment')

    import_mapping_vendor_payment_field = fields.Boolean('Import Mapping Vendor Payment?')
    import_mapping_vendor_payment_id = fields.Many2one('mapping.fields', 'Import Vendor Payment')

    import_mapping_department_field = fields.Boolean('Import Mapping Department Memo?')
    import_mapping_department_id = fields.Many2one('mapping.fields', 'Import Department Memo')
    export_mapping_department_field = fields.Boolean('Export Mapping Department Memo?')
    export_mapping_department_id = fields.Many2one('mapping.fields', 'Export Department Memo')
    last_department_mapping_export = fields.Datetime('Last Department Memo Export Mapping On')

    import_mapping_employee_field = fields.Boolean('Import Mapping Employee Memo?')
    import_mapping_employee_id = fields.Many2one('mapping.fields', 'Import Employee Memo')
    export_mapping_employee_field = fields.Boolean('Export Mapping Employee Memo?')
    export_mapping_employee_id = fields.Many2one('mapping.fields', 'Export Employee Memo')
    last_employee_mapping_export = fields.Datetime('Last Employee Memo Export Mapping On')

    import_account_by_date = fields.Boolean('Import Account By Custom Date?')
    import_account_date = fields.Date('Import Account Date')

    import_tax_by_date = fields.Boolean('Import Tax By Custom Date?')
    import_tax_date = fields.Date('Import Tax Date')

    import_customer_by_date = fields.Boolean('Import Customer By Custom Date?')
    import_customer_date = fields.Date('Import Customer Date')

    import_vendor_by_date = fields.Boolean('Import Vendor By Custom Date?')
    import_vendor_date = fields.Date('Import Vendor Date')

    import_pc_by_date = fields.Boolean('Import Product Category By Custom Date?')
    import_pc_date = fields.Date('Import Product Category Date')

    import_product_by_date = fields.Boolean('Import Product By Custom Date?')
    import_product_date = fields.Date('Import Product Date')

    import_payment_method_by_date = fields.Boolean('Import Payment Method By Custom Date?')
    import_payment_method_date = fields.Date('Import Payment Method Date')

    import_payment_term_by_date = fields.Boolean('Import Payment Term By Custom Date?')
    import_payment_term_date = fields.Date('Import Payment Term Date')

    import_sale_order_by_date = fields.Boolean('Import Sale Order By Custom Date?')
    import_sale_order_date = fields.Date('Import Sale Order Date')

    import_invoice_by_date = fields.Boolean('Import Invoice By Custom Date?')
    import_invoice_date = fields.Date('Import Invoice Date')

    import_credit_memo_by_date = fields.Boolean('Import Credit Memo By Custom Date?')
    import_credit_memo_date = fields.Date('Import Credit Memo Date')

    import_purchase_order_by_date = fields.Boolean('Import Purchase Order By Custom Date?')
    import_purchase_order_date = fields.Date('Import Purchase Order Date')

    import_bills_by_date = fields.Boolean('Import Bills By Custom Date?')
    import_bills_date = fields.Date('Import Bills Date')

    import_cp_by_date = fields.Boolean('Import Customer Payment By Custom Date?')
    import_cp_date = fields.Date('Import Customer Payment Date')

    import_vp_by_date = fields.Boolean('Import Vendor Payment By Custom Date?')
    import_vp_date = fields.Date('Import Vendor Payment Date')

    import_department_by_date = fields.Boolean('Import Department By Custom Date?')
    import_department_date = fields.Date('Import Department Date')

    import_employee_by_date = fields.Boolean('Import Employee By Custom Date?')
    import_employee_date = fields.Date('Import Employee Date')

    import_je_by_date = fields.Boolean('Import Journal Entry By Custom Date?')
    import_je_date = fields.Date('Import Journal Entry Date')


    # setting up the Account Receivable for Partners
    #     @api.onchange('qb_account_recievable')
    #     def onchange_qb_account_recievable(self):
    #         acc_dict={}
    #         acc_dict.update({'name':'property_account_receivable_id'})
    #         model_id = self.env['ir.model'].search([('name','=','Contact')])
    #         if model_id:
    #             field_id = self.env['ir.model.fields'].search([('name','=','property_account_receivable_id'),('field_description','=','Account Receivable'),('model_id','=',model_id.id)])
    #             if field_id:
    #                 acc_dict.update({'fields_id':field_id[0].id})
    #         account_id = self.env['account.account'].search([('name','=',self.qb_account_recievable.name)])
    #         if account_id:
    #             acc_dict.update({'value_reference':'account.account,'+str(account_id[0].id)})
    #         if acc_dict:
    # if  not self.qb_account_recievable:
    #             self.env['ir.property'].create(acc_dict)
    #         else:
    #             raise ValidationError(_('You have already set Account Receivable !changing it may cause inconsistency'))

    # Setting Up the Account Payable for Partners
    #     @api.onchange('qb_account_payable')
    #     def onchange_qb_account_payable(self):
    #         ap_dict={}
    #         ap_dict.update({'name':'property_account_payable_id'})
    #         model_id = self.env['ir.model'].search([('name','=','Contact')])
    #         if model_id:
    #             field_id = self.env['ir.model.fields'].search([('name','=','property_account_payable_id'),('field_description','=','Account Payable'),('model_id','=',model_id.id)])
    #             if field_id:
    #                 ap_dict.update({'fields_id':field_id[0].id})
    #         account_id = self.env['account.account'].search([('name','=',self.qb_account_payable.name)])
    #         if account_id:
    #             ap_dict.update({'value_reference':'account.account,'+str(account_id[0].id)})
    # if  not self.qb_account_payable:
    #         if ap_dict:
    #             self.env['ir.property'].create(ap_dict)
    #         else:
    #             raise ValidationError(_('You have already set Account Payable !changing it may cause inconsistency'))

    # Setting Up the Income Account for Product Category
    #     @api.onchange('qb_income_account')
    #     def onchange_qb_income_account(self):
    #         in_dict={}
    #         in_dict.update({'name':'property_account_income_categ_id'})
    #         model_id = self.env['ir.model'].search([('name','=','Product Category')])
    #         if model_id:
    #             field_id = self.env['ir.model.fields'].search([('name','=','property_account_income_categ_id'),('field_description','=','Income Account'),('model_id','=',model_id.id)])
    #             if field_id:
    #                 in_dict.update({'fields_id':field_id[0].id})
    #         account_id = self.env['account.account'].search([('name','=',self.qb_income_account.name)])
    #         if account_id:
    #             in_dict.update({'value_reference':'account.account,'+str(account_id[0].id)})
    #         if  in_dict:
    #             self.env['ir.property'].create(in_dict)
    #         else:
    #             raise ValidationError(_('You have already set Income Account !changing it may cause inconsistency'))

    # Setting Up the Expense Account for Product Category
    #     @api.onchange('qb_expense_account')
    #     def onchange_qb_expense_account(self):
    #         ex_dict={}
    #         ex_dict.update({'name':'property_account_expense_categ_id'})
    #         model_id = self.env['ir.model'].search([('name','=','Product Category')])
    #         if model_id:
    #             field_id = self.env['ir.model.fields'].search([('name','=','property_account_expense_categ_id'),('field_description','=','Expense Account'),('model_id','=',model_id.id)])
    #             if field_id:
    #                 ex_dict.update({'fields_id':field_id[0].id})
    #         account_id = self.env['account.account'].search([('name','=',self.qb_expense_account.name)])
    #         if account_id:
    #             ex_dict.update({'value_reference':'account.account,'+str(account_id[0].id)})
    #         if  ex_dict:
    #             self.env['ir.property'].create(ex_dict)
    #         else:
    #             raise ValidationError(_('You have already set Expense Account !changing it may cause inconsistency'))

    # @api.multi
    def login(self):
        if not self.client_id:
            raise AccessError('Please add your Client Id')
        url = self.auth_base_url + '?client_id=' + self.client_id + \
            '&scope=com.intuit.quickbooks.accounting&redirect_uri=' + \
            self.request_token_url + '&response_type=code&state=abccc'
        # print('\n\n Auth Base Url : ',self.auth_base_url,
        #       '\n Clinet Id  : ',self.client_id,
        #       '\n Refresh Token Url : ',self.request_token_url,
        #       '\n Authentication Url : ', url,'\n\n\n')
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new"
        }

    def refresh_token(self):
        """Get new access token from existing refresh token"""
        if not self:
            self = self.search([])
        _logger.info(
            "Current Context is ---> {}---{}".format(self, self._context))

        for company_id in self:
            try:
                if company_id:
                    _logger.info(
                        'Start ====> Trying to get access token for company {} '.format(company_id.name))
                    client_id = company_id.client_id
                    client_secret = company_id.client_secret
                    if not client_id:
                        raise AccessError("Please Configure Server Details")
                    raw_b64 = str(client_id + ":" + client_secret)
                    raw_b64 = raw_b64.encode('utf-8')
                    converted_b64 = base64.b64encode(raw_b64).decode('utf-8')
                    auth_header = 'Basic ' + converted_b64
                    headers = {}
                    headers['Authorization'] = str(auth_header)
                    headers['accept'] = 'application/json'
                    payload = {'grant_type': 'refresh_token',
                               'refresh_token': company_id.qbo_refresh_token}
                    _logger.info(
                        "Payload is --------------> {}".format(payload))
                    access_token = requests.post(
                        company_id.access_token_url, data=payload, headers=headers)
                    _logger.info(
                        "Access token is --------------> {}".format(access_token.text))
                    if access_token:
                        parsed_token_response = json.loads(access_token.text)
                        _logger.info(
                            "Parsed response is ------------------> {}".format(parsed_token_response))
                        if parsed_token_response:
                            company_id.write({
                                'access_token': parsed_token_response.get('access_token'),
                                'qbo_refresh_token': parsed_token_response.get('refresh_token'),
                                'access_token_expire_in': datetime.now() + timedelta(
                                    seconds=parsed_token_response.get('expires_in')),
                                'refresh_token_expire_in': datetime.now() + timedelta(
                                    seconds=parsed_token_response.get('x_refresh_token_expires_in'))
                            })
                            _logger.info(
                                _("Success =====> Token refreshed successfully!"))
            except Exception as e:
                _logger.error('Error =====> : {}  {}'.format(e, len(self)))
                if len(self) == 1:
                    raise ValidationError(e)

    @api.model
    @api.onchange('qbo_domain')
    def onchange_qbo_domain(self):
        if self.qbo_domain == 'sandbox':
            self.url = 'https://sandbox-quickbooks.api.intuit.com/v3/company/'
        else:
            self.url = 'https://quickbooks.api.intuit.com/v3/company/'

    @api.model
    def get_import_query_url(self):
        if self.access_token:
            headers = {}
            headers['Authorization'] = 'Bearer ' + str(self.access_token)
            headers['accept'] = 'application/json'
            headers['Content-Type'] = 'text/plain'
            if self.url:
                url = str(self.url) + str(self.realm_id)
            else:
                raise ValidationError(_('Url not configure'))
            return {'url': url, 'headers': headers, 'minorversion': self.minorversion}
        else:
            raise ValidationError(_('Invalid access token'))

    @api.model
    def get_import_query_url_1(self):
        if self.access_token:
            headers = {}
            headers['Authorization'] = 'Bearer ' + str(self.access_token)
            headers['accept'] = 'application/json'
            headers['Content-Type'] = 'application/json'
            if self.url:
                url = str(self.url) + str(self.realm_id)
            else:
                raise ValidationError(_('Url not configure'))
            return {'url': url, 'headers': headers, 'minorversion': self.minorversion}
        else:
            raise ValidationError(_('Invalid access token'))

    # @api.multi
    def import_customers(self):
        # try:
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        _logger.info("Company is   :-> {} ".format(company))
        if company.import_customer_by_date:
            query = "select * from Customer WHERE Metadata.LastUpdatedTime >= '%s' order by Id STARTPOSITION %s MAXRESULTS %s " % (
                company.import_customer_date, company.start, company.limit)
        else:
            query = "select * from Customer WHERE Id > '%s' order by Id STARTPOSITION %s MAXRESULTS %s " % (
            company.last_imported_customer_id, company.start, company.limit)
        url_str = company.get_import_query_url()
        url = url_str.get('url') + '/query?%squery=%s' % (
            'minorversion=' + url_str.get('minorversion') + '&' if url_str.get('minorversion') else '', query)
        data = requests.request(
            'GET', url, headers=url_str.get('headers'), verify=False)
        _logger.info("Customer data is *************** {}".format(data.text))
        if data.status_code == 200:
            _logger.info("Customer data is ------------> {}".format(data))
            res = json.loads(str(data.text))
            if self.import_mapping_customer_field and self.env.context.get('mapping'):
                if res.get('QueryResponse', False) and res.get('QueryResponse').get('Customer', []):
                    self.import_mapping_customer_id.with_context({'import': True, 'mapping_customer': True}).json_data = res.get('QueryResponse').get('Customer', [])
                else:
                    raise UserError("Empty data")
            else:
                partner = self.env['res.partner'].create_partner(
                    data, is_customer=True)
                if partner:
                    company.last_imported_customer_id = partner.qbo_customer_id
                    success_form = self.env.ref(
                        'pragmatic_quickbooks_connector.import_successfull_view', False)
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
        else:
            raise UserError("Empty Data")
            _logger.warning(_('Empty data'))
        # except Exception as e:
        #     traceback.print_exc()
        #     raise UserError(e)

    def import_vendors(self):
        # try:
        company = self.env['res.users'].search(
            [('id', '=', self._uid)], limit=1).company_id
        if company.import_vendor_by_date:
            query = "select * from vendor WHERE Metadata.LastUpdatedTime >= '%s' " % (company.import_vendor_date)
        else:
            query = "select * from vendor WHERE Id > '%s' order by Id" % (company.last_imported_vendor_id)
        url_str = company.get_import_query_url()
        url = url_str.get('url') + '/query?%squery=%s' % (
            'minorversion=' + url_str.get('minorversion') + '&' if url_str.get('minorversion') else '', query)
        data = requests.request('GET', url, headers=url_str.get('headers'))
        if data.status_code == 200:
            _logger.info(
                "Vendor data is ---------------> {}".format(data.text))
            # partner = self.env['res.partner'].create_vendor(data, is_vendor=True)
            res = json.loads(str(data.text))
            if self.import_mapping_vendor_field and self.env.context.get('mapping'):
                if res.get('QueryResponse', False).get('Vendor', False):
                    self.import_mapping_vendor_id.with_context({'import': True}).json_data = res.get('QueryResponse').get('Vendor', [])
                else:
                    raise UserError("Empty data")
            else:
                partner = self.env['res.partner'].create_partner(
                    data, is_vendor=True)

                if partner:
                    self.last_imported_vendor_id = partner.qbo_vendor_id
                    success_form = self.env.ref(
                        'pragmatic_quickbooks_connector.import_successfull_view', False)
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
        else:
            raise UserError("Empty Data")
        # except Exception as e:
        #     traceback.print_exc()
        #     raise UserError(e)

    def import_chart_of_accounts(self):
        try:
            company = self.env['res.users'].search(
                [('id', '=', self._uid)]).company_id
            if company.import_account_by_date:
                query = "select * from Account WHERE Metadata.LastUpdatedTime >= '%s'" % (company.import_account_date)
            else:
                query = "select * from Account WHERE Id > '%s' order by Id" % (company.last_acc_imported_id)

            url_str = company.get_import_query_url()
            url = url_str.get('url') + '/query?query=' + query
            data = requests.request('GET', url, headers=url_str.get('headers'))
            if data.status_code == 200:
                _logger.info(
                    "Charts of accounts data is ----------------> {}".format(data.text))
                if self.import_mapping_account_field and self.env.context.get('mapping'):
                    res = json.loads(str(data.text))
                    if res.get('QueryResponse', False).get('Account', False):
                        self.import_mapping_account_id.with_context({'import': True}).json_data = res.get('QueryResponse').get('Account', [])
                        return
                return_id, acc = self.env['account.account'].create_account_account(data, company.last_acc_imported_id or 0)
                if acc:
                    self.last_acc_imported_id = return_id
                    success_form = self.env.ref(
                        'pragmatic_quickbooks_connector.import_successfull_view', False)
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
            else:
                _logger.warning(_('Empty data'))
                raise UserError("Empty Data")
        except Exception as e:
            raise UserError(e)

    def error_message_from_quickbook(self, result, name, object_name):
        _logger.error(_("[%s] %s" % (result.status_code, result.text)))
        response = json.loads(result.text)
        if response.get('Fault'):
            if response.get('Fault').get('Error'):
                for message in response.get('Fault').get('Error'):
                    if message.get('Detail'):
                        self.env['qbo.logger'].create({
                            'odoo_name': name,
                            'odoo_object': object_name,
                            'message': 'Quickbooks Online Exception \n\n' + message.get('Detail'),
                            'created_date': datetime.now(),
                        })
                        raise UserError('Quickbooks Online Exception \n\n' + message.get('Detail'))

    def export_account_mapping(self):
        if self.last_account_mapping_export:
            account_ids = self.env['account.account'].search([
                ('write_date', '>=', self.last_account_mapping_export),
                ('qbo_acc_type', '!=', False),
                ('qbo_acc_subtype', '!=', False),
            ])
        else:
            account_ids = self.env['account.account'].search([
                ('qbo_id', '=', False),
                ('qbo_acc_type', '!=', False),
                ('qbo_acc_subtype', '!=', False),
            ])
        if self.export_mapping_account_field and self.export_mapping_account_id:
            url_str = self.get_import_query_url_1()
            url = url_str.get('url')
            headers = url_str.get('headers')
            for account_id in account_ids:
                outdict = {}
                for fields_line_id in self.export_mapping_account_id.fields_lines:
                    split_key = fields_line_id.value.split('.')
                    attr = getattr(account_id, fields_line_id.col1.name)
                    if not attr:
                        attr = ''
                    if fields_line_id.ttype in ['boolean', 'integer', 'float', 'char', 'text', 'monetary']:
                        values = attr
                    elif fields_line_id.ttype == 'selection' and fields_line_id.col.name == 'qbo_acc_type':
                        values = account_id.qbo_acc_type.name
                    elif fields_line_id.ttype == 'datetime':
                        values = fields.Datetime.to_string(attr)
                    elif fields_line_id.ttype == 'date':
                        values = fields.Date.to_string(attr)
                    elif fields_line_id.ttype in ['many2one']:
                        m2o_ref = getattr(account_id, fields_line_id.col1.name)
                        attr = getattr(m2o_ref, fields_line_id.relation_field.name)
                        values = attr or ''
                    if len(split_key) > 1:
                        if split_key[0] not in outdict:
                            outdict[split_key[0]] = {split_key[1]: values}
                        else:
                            outdict[split_key[0]].update({split_key[1]: values})
                    else:
                        outdict[split_key[0]] = values
                if account_id.qbo_id:
                    res = requests.request(
                        'GET', url + "/account/{}?minorversion=12".format(account_id.qbo_id), headers=headers, data=outdict)
                    synctoken = '0'
                    if res.status_code == 200:
                        response = res.json() #self.convert_xmltodict(res.text)
                        _logger.info("RESPONSE IS ---> {}".format(response))
                        synctoken = response.get('Account').get('SyncToken') #response.get('IntuitResponse').get('Account').get('SyncToken')
                    outdict.update({
                        'Id': account_id.qbo_id,
                        'SyncToken': synctoken
                    })
                parsed_dict = json.dumps(outdict)
                result = requests.request('POST',  url + "/account?minorversion=12", headers=headers, data=parsed_dict)
                if result.status_code == 200:
                    response = result.json() #self.convert_xmltodict(result.text)
                    qbo_id = int(response.get('Account').get('Id'))
                    account_id.qbo_id = qbo_id
                    _logger.info(
                        _("Account exported sucessfully! product template Id: %s" % (account_id.qbo_id)))
                    self._cr.commit()
                else:
                    self.error_message_from_quickbook(result, account_id.name, 'Account')

    def import_tax(self):
        try:
            if not self.env.user.company_id.country_id:
                raise UserError(_("Please set the country in the company!"))
            #         self.ensure_one()
            company = self.env['res.users'].search(
                [('id', '=', self._uid)]).company_id
            if company.import_tax_by_date:
                query = "select * from TaxCode WHERE Metadata.LastUpdatedTime >= '%s'" % (company.import_tax_date)
            else:
                query = "select * From TaxCode WHERE Id > '%s' order by Id" % (company.last_imported_tax_id)
            url_str = company.get_import_query_url()
            url = url_str.get('url') + '/query?query=' + query
            data = requests.request('GET', url, headers=url_str.get('headers'))
            _logger.info("Tax data is ---------------> {}".format(data))
            if data.status_code == 200:
                if self.import_mapping_tax_field and self.env.context.get('mapping'):
                    res = json.loads(str(data.text))
                    if res.get('QueryResponse', False) and res.get('QueryResponse').get('TaxCode', []):
                        self.import_mapping_tax_id.with_context({'import': True}).json_data = res.get('QueryResponse').get('TaxCode', [])
                else:
                    acc_tax = self.env['account.tax'].create_account_tax(data)
                    if acc_tax:
                        company.last_imported_tax_id = acc_tax.qbo_tax_id or acc_tax.qbo_tax_rate_id
                        success_form = self.env.ref(
                            'pragmatic_quickbooks_connector.import_successfull_view', False)
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
            else:
                raise UserError("Empty Data")
                _logger.warning(_('Empty data'))
        except Exception as e:
            raise UserError(e)

    def export_tax_mapping(self):
        try:
            if self.last_tax_mapping_export:
                tax_ids = self.env['account.tax'].search([
                    ('write_date', '>=', self.last_tax_mapping_export),
                    ('amount_type','!=','group'),
                ])
            else:
                tax_ids = self.env['account.tax'].search([
                    ('qbo_tax_rate_id', '=', False),
                    ('amount_type','!=','group'),
                ])
            if self.export_mapping_tax_field and self.export_mapping_tax_id:
                url_str = self.get_import_query_url_1()
                url = url_str.get('url')
                headers = url_str.get('headers')
                for tax_id in tax_ids:
                    outdict = {}
                    for fields_line_id in self.export_mapping_tax_id.fields_lines:
                        split_key = fields_line_id.value.split('.')
                        attr = getattr(tax_id, fields_line_id.col1.name)
                        if not attr:
                            attr = ''
                        if fields_line_id.ttype in ['boolean', 'integer', 'float', 'char', 'text', 'monetary']:
                            values = attr
                        elif fields_line_id.ttype == 'datetime':
                            values = fields.Datetime.to_string(attr)
                        elif fields_line_id.ttype == 'date':
                            values = fields.Date.to_string(attr)
                        elif fields_line_id.ttype in ['many2one']:
                            m2o_ref = getattr(tax_id, fields_line_id.col1.name)
                            attr = getattr(m2o_ref, fields_line_id.relation_field.name)
                            values = attr or ''
                        elif fields_line_id.ttype in ['one2many', 'many2many']:
                            line_list = []
                            if attr:
                                for line in attr:
                                    qbo_id = getattr(line, 'qbo_tax_rate_id')
                                    if not qbo_id:
                                        line_val = {'TaxApplicableOn': 'Purchase'}
                                        if tax_id.type_tax_use == 'sale':
                                            outdict.update({'TaxApplicableOn': 'Sales'})
                                        for sub_field in fields_line_id.sub_field_object_id.sub_field_ids:
                                            sub_split_key = sub_field.qb_field.split('.')
                                            sub_attr = getattr(line, sub_field.field_id.name)
                                            if sub_field.ttype == 'many2one':
                                                sub_attr = getattr(sub_attr, sub_field.relation_field.name)
                                                value = sub_attr or ""
                                            else:
                                                value = sub_attr or ""
                                            if len(sub_split_key) == 1:
                                                line_val.update({sub_field.qb_field: value})
                                            elif len(sub_split_key) == 2:
                                                if sub_split_key[0] not in line_val:
                                                    line_val.update({sub_split_key[0]: {sub_split_key[1]: value}})
                                                else:
                                                    line_val[sub_split_key[0]].update({sub_split_key[1]: value})
                                            sub_attr = getattr(line, sub_field.field_id.name)
                                        line_list.append(line_val)
                                    else:
                                        line_list.append({'TaxRateId': qbo_id})
                            else:
                                line_val = {'TaxApplicableOn': 'Purchase'}
                                if tax_id.type_tax_use == 'sale':
                                    line_val.update({'TaxApplicableOn': 'Sales'})
                                for sub_field in fields_line_id.sub_field_object_id.sub_field_ids:
                                    if sub_field.qb_field == 'TaxApplicableOn':
                                        continue
                                    sub_split_key = sub_field.qb_field.split('.')
                                    sub_attr = getattr(tax_id, sub_field.field_id.name)
                                    if sub_field.ttype == 'many2one':
                                        sub_attr = getattr(sub_attr, sub_field.relation_field.name)
                                        value = sub_attr or ""
                                    else:
                                        value = sub_attr or ""
                                    if len(sub_split_key) == 1:
                                        line_val.update({sub_field.qb_field: value})
                                    elif len(sub_split_key) == 2:
                                        if sub_split_key[0] not in line_val:
                                            line_val.update({sub_split_key[0]: {sub_split_key[1]: value}})
                                        else:
                                            line_val[sub_split_key[0]].update({sub_split_key[1]: value})
                                line_list.append(line_val)
                            values = line_list
                        if len(split_key) > 1:
                            if split_key[0] not in outdict:
                                outdict[split_key[0]] = {split_key[1]: values}
                            else:
                                outdict[split_key[0]].update({split_key[1]: values})
                        else:
                            outdict[split_key[0]] = values
                    parsed_dict = json.dumps(outdict)
                    result = requests.request('POST', url + "/taxservice/taxcode", headers=headers, data=parsed_dict)
                    if result.status_code == 200:
                        response = result.json()
                        qbo_id = int(response.get('TaxCodeId'))
                        for i in response.get('TaxRateDetails'):
                            t_type = 'purchase'
                            if i.get('TaxApplicableOn') == 'Sales':
                                t_type = 'sale'
                            tax_rate = self.env['account.tax'].search([
                                ('name', '=', i.get('TaxRateName')),
                                ('type_tax_use', '=', t_type),
                                ('qbo_tax_rate_id', '=', False)], limit=1, order="id Desc")
                            if tax_rate:
                                tax_rate.qbo_tax_rate_id = i.get('TaxRateId')
                        tax_id.qbo_tax_rate_id = qbo_id
                        _logger.info(
                            _("Tax exported sucessfully! %s" % (qbo_id)))
                        self._cr.commit()
                        self.last_tax_mapping_export = fields.Datetime.now()
                    else:
                        self.error_message_from_quickbook(result, tax_id.name, 'Tax')
        except Exception as e:
            raise UserError(e)

    # @api.multi
    def import_tax_agency(self):
        try:
            company = self.env['res.users'].search(
                [('id', '=', self._uid)]).company_id
            #         self.ensure_one()
            query = "select * From TaxAgency WHERE Id > '%s' order by Id" % (
                company.last_imported_tax_agency_id)
            url_str = company.get_import_query_url()
            url = url_str.get('url') + '/query?query=' + query
            data = requests.request('GET', url, headers=url_str.get('headers'))
            _logger.info("Tax agency data is ---------------> {}".format(data))

            if data.status_code == 200:
                agency = self.env[
                    'account.tax.agency'].create_account_tax_agency(data)
                if agency:
                    self.last_imported_tax_agency_id = agency.qbo_agency_id
                    success_form = self.env.ref(
                        'pragmatic_quickbooks_connector.import_successfull_view', False)
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
            else:
                raise UserError("Empty data")
                _logger.warning(_('Empty data'))
        except Exception as e:
            raise UserError(e)

    # @api.multi
    def import_product_category(self):
        #         self.ensure_one()
        try:
            company = self.env['res.users'].search(
                [('id', '=', self._uid)]).company_id
            if company.import_pc_by_date:
                query = "select * from Item WHERE Type='Category' and Metadata.LastUpdatedTime >= '%s'" % (company.import_pc_date)
            else:
                query = "select * from Item where Type='Category' and Id > '%s' order by Id" % (company.last_imported_product_category_id)
            url_str = company.get_import_query_url()
            url = url_str.get('url') + '/query?%squery=%s' % (
                'minorversion=' + url_str.get('minorversion') + '&' if url_str.get('minorversion') else '', query)
            data = requests.request('GET', url, headers=url_str.get('headers'))
            _logger.info(
                "Product category  data is ---------------> {}".format(data))
            if data.status_code == 200:
                if self.import_mapping_product_category_field and self.env.context.get('mapping'):
                    res = json.loads(str(data.text))
                    if 'QueryResponse' in res:
                        categories = res.get('QueryResponse').get('Item', [])
                    else:
                        categories = [res.get('Item')] or []
                    if categories:
                        self.import_mapping_product_category_id.with_context({'import': True}).json_data = categories
                else:
                    category = self.env[
                        'product.category'].create_product_category(data)
                    if category:
                        company.last_imported_product_category_id = category.qbo_product_category_id
                        success_form = self.env.ref(
                            'pragmatic_quickbooks_connector.import_successfull_view', False)
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
            else:
                raise UserError("Empty data")
                _logger.warning(_('Empty data'))
        except Exception as e:
            raise UserError(e)

    def export_product_category_mapping(self):
        if self.last_product_category_mapping_export:
            product_category_ids = self.env['product.category'].search([
                ('write_date', '>=', self.last_product_category_mapping_export),
            ])
        else:
            product_category_ids = self.env['product.category'].search([
                ('qbo_product_category_id', '=', False),
            ])
        if self.export_mapping_product_category_field and self.export_mapping_product_category_id:
            url_str = self.get_import_query_url_1()
            url = url_str.get('url')
            headers = url_str.get('headers')
            for product_category_id in product_category_ids:
                outdict = {
                    "Type": "Category",
                }
                for fields_line_id in self.export_mapping_product_category_id.fields_lines:
                    split_key = fields_line_id.value.split('.')
                    attr = getattr(product_category_id, fields_line_id.col1.name)
                    if not attr:
                        continue
                    if fields_line_id.ttype in ['boolean', 'integer', 'float', 'char', 'text', 'monetary']:
                        values = attr
                    elif fields_line_id.ttype == 'datetime':
                        values = fields.Datetime.to_string(attr)
                    elif fields_line_id.ttype == 'date':
                        values = fields.Date.to_string(attr)
                    elif fields_line_id.ttype in ['many2one']:
                        m2o_ref = getattr(product_category_id, fields_line_id.col1.name)
                        attr = ''
                        if m2o_ref:
                            attr = getattr(m2o_ref, fields_line_id.relation_field.name)
                            if attr:
                                outdict.update({"SubItem": True})
                        values = attr or ''
                    if len(split_key) > 1:
                        if split_key[0] not in outdict:
                            outdict[split_key[0]] = {split_key[1]: values}
                        else:
                            outdict[split_key[0]].update({split_key[1]: values})
                    else:
                        outdict[split_key[0]] = values
                parsed_dict = json.dumps(outdict)
                if product_category_id.qbo_product_category_id:
                    res = requests.request('GET', url + "/item/{}?minorversion=12".format(
                        product_category_id.qbo_product_category_id), headers=headers, data=parsed_dict)
                    synctoken = '0'
                    if res.status_code == 200:
                        response = res.json()
                        _logger.info("RESPONSE IS ---> {}".format(response))
                        synctoken = response.get('Item').get('SyncToken')
                    outdict.update({
                        'Id': product_category_id.qbo_product_category_id,
                        'SyncToken': synctoken
                    })
                parsed_dict = json.dumps(outdict)
                result = requests.request('POST',
                                          url + "/item?operation=update&minorversion=12",
                                          headers=headers,
                                          data=parsed_dict)
                if result.status_code == 200:
                    response = result.json()
                    qbo_id = int(response.get('Item').get('Id'))
                    product_category_id.qbo_product_category_id = qbo_id
                    self.last_product_category_mapping_export = datetime.now()
                    _logger.info(
                        _("Product exported sucessfully! product template Id: %s" % (product_category_id.qbo_product_category_id)))
                    self._cr.commit()
                else:
                    self.error_message_from_quickbook(result, product_category_id.name, 'Product Category')

    # @api.multi
    def import_product(self):
        try:
            #         self.ensure_one()
            company = self.env['res.users'].search(
                [('id', '=', self._uid)]).company_id
            query = "select * from Item where Id > '%s' order by Id STARTPOSITION %s MAXRESULTS %s  " % (
                company.last_imported_product_id, company.start, company.limit)
            url_str = company.get_import_query_url()
            url = url_str.get('url') + '/query?%squery=%s' % (
                'minorversion=' + url_str.get('minorversion') + '&' if url_str.get('minorversion') else '', query)
            data = requests.request('GET', url, headers=url_str.get('headers'))
            _logger.info(
                "Product Data is --------------------> {}".format(data))
            if data.status_code == 200:
                product = self.env['product.template'].create_product(data)
                _logger.info(
                    "product is ******************* {}".format(product))
                if product:
                    company.last_imported_product_id = product.qbo_product_id
            else:
                raise UserError("Empty data")
                _logger.warning(_('Empty data in product!!!!!'))
        except Exception as e:
            raise UserError(e)

    def export_product_mapping(self):
        if self.last_product_mapping_export:
            product_ids = self.env['product.product'].search([
                ('write_date', '>=', self.last_product_mapping_export),
                # ('qbo_product_id', '=', False),
            ])
        else:
            product_ids = self.env['product.product'].search([
                ('qbo_product_id', '=', False),
            ])
        if self.export_mapping_product_field and self.export_mapping_product_id:
            url_str = self.get_import_query_url_1()
            url = url_str.get('url')
            headers = url_str.get('headers')
            for product_id in product_ids:
                outdict = {
                    "InvStartDate": str(date.today()),
                    'TrackQtyOnHand': False,
                    'QtyOnHand': product_id.qty_available,
                    'SubItem': True,
                    'ParentRef': {
                        'value': product_id.categ_id.qbo_product_category_id
                    },
                    'AssetAccountRef': {
                        'value': product_id.categ_id.property_stock_valuation_account_id.qbo_id
                    }
                }
                if product_id.type == 'product':
                    outdict.update({'TrackQtyOnHand': True})
                for fields_line_id in self.export_mapping_product_id.fields_lines:
                    split_key = fields_line_id.value.split('.')
                    attr = getattr(product_id, fields_line_id.col1.name)
                    if not attr:
                        attr = ''
                    if fields_line_id.ttype in ['boolean', 'integer', 'float', 'char', 'text', 'monetary']:
                        values = attr
                    elif fields_line_id.ttype == 'selection' and fields_line_id.value == 'Type':
                        values = 'Inventory'
                        if product_id.type == "consu":
                            values = 'NonInventory'
                        elif product_id.type == "service":
                            values = 'Service'
                    elif fields_line_id.ttype == 'datetime':
                        values = fields.Datetime.to_string(attr)
                    elif fields_line_id.ttype == 'date':
                        values = fields.Date.to_string(attr)
                    elif fields_line_id.ttype in ['many2one']:
                        m2o_ref = getattr(product_id, fields_line_id.col1.name)
                        attr = getattr(m2o_ref, fields_line_id.relation_field.name)
                        values = attr or ''
                    if len(split_key) > 1:
                        if split_key[0] not in outdict:
                            outdict[split_key[0]] = {split_key[1]: values}
                        else:
                            outdict[split_key[0]].update({split_key[1]: values})
                    else:
                        outdict[split_key[0]] = values
                if product_id.qbo_product_id:
                    outdict.update({
                        'SyncToken': product_id.product_tmpl_id.getSyncToken(product_id.qbo_product_id),
                        'Id': product_id.qbo_product_id,
                    })
                headers = {}
                headers['Authorization'] = 'Bearer ' + str(self.access_token)
                headers['Content-Type'] = 'application/json'
                parsed_dict = json.dumps(outdict)
                result = requests.request('POST', url + "/item?operation=update&minorversion=12", headers=headers, data=parsed_dict)
                if result.status_code == 200:
                    response = self.convert_xmltodict(result.text)
                    qbo_id = int(response.get('IntuitResponse').get('Item').get('Id'))
                    product_id.qbo_product_id = qbo_id
                    self.last_product_mapping_export = datetime.now()
                    _logger.info(
                        _("Product exported sucessfully! product template Id: %s" % (product_id.qbo_product_id)))
                    self._cr.commit()
                else:
                    self.error_message_from_quickbook(result, product_id.name, 'Product')

    # @api.multi
    def import_inventory(self):
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        _logger.info("COMPANY CATEGORY IS-------------> {} ".format(company))
        try:
            query = "select * from Item"
            url_str = company.get_import_query_url()
            url = url_str.get('url') + '/query?%squery=%s' % (
                'minorversion=' + url_str.get('minorversion') + '&' if url_str.get('minorversion') else '', query)
            data = requests.request('GET', url, headers=url_str.get('headers'))
            if data.status_code == 200:
                parsed_data = data.json()
                _logger.info(
                    "Inventory data is -----------------> {}".format(parsed_data))
                for recs in parsed_data.get("QueryResponse").get('Item'):
                    _logger.info("ID IS  ---> {}".format(recs.get('Id')))
                    product_exists = self.env['product.product'].search(
                        [('qbo_product_id', '=', recs.get('Id'))])
                    _logger.info(
                        "Product exists -----------> {}".format(product_exists))
                    if product_exists and product_exists.type == 'product':
                        _logger.info("For creation of products")
                        if product_exists.qty_available != recs.get('QtyOnHand') and recs.get('QtyOnHand') >= 0:
                            stock_qty = self.env['stock.quant'].search(
                                [('product_id', '=', product_exists.id)])
                            _logger.info(
                                "Stock quantity is ------------->{}".format(stock_qty))
                            stock_change_qty = self.env[
                                'stock.change.product.qty']
                            vals = {
                                'product_id': product_exists.id,
                                'new_quantity': recs.get('QtyOnHand'),
                                'product_tmpl_id': product_exists.product_tmpl_id.id
                            }
                            _logger.info("vals are ------->{}".format(vals))
                            res = stock_change_qty.create(vals)
                            _logger.info("RES IS ----------->{}".format(res))
                            res.change_product_qty()
                            company.last_imported_product_id = product_exists.qbo_product_id
                success_form = self.env.ref(
                    'pragmatic_quickbooks_connector.import_successfull_view', False)
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
            raise ValidationError(
                _('Inventory Update Failed due to %s' % str(e)))

    def import_payment_method(self):
        try:
            company = self.env['res.users'].search(
                [('id', '=', self._uid)]).company_id
            if company.import_payment_method_by_date:
                query = "select * from PaymentMethod WHERE Metadata.LastUpdatedTime >= '%s' order by Id " % (
                    company.import_payment_method_date)
            else:
                query = "select * From PaymentMethod WHERE Id > '%s' order by Id" % (company.last_imported_payment_method_id)

            url_str = self.get_import_query_url()
            url = url_str.get('url') + '/query?%squery=%s' % (
                'minorversion=' + url_str.get('minorversion') + '&' if url_str.get('minorversion') else '', query)
            data = requests.request('GET', url, headers=url_str.get('headers'))
            _logger.info(
                "\n\n\n\n\nPayment method data is ---------------> {}".format(data.text))
            if data.status_code == 200:
                method = self.env[
                    'account.journal'].create_payment_method(data)
                if method:
                    company.last_imported_payment_method_id = method.qbo_method_id
                    success_form = self.env.ref(
                        'pragmatic_quickbooks_connector.import_successfull_view', False)
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
            else:
                _logger.warning(_('Empty data'))
                raise UserError("Empty data")
        except Exception as e:
            raise UserError(e)

    def import_payment(self):
        try:
            company = self.env['res.company'].search([('id', '=', 1)], limit=1)
            if company.import_cp_by_date:
                query = "select * from Payment WHERE Metadata.LastUpdatedTime > '%s' order by Id " % (
                    company.import_cp_date)
            else:
                query = "select * From Payment WHERE Id > '%s' order by Id" % (company.last_imported_payment_id)
            url_str = self.get_import_query_url()
            url = url_str.get('url') + '/query?%squery=%s' % (
                'minorversion=' + url_str.get('minorversion') + '&' if url_str.get('minorversion') else '', query)
            data = requests.request('GET', url, headers=url_str.get('headers'))
            _logger.info(
                "Payment data is ---------------> {}".format(data.text))

            if data.status_code == 200:
                _logger.info(
                    "Data for importing customer payments in odoo is ---> {}".format(data.text))
                if self.import_mapping_cust_payment_id and self.env.context.get('mapping'):
                    res = json.loads(str(data.text))
                    if res.get('QueryResponse', False) and res.get('QueryResponse').get('Payment', []):
                        self.import_mapping_cust_payment_id.with_context({'import': True}).json_data = res.get('QueryResponse').get('Payment', [])
                else:
                    last_imported_id = self.env[
                        'account.payment'].create_payment(data, is_customer=True)
                    if last_imported_id:
                        company.last_imported_payment_id = last_imported_id
                        success_form = self.env.ref(
                            'pragmatic_quickbooks_connector.import_successfull_view', False)
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
            else:
                raise UserError("Empty data")
                _logger.warning(_('Empty data'))
        except Exception as e:
            raise UserError(e)

    # @api.multi
    def import_bill_payment(self):
        try:
            company = self.env['res.users'].search(
                [('id', '=', self._uid)]).company_id
            if company.import_vp_by_date:
                query = "select * from billpayment WHERE Metadata.LastUpdatedTime > '%s' order by Id " % (
                    company.import_vp_date)
            else:
                query = "select * From billpayment WHERE Id > '%s' order by Id" % (company.last_imported_bill_payment_id)
            url_str = company.get_import_query_url()
            url = url_str.get('url') + '/query?%squery=%s' % (
                'minorversion=' + url_str.get('minorversion') + '&' if url_str.get('minorversion') else '', query)
            data = requests.request('GET', url, headers=url_str.get('headers'))
            _logger.info(
                " Bill payment data is -----------------> {}".format(data))
            if data.status_code == 200:
                if self.import_mapping_vendor_payment_id and self.env.context.get('mapping'):
                    res = json.loads(str(data.text))
                    if res.get('QueryResponse', False) and res.get('QueryResponse').get('BillPayment', []):
                        self.import_mapping_vendor_payment_id.with_context({'import': True}).json_data = res.get('QueryResponse').get('BillPayment', [])
                else:
                    last_imported_id = self.env[
                        'account.payment'].create_payment(data, is_vendor=True)
                    if last_imported_id:
                        company.last_imported_bill_payment_id = last_imported_id
                        success_form = self.env.ref(
                            'pragmatic_quickbooks_connector.import_successfull_view', False)
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
            else:
                raise UserError("Empty data")
                _logger.warning(_('Empty data'))
        except Exception as e:
            raise UserError(e)

    def import_payment_term_from_quickbooks(self):
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id

        payment_term = self.env['account.payment.term']

        payment_term_line = self.env['account.payment.term.line']

        if company.access_token:
            headers = {}
            headers['Authorization'] = 'Bearer ' + str(self.access_token)
            headers['Accept'] = 'application/json'
            headers['Content-Type'] = 'text/plain'
            if company.import_payment_term_by_date:
                data = requests.request('GET', company.url + str(
                    company.realm_id) + "/query?query=select * from term where Metadata.LastUpdatedTime >= '{}'".format(
                    str(company.import_payment_term_date)), headers=headers)
            else:
                data = requests.request('GET', company.url + str(
                    company.realm_id) + "/query?query=select * from term where Id > '{}'".format(
                    str(company.x_quickbooks_last_paymentterm_imported_id)), headers=headers)
            if data.status_code == 200:
                ''' Holds quickbookIds which are inserted '''
                recs = []
                parsed_data = json.loads(str(data.text))
                if parsed_data:
                    _logger.info(
                        "Payment term from qbo data is ---------------> {}".format(parsed_data))
                    if self.import_mapping_product_category_field and self.env.context.get('mapping'):
                        res = json.loads(str(data.text))
                        self.import_mapping_payment_term_id.with_context({'import': True}).json_data = res.get('QueryResponse').get('Term', [])
                    else:
                        # if parsed_data.get('QueryResponse') and parsed_data.get('QueryResponse').get('Term'):
                        for term in parsed_data.get('QueryResponse').get('Term'):
                            vals = {}
                            dict_ptl = {}
                            exists = payment_term.search(
                                [('name', '=', term.get('Name'))])
                            if not exists:
                                ''' Loop and create Data '''
                                if term.get('Active'):
                                    vals['active'] = term.get('Active')
                                if term.get('Name'):
                                    vals['note'] = term.get('Name')
                                    vals['name'] = term.get('Name')
                                '''  Insert data in account payment term line and attach its id to payment term create'''
                                #                                 if term.get('DueDays'):
                                #                                     dict_ptl['value'] = 'balance'
                                #                                     dict_ptl['days'] = term.get('DueDays')

                                vals.update(
                                    {'line_ids': [(0, 0, {'value': 'balance', 'days': term.get('DueDays')})]})
                                payment_term_create = payment_term.create(vals)
                                if payment_term_create:
                                    payment_term_create.x_quickbooks_id = term.get(
                                        'Id')
                                    recs.append(term.get('Id'))
                                    #                                     self.x_quickbooks_last_paymentterm_imported_id = term.get('Id')
                                    company.x_quickbooks_last_paymentterm_sync = fields.datetime.now()

                                    #                                     dict_ptl['payment_id'] = payment_term_create.id
                                    #                                     payment_term_line_create = payment_term_line.create(dict_ptl)
                                    # if payment_term_line_create:
                                    company.x_quickbooks_last_paymentterm_imported_id = max(
                                        recs)
                                    _logger.info(
                                        _("Payment term line was created %s" % payment_term_create.line_ids.ids))

                            else:
                                _logger.info(
                                    _("REC Exists %s" % term.get('Name')))
                            _logger.info(
                                "Records are -----------> {}".format(recs))
                            if recs:
                                company.x_quickbooks_last_paymentterm_imported_id = max(
                                    recs)
                        success_form = self.env.ref(
                            'pragmatic_quickbooks_connector.import_successfull_view', False)
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
                else:
                    raise UserError(
                        "It seems that all of the Payment Trems are already imported.")

                        #     def createOdooParentId(self, quickbook_id):

    # if quickbook_id:
    #             ''' GET DICTIONARY FROM QUICKBOOKS FOR CREATING A DICT '''
    #             if self.access_token:
    #                 headers = {}
    #                 headers['Authorization'] = 'Bearer '+str(self.access_token)
    #                 headers['accept'] = 'application/json'
    #                 headers['Content-Type']='text/plain'
    #                 print "New header is :",headers
    #             data = requests.request('GET',self.url+str(self.realm_id)+'/customer/'+str(quickbook_id),headers=headers)
    #             if data:
    #                 parsed_data = json.loads(str(data.text))
    #                 cust = parsed_data.get('Customer')
    #                 if cust:
    #                     print "CCCCCCCCCC", cust
    # if int(cust.get('Id')) > self.x_quickbooks_last_customer_imported_id:
    #                     print cust.get('Id'),"\n ------------------------------------------------"
    #                     ''' Check if the Id from Quickbook is present in odoo or not if present
    #                     then dont insert, This will avoid duplications'''
    #                     res_partner = self.env['res.partner'].search([('display_name','=',cust.get('DisplayName'))],limit=1)
    #
    #                     print "RRRRRRRRRRRR", res_partner
    #                     if res_partner:
    #                         return res_partner.id
    #                     if not res_partner:
    #                         print "Inside res_partner !!!!!!!!!!!!!"
    #                         dict = {}
    #                         if cust.get('PrimaryPhone'):
    #                             dict['phone'] = cust.get('PrimaryPhone').get('FreeFormNumber')
    #                         if cust.get('PrimaryEmailAddr'):
    #                             dict['email'] = cust.get('PrimaryEmailAddr').get('Address', ' ')
    #                         if cust.get('GivenName') and cust.get('FamilyName',' '):
    #                             dict['name'] = cust.get('GivenName')+" "+cust.get('FamilyName',' ')
    #                         if cust.get('GivenName') and not cust.get('FamilyName'):
    #                             dict['name'] = cust.get('GivenName')
    #                         if cust.get('FamilyName') and not cust.get('GivenName'):
    #                             dict['name'] = cust.get('FamilyName')
    #                         if not cust.get('FamilyName') and not cust.get('GivenName'):
    #                             if cust.get('CompanyName'):
    #                                 dict['name'] = cust.get('CompanyName')
    #
    # if cust.get('Active'):
    # if str(cust.get('Active')) == 'true':
    # dict['active']=True
    # else:
    # dict['active']=False
    #                         if cust.get('Id'):
    #                             dict['x_quickbooks_id'] = cust.get('Id')
    #                         if cust.get('Notes'):
    #                             dict['comment'] = cust.get('Notes')
    #                         if cust.get('BillWithParent'):
    #                             dict['company_type'] = 'company'
    #                         if cust.get('Mobile'):
    #                             dict['mobile'] = cust.get('Mobile').get('FreeFormNumber')
    #                         if cust.get('Fax'):
    #                             dict['fax'] = cust.get('Fax').get('FreeFormNumber')
    #                         if cust.get('WebAddr'):
    #                             dict['website'] = cust.get('WebAddr').get('URI')
    #                         if cust.get('Title'):
    #                             ''' If Title is present then first check in odoo if title exists or not
    #                             if exists attach Id of tile else create new and attach its ID'''
    #                             dict['title'] = self.attachCustomerTitle(cust.get('Title'))
    # print "FINAL DICT TITLE IS :",dict['name'],dict['title']
    # aaaaaaaaaa
    #                         dict['company_type']='company'
    #                         print "DICT TO ENTER IS : {}".format(dict)
    #                         create = res_partner.create(dict)
    #                         if create:
    #                             if cust.get('BillAddr'):
    #                                 ''' Getting BillAddr from quickbooks and Checking
    #                                     in odoo to get countryId, stateId and create
    #                                     state if not exists in odoo
    #                                     '''
    #                                 dict = {}
    #                                 '''
    #                                 Get state id if exists else create new state and return it
    #                                 '''
    #                                 if cust.get('BillAddr').get('CountrySubDivisionCode'):
    #                                     state_id = self.attachCustomerState(cust.get('BillAddr').get('CountrySubDivisionCode'),cust.get('BillAddr').get('Country'))
    #                                     if state_id:
    #                                         dict['state_id'] = state_id
    #                                     print "STATE ID IS ::::::::::",state_id
    #
    #                                 country_id = self.env['res.country'].search([
    #                                                                         ('name','=',cust.get('BillAddr').get('Country'))],limit=1)
    #                                 if country_id:
    #                                     dict['country_id'] = country_id.id
    #                                 dict['parent_id'] = create.id
    #                                 dict['type'] = 'invoice'
    #                                 dict['zip'] = cust.get('BillAddr').get('PostalCode',' ')
    #                                 dict['city'] = cust.get('BillAddr').get('City')
    #                                 dict['street'] = cust.get('BillAddr').get('Line1')
    #                                 print "DICT IS ",dict
    #                                 child_create = res_partner.create(dict)
    #                                 if child_create:
    #                                     print "Child Created BillAddr"
    #                             if cust.get('ShipAddr'):
    #                                 ''' Getting BillAddr from quickbooks and Checking
    #                                     in odoo to get countryId, stateId and create
    #                                     state if not exists in odoo
    #                                     '''
    #                                 dict = {}
    #                                 if cust.get('ShipAddr').get('CountrySubDivisionCode'):
    #                                     state_id = self.attachCustomerState(cust.get('ShipAddr').get('CountrySubDivisionCode'),cust.get('ShipAddr').get('Country'))
    #                                     if state_id:
    #                                         dict['state_id'] = state_id
    #                                     print "STATE ID IS ::::::::::",state_id
    #
    #
    #                                 country_id = self.env['res.country'].search([('name','=',cust.get('ShipAddr').get('Country'))])
    #                                 if country_id:
    #                                     dict['country_id'] = country_id[0].id
    #                                 dict['parent_id'] = create.id
    #                                 dict['type'] = 'delivery'
    #                                 dict['zip'] = cust.get('ShipAddr').get('PostalCode',' ')
    #                                 dict['city'] = cust.get('ShipAddr').get('City')
    #                                 dict['street'] = cust.get('ShipAddr').get('Line1')
    #                                 print "DICT IS ",dict
    #                                 child_create = res_partner.create(dict)
    #                                 if child_create:
    #                                     print "Child Created ShipAddr"
    #                                 print "Created Parent"
    #                                 self.x_quickbooks_last_customer_sync = fields.Datetime.now()
    #                                 self.x_quickbooks_last_customer_imported_id = int(cust.get('Id'))
    #                             return create.id
    #
    #     def attachCustomerTitle(self, title):
    #         res_partner_tile = self.env['res.partner.title']
    #         title_id = False
    #         if title:
    #             title_id = res_partner_tile.search([('name', '=', title)], limit=1)
    #             if not title_id:
    #                 ''' Create New Title in Odoo '''
    #                 create_id = res_partner_tile.create({'name': title})
    #                 create_id = title_id.id
    #                 if create_id:
    #                     return create_id.id
    #         print "TITLE IS LLLLLLLLLLLLLL",title_id
    #         return title_id.id
    #
    #     def attachCustomerState(self, state, country):
    #         res_partner_country = self.env['res.country']
    #         res_partner_state = self.env['res.country.state']
    #         state_id = False
    #         if state and country:
    #             country_id = res_partner_country.search([('name','=',country)],limit=1)
    #             if country_id:
    #                 print "Country Id is ::",country_id.name,country_id.id
    #                 state_id = res_partner_state.search([('name','=',state)],limit=1)
    #                 print "STATE ID ::::::::::::::::",state_id.country_id.id,country_id[0].id
    #                 if state_id and state_id[0].country_id.id == country_id[0].id:
    #                     print "Found State_id ",state_id
    #                     return state_id[0].id
    #                 else:
    #                     print "Inside Else"
    #                     ''' Create New State Under Country Id '''
    #                     new_state_id = res_partner_state.create({
    #                         'country_id':country_id[0].id,
    #                         'code':state[:2],
    #                         'name':state
    #                         })
    #                     if new_state_id:
    #                         print "Created new State id",new_state_id
    #                         return new_state_id.id
    #
    #     @api.multi
    #     def importcust(self):
    #         if self.access_token:
    #             headers = {}
    #             headers['Authorization'] = 'Bearer '+str(self.access_token)
    #             headers['accept'] = 'application/json'
    #             headers['Content-Type']='text/plain'
    #             print "New header is :",headers
    #             data = requests.request('GET',self.url+str(self.realm_id)+"/query?query=select * from customer where Id > '{}'".format(self.x_quickbooks_last_customer_imported_id),headers=headers)
    #             if data:
    #                 recs = []
    #                 parsed_data = json.loads(str(data.text))
    #                 if parsed_data:
    #                     print "\n\n =======Ress====== ", parsed_data,type(parsed_data)
    #                     if parsed_data.get('QueryResponse') and parsed_data.get('QueryResponse').get('Customer'):
    #                         for cust in parsed_data.get('QueryResponse').get('Customer'):
    # if int(cust.get('Id')) > self.x_quickbooks_last_customer_imported_id:
    #                             print cust.get('Id'),"\n ------------------------------------------------"
    #                             ''' Check if the Id from Quickbook is present in odoo or not if present
    #                             then dont insert, This will avoid duplications'''
    #                             res_partner = self.env['res.partner'].search([('x_quickbooks_id','=',int(cust.get('Id')))])
    #                             if not res_partner:
    #                                 dict = {}
    #                                 if cust.get('PrimaryPhone'):
    #                                     dict['phone'] = cust.get('PrimaryPhone').get('FreeFormNumber')
    #                                 if cust.get('PrimaryEmailAddr'):
    #                                     dict['email'] = cust.get('PrimaryEmailAddr').get('Address', ' ')
    #                                 if cust.get('GivenName') and cust.get('FamilyName',' '):
    #                                     dict['name'] = cust.get('GivenName')+" "+cust.get('FamilyName',' ')
    #                                 if cust.get('GivenName') and not cust.get('FamilyName'):
    #                                     dict['name'] = cust.get('GivenName')
    #                                 if cust.get('FamilyName') and not cust.get('GivenName'):
    #                                     dict['name'] = cust.get('FamilyName')
    #                                 if not cust.get('FamilyName') and not cust.get('GivenName'):
    #                                     if cust.get('CompanyName'):
    #                                         dict['name'] = cust.get('CompanyName')
    #                                         print "Came here"
    #
    # if cust.get('Active'):
    # if str(cust.get('Active')) == 'true':
    # dict['active']=True
    # else:
    # dict['active']=False
    #                                 if cust.get('ParentRef'):
    #                                     print "GOT PARENT REF",cust.get('ParentRef')
    #                                     result = self.createOdooParentId(cust.get('ParentRef').get('value'))
    #                                     if result:
    #                                         dict['parent_id'] = result
    #                                         print "ATTACHED PARENT ID"
    #
    #                                 if cust.get('Id'):
    #                                     dict['x_quickbooks_id'] = cust.get('Id')
    #                                 if cust.get('Notes'):
    #                                     dict['comment'] = cust.get('Notes')
    #                                 if cust.get('BillWithParent'):
    #                                     dict['company_type'] = 'company'
    #                                 if cust.get('Mobile'):
    #                                     dict['mobile'] = cust.get('Mobile').get('FreeFormNumber')
    #                                 if cust.get('Fax'):
    #                                     dict['fax'] = cust.get('Fax').get('FreeFormNumber')
    #                                 if cust.get('WebAddr'):
    #                                     dict['website'] = cust.get('WebAddr').get('URI')
    #                                 if cust.get('Title'):
    #
    #                                     ''' If Title is present then first check in odoo if title exists or not
    #                                     if exists attach Id of tile else create new and attach its ID'''
    #                                     dict['title'] = self.attachCustomerTitle(cust.get('Title'))
    # print "FINAL DICT TITLE IS :",dict['name'],dict['title']
    # aaaaaaaaaa
    #                                 print "DICT TO ENTER IS : {}".format(dict)
    #                                 create = res_partner.create(dict)
    #                                 if create:
    #                                     recs.append(create.id)
    #                                     if not cust.get('ParentRef'):
    #                                         if cust.get('BillAddr'):
    #                                             ''' Getting BillAddr from quickbooks and Checking
    #                                                 in odoo to get countryId, stateId and create
    #                                                 state if not exists in odoo
    #                                                 '''
    #                                             dict = {}
    #                                             '''
    #                                             Get state id if exists else create new state and return it
    #                                             '''
    #                                             if cust.get('BillAddr').get('CountrySubDivisionCode'):
    #                                                 state_id = self.attachCustomerState(cust.get('BillAddr').get('CountrySubDivisionCode'),cust.get('BillAddr').get('Country'))
    #                                                 if state_id:
    #                                                     dict['state_id'] = state_id
    #                                                 print "STATE ID IS ::::::::::",state_id
    #
    #                                             country_id = self.env['res.country'].search([
    #                                                                                     ('name','=',cust.get('BillAddr').get('Country'))],limit=1)
    #                                             if country_id:
    #                                                 dict['country_id'] = country_id.id
    #                                             dict['parent_id'] = create.id
    #                                             dict['type'] = 'invoice'
    #                                             dict['zip'] = cust.get('BillAddr').get('PostalCode',' ')
    #                                             dict['city'] = cust.get('BillAddr').get('City')
    #                                             dict['street'] = cust.get('BillAddr').get('Line1')
    #                                             print "DICT IS ",dict
    #                                             child_create = res_partner.create(dict)
    #                                             if child_create:
    #                                                 print "Child Created BillAddr"
    #
    #                                         if cust.get('ShipAddr'):
    #                                             ''' Getting BillAddr from quickbooks and Checking
    #                                                 in odoo to get countryId, stateId and create
    #                                                 state if not exists in odoo
    #                                                 '''
    #                                             dict = {}
    #                                             if cust.get('ShipAddr').get('CountrySubDivisionCode'):
    #                                                 state_id = self.attachCustomerState(cust.get('ShipAddr').get('CountrySubDivisionCode'),cust.get('ShipAddr').get('Country'))
    #                                                 if state_id:
    #                                                     dict['state_id'] = state_id
    #                                                 print "STATE ID IS ::::::::::",state_id
    #
    #
    #                                             country_id = self.env['res.country'].search([('name','=',cust.get('ShipAddr').get('Country'))])
    #                                             if country_id:
    #                                                 dict['country_id'] = country_id[0].id
    #                                             dict['parent_id'] = create.id
    #                                             dict['type'] = 'delivery'
    #                                             dict['zip'] = cust.get('ShipAddr').get('PostalCode',' ')
    #                                             dict['city'] = cust.get('ShipAddr').get('City')
    #                                             dict['street'] = cust.get('ShipAddr').get('Line1')
    #                                             print "DICT IS ",dict
    #                                             child_create = res_partner.create(dict)
    #                                             if child_create:
    #                                                 print "Child Created ShipAddr"
    #                                     print "Created Res partner"
    #                                     self.x_quickbooks_last_customer_sync = fields.Datetime.now()
    #                                     if recs:
    #                                         self.x_quickbooks_last_customer_imported_id = max(recs)
    #                                 else:
    #                                     dict = {}
    #                                     if cust.get('PrimayPhone'):
    #                                         dict['phone'] = cust.get('PrimaryPhone').get('FreeFormNumber',' ')
    #
    #                                     if cust.get('PrimaryEmailAddr'):
    #                                         dict['email'] = cust.get('PrimaryEmailAddr').get('Address', ' ')
    #                                     write = res_partner.write(dict)
    #                                     if write :
    #                                         print "Written Successfully"
    #             else:
    #                 print "Didnt got Data"

    # ----------------------------------------------------------------------------------------------------------

    # function called when clicked on sync employee button
    # @api.multi
    def import_employee(self):
        try:
            company = self.env['res.users'].search(
                [('id', '=', self._uid)]).company_id

            if company.access_token:
                headers = {}
                headers['Authorization'] = 'Bearer ' + company.access_token
                headers['accept'] = 'application/json'
                headers['Content-Type'] = 'text/plain'

                '''ALL EMPLOYEES WITH ALL THE INFO'''
                if company.import_employee_by_date:
                    query = "select * from employee WHERE Metadata.LastUpdatedTime > '%s' order by Id " % (
                        company.import_employee_date)
                else:
                    query = "select * from employee WHERE Id > '%s' order by Id" % (
                        company.quickbooks_last_employee_imported_id)
                data = requests.request('GET', company.url + str(company.realm_id) + "/query?query=" + query,
                                        headers=headers)
                if data.status_code == 200:
                    recs = []
                    parsed_data = json.loads(str(data.text))
                    if parsed_data:
                        _logger.info(
                            "Employee data  is ------------------->{}".format(parsed_data))

                        if parsed_data.get('QueryResponse') and parsed_data.get('QueryResponse').get('Employee'):
                            for emp in parsed_data.get('QueryResponse').get('Employee'):

                                # ''' This will avoid duplications'''

                                hr_employee = self.env['hr.employee'].search(
                                    [('quickbook_id', '=', emp.get('Id'))])

                                dict_e = {}

                                if emp.get('DisplayName'):
                                    dict_e['name'] = emp.get('DisplayName')

                                if emp.get('PrimaryPhone'):
                                    dict_e['mobile_phone'] = emp.get(
                                        'PrimaryPhone').get('FreeFormNumber')

                                if emp.get('PrimaryEmailAddr'):
                                    dict_e['work_email'] = emp.get(
                                        'PrimaryEmailAddr').get('Address', ' ')

                                if emp.get('Id'):
                                    dict_e['quickbook_id'] = emp.get('Id')

                                if emp.get('Mobile'):
                                    dict_e['work_phone'] = emp.get(
                                        'Mobile').get('FreeFormNumber')

                                if emp.get('EmployeeNumber'):
                                    dict_e['employee_no'] = emp.get(
                                        'EmployeeNumber')

                                if emp.get('BirthDate'):
                                    dict_e['birthday'] = emp.get('BirthDate')

                                if emp.get('Gender'):
                                    if emp.get('Gender') == 'Female':
                                        dict_e['gender'] = 'female'
                                    if emp.get('Gender') == 'Male':
                                        dict_e['gender'] = 'male'
                                    if emp.get('Gender') == 'Other':
                                        dict_e['gender'] = 'other'

                                # if emp.get('GivenName') and emp.get('FamilyName', ' '):
                                #     dict_e['name'] = emp.get('GivenName') + " " + emp.get('FamilyName', ' ')
                                #
                                # if emp.get('GivenName') and not emp.get('FamilyName'):
                                #     dict_e['name'] = emp.get('GivenName')

                                if emp.get('Notes'):
                                    dict_e['notes'] = emp.get('Notes')

                                if emp.get('HiredDate'):
                                    dict_e['hired_date'] = emp.get('HiredDate')

                                if emp.get('ReleasedDate'):
                                    dict_e['released_date'] = emp.get(
                                        'ReleasedDate')

                                if emp.get('BillRate'):
                                    dict_e['billing_rate'] = emp.get(
                                        'BillRate')

                                if emp.get('SSN'):
                                    dict_e['ssn'] = emp.get('SSN')

                                if not hr_employee:

                                    '''If employee is not present we create it'''

                                    employee_create = hr_employee.create(
                                        dict_e)

                                    if employee_create:
                                        _logger.info(
                                            'Employee Created Sucessfully..!!')

                                        recs.append(employee_create.id)
                                        if emp.get('PrimaryAddr'):

                                            dict_c = {}

                                            if emp.get('PrimaryAddr').get('CountrySubDivisionCode'):

                                                state_id = self.State(
                                                    emp.get('PrimaryAddr').get(
                                                        'CountrySubDivisionCode'),
                                                    emp.get('PrimaryAddr').get('Country'))
                                                if state_id:
                                                    dict_c[
                                                        'state_id'] = state_id
                                            country_id = self.env['res.country'].search([
                                                ('code', '=', emp.get('PrimaryAddr').get('CountrySubDivisionCode'))],
                                                limit=1)
                                            if country_id:
                                                dict_c[
                                                    'country_id'] = country_id.id
                                            if emp.get('DisplayName'):
                                                dict_c['name'] = emp.get(
                                                    'DisplayName')
                                            if emp.get('PrimaryAddr').get('Id'):
                                                dict_c['qbo_customer_id'] = emp.get(
                                                    'PrimaryAddr').get('Id')

                                            if emp.get('PrimaryAddr').get('PostalCode', ' '):
                                                dict_c['zip'] = emp.get(
                                                    'PrimaryAddr').get('PostalCode', ' ')
                                            if emp.get('PrimaryAddr').get('City'):
                                                dict_c['city'] = emp.get(
                                                    'PrimaryAddr').get('City')

                                            if emp.get('PrimaryAddr').get('Line1'):
                                                dict_c['street'] = emp.get(
                                                    'PrimaryAddr').get('Line1')

                                            if emp.get('PrimaryAddr'):
                                                check_id = emp.get(
                                                    'PrimaryAddr').get('Id')

                                                cust_obj = self.env['res.partner'].search(
                                                    [['qbo_customer_id', 'ilike', check_id]])

                                                if cust_obj:
                                                    for cust_id in cust_obj:
                                                        cust_id.write(dict_c)
                                                        '''CREATING NEW EMP'S EXISTING ADDRESS'''

                                                        employee_obj = self.env['hr.employee'].search(
                                                            [['quickbook_id', '=', emp.get('Id')]])
                                                        _logger.info("Employee object is --------------------> {}".format(
                                                            employee_obj))
                                                        if employee_obj:
                                                            # for check in
                                                            # employee_obj:
                                                            res = employee_obj.update({

                                                                'address_id': cust_id.id
                                                            })
                                                else:
                                                    '''CREATING NEW EMP'S NEW ADDRESS'''

                                                    address_create = self.env[
                                                        'res.partner'].create(dict_c)
                                                    # for addr_create in
                                                    # address_create:
                                                    dict_c[
                                                        'address_id'] = address_create.id

                                                    # write = employee_create.write(dict_c)
                                                    # if write:
                                                    #     print("Employee Created Successfully")

                                            # self.quickbooks_last_employee_sync = fields.Datetime.now()
                                            company.quickbooks_last_employee_imported_id = int(
                                                emp.get('Id'))

                                            # write = employee_create.write(dict_c)
                                            # if write:
                                            #     print("Employee Created Successfully")

                                else:
                                    if 'PrimaryAddr' in emp and emp.get('PrimaryAddr'):

                                        dict_c = {}

                                        if emp.get('PrimaryAddr').get('CountrySubDivisionCode'):

                                            state_id = self.State(
                                                emp.get('PrimaryAddr').get(
                                                    'CountrySubDivisionCode'),
                                                emp.get('PrimaryAddr').get('Country'))
                                            if state_id:
                                                dict_c['state_id'] = state_id
                                        country_id = self.env['res.country'].search([
                                            ('code', '=', emp.get('PrimaryAddr').get('CountrySubDivisionCode'))],
                                            limit=1)
                                        if country_id:
                                            dict_c[
                                                'country_id'] = country_id.id
                                        # dict['parent_id'] = create.id

                                        if emp.get('DisplayName'):
                                            dict_c['name'] = emp.get(
                                                'DisplayName')
                                        if emp.get('PrimaryAddr').get('Id'):
                                            dict_c['qbo_customer_id'] = emp.get(
                                                'PrimaryAddr').get('Id')

                                        if emp.get('PrimaryAddr').get('PostalCode', ' '):
                                            dict_c['zip'] = emp.get(
                                                'PrimaryAddr').get('PostalCode', ' ')
                                        if emp.get('PrimaryAddr').get('City'):
                                            dict_c['city'] = emp.get(
                                                'PrimaryAddr').get('City')

                                        if emp.get('PrimaryAddr').get('Line1'):
                                            dict_c['street'] = emp.get(
                                                'PrimaryAddr').get('Line1')

                                    '''If employee is present we update it'''
                                    employee_write = hr_employee.write(dict_e)

                                    if 'PrimaryAddr' in emp and emp.get('PrimaryAddr'):
                                        check_id = emp.get(
                                            'PrimaryAddr').get('Id')
                                        cust_obj = self.env['res.partner'].search(
                                            [['qbo_customer_id', '=', check_id]])

                                        if cust_obj:

                                            '''UPDATING EXISTING EMP'S EXISTING ADDRESS'''

                                            cust_obj.write(dict_c)
                                            employee_obj = self.env['hr.employee'].search(
                                                [['quickbook_id', '=', emp.get('Id')]])
                                            if employee_obj:
                                                res = employee_obj.update({

                                                    'address_id': cust_obj.id
                                                })

                                        else:
                                            '''UPDATING EXISTING EMP'S NEW ADDRESS'''

                                            address = self.env[
                                                'res.partner'].create(dict_c)
                                            dict_c['address_id'] = address.id

                                            employee_obj = self.env['hr.employee'].search(
                                                [['quickbook_id', '=', emp.get('Id')]])
                                            if employee_obj:
                                                res = employee_obj.update({

                                                    'address_id': address.id
                                                })

                                    if employee_write:
                                        company.quickbooks_last_employee_imported_id = int(
                                            emp.get('Id'))
                                        _logger.info(
                                            'Employee Updated Successfully :: %s', emp.get('Id'))
                            success_form = self.env.ref(
                                'pragmatic_quickbooks_connector.import_successfull_view', False)
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
                        else:
                            raise UserError(
                                "It seems that all of the Employees are already imported!")
                            _logger.warning(_('Empty data'))
        except Exception as e:
            raise UserError(e)

    def export_employee_mapping(self):
        if self.last_employee_mapping_export:
            employee_ids = self.env['hr.employee'].search([
                ('write_date', '>=', self.last_employee_mapping_export),
                ('quickbook_id', '=', False),
                # ('qbo_product_id', '=', False),
            ])
        else:
            employee_ids = self.env['hr.employee'].search([
                ('quickbook_id', '=', False),
            ])
        if self.export_mapping_employee_field and self.export_mapping_employee_id:
            url_str = self.get_import_query_url_1()
            url = url_str.get('url')
            headers = url_str.get('headers')
            for employee_id in employee_ids:
                outdict = {}
                for fields_line_id in self.export_mapping_employee_id.fields_lines:
                    split_key = fields_line_id.value.split('.')
                    attr = getattr(employee_id, fields_line_id.col1.name)
                    if not attr:
                        attr = ''
                    if fields_line_id.ttype in ['boolean', 'integer', 'float', 'char', 'text', 'monetary']:
                        values = attr
                    elif fields_line_id.ttype == 'selection' and fields_line_id.value == 'Gender':
                        if employee_id.gender == 'female':
                            values = 'Female' or ''
                        elif employee_id.gender == 'male':
                            values = 'Male' or ''
                        elif employee_id.gender == 'other':
                            values = 'Other' or ''
                        # if not values:
                        #     continue
                    elif fields_line_id.ttype == 'datetime':
                        values = fields.Datetime.to_string(attr)
                    elif fields_line_id.ttype == 'date':
                        values = fields.Date.to_string(attr)
                    elif fields_line_id.ttype in ['many2one']:
                        m2o_ref = getattr(employee_id, fields_line_id.col1.name)
                        attr = getattr(m2o_ref, fields_line_id.relation_field.name)
                        values = attr or ''
                    if not values:
                        continue
                    if len(split_key) > 1:
                        if split_key[0] not in outdict:
                            outdict[split_key[0]] = {split_key[1]: values}
                        else:
                            outdict[split_key[0]].update({split_key[1]: values})
                    else:
                        if fields_line_id.value == 'DisplayName':
                            name_split = values.split()
                            if len(name_split) > 1:
                                outdict['MiddleName'] = name_split[0]
                                outdict['FamilyName'] = name_split[1]
                            else:
                                outdict['MiddleName'] = name_split[0]
                                outdict['FamilyName'] = name_split[0]
                        outdict[split_key[0]] = values
                parsed_dict = json.dumps(outdict)
                if employee_id.quickbook_id:
                    res = employee_id.getSyncToken(employee_id.quickbook_id)
                    outdict.update({
                        'SyncToken': str(res),
                        'Id': employee_id.quickbook_id,
                    })
                    result = requests.request('POST', url + "/employee?operation=update", headers=headers, data=parsed_dict)
                else:
                    result = requests.request('POST', url + "/employee", headers=headers, data=parsed_dict)
                if result.status_code == 200:
                    response = result.json()
                    qbo_id = int(response.get('Employee').get('Id'))
                    employee_id.quickbook_id = qbo_id
                    self.last_employee_mapping_export = datetime.now()
                    _logger.info(
                        _("Employee exported sucessfully! Employee Id: %s" % (employee_id.quickbook_id)))
                    self._cr.commit()
                else:
                    self.error_message_from_quickbook(result, employee_id.name, 'Employee')

    def State(self, state, country):

        state_id = False
        if state and country:
            country_id = self.env['res.country'].search(
                [('name', '=', country)], limit=1)
            if country_id:

                state_id = self.env['res.country.state'].search(
                    [('name', '=', state)], limit=1)

                if state_id and state_id.country_id.id == country_id.id:
                    return state_id.id
                else:
                    new_state_id = self.env['res.country.state'].create({
                        'country_id': country_id.id,
                        'code': state[:2],
                        'name': state
                    })
                    if new_state_id:
                        return new_state_id.id

    # -------------------------------------DEPARTMENT-----------------------------------------

    # function called when clicked on sync dept button
    # @api.multi
    def import_department(self):
        try:
            company = self.env['res.users'].search(
                [('id', '=', self._uid)]).company_id

            if company.access_token:
                headers = {}
                headers['Authorization'] = 'Bearer ' + company.access_token
                headers['accept'] = 'application/json'
                headers['Content-Type'] = 'text/plain'
                if company.import_department_by_date:
                    query = "select * from department WHERE Metadata.LastUpdatedTime > '%s' order by Id " % (
                        company.import_department_date)
                else:
                    query = "select * from department WHERE Id > '%s' order by Id" % (company.quickbooks_last_dept_imported_id)
                data = requests.request('GET', company.url + str(company.realm_id) + "/query?query=" + query,
                                        headers=headers)
                if data.status_code == 200:
                    recs = []
                    parsed_data = json.loads(str(data.text))
                    if parsed_data:
                        _logger.info(
                            "Department data  is ------------------->{}".format(parsed_data))
                        if parsed_data.get('QueryResponse') and parsed_data.get('QueryResponse').get('Department'):
                            if self.import_mapping_department_field and self.import_mapping_department_id and self.env.context.get('mapping'):
                                self.import_mapping_department_id.with_context({'import': True}).json_data = parsed_data.get('QueryResponse').get('Department')
                                return
                            for emp in parsed_data.get('QueryResponse').get('Department'):
                                # ''' This will avoid duplications'''

                                hr_dept = self.env['hr.department'].search(
                                    [('quickbook_id', '=', emp.get('Id'))])
                                dict_e = {}

                                if emp.get('Name'):
                                    dict_e['name'] = emp.get('Name')

                                if emp.get('Id'):
                                    dict_e['quickbook_id'] = emp.get('Id')

                                if emp.get('ParentRef'):
                                    if emp.get('ParentRef').get('value'):
                                        parent_id = self.env['hr.department'].search(
                                            [('quickbook_id', '=', emp.get('ParentRef').get('value'))])
                                        dict_e['parent_id'] = parent_id.id

                                if not hr_dept:

                                    '''If employee is not present we create it'''

                                    dept_create = hr_dept.create(dict_e)
                                    if dept_create:

                                        company.quickbooks_last_dept_imported_id = int(
                                            emp.get('Id'))
                                        _logger.info(
                                            'Department Created Sucessfully..!!')
                                    else:
                                        _logger.info(
                                            'Department Not Created Sucessfully..!!')
                                else:
                                    dept_write = hr_dept.write(dict_e)
                                    if dept_write:
                                        company.quickbooks_last_dept_imported_id = int(
                                            emp.get('Id'))
                                        _logger.info(
                                            'Department Updated Sucessfully..!!')
                                    else:
                                        _logger.info(
                                            'Department Not Updated Sucessfully..!!')
                            success_form = self.env.ref(
                                'pragmatic_quickbooks_connector.import_successfull_view', False)
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
                        else:
                            raise UserError(
                                "It seems that all of the Departments are already imported!")
                            _logger.warning(_('Empty data'))
        except Exception as e:
            raise UserError(e)

    def export_department_mapping(self):
        if self.last_department_mapping_export:
            department_ids = self.env['hr.department'].search([
                ('write_date', '>=', self.last_department_mapping_export),
                ('quickbook_id', '=', False),
            ])
        else:
            department_ids = self.env['hr.department'].search([
                ('quickbook_id', '=', False),
            ])
        if self.export_mapping_department_field and self.export_mapping_department_id:
            url_str = self.get_import_query_url_1()
            url = url_str.get('url')
            headers = url_str.get('headers')
            for department_id in department_ids:
                outdict = {}
                for fields_line_id in self.export_mapping_department_id.fields_lines:
                    split_key = fields_line_id.value.split('.')
                    attr = getattr(department_id, fields_line_id.col1.name)
                    if not attr:
                        continue
                    if fields_line_id.ttype in ['boolean', 'integer', 'float', 'char', 'text', 'monetary']:
                        values = attr
                    elif fields_line_id.ttype == 'datetime':
                        values = fields.Datetime.to_string(attr)
                    elif fields_line_id.ttype == 'date':
                        values = fields.Date.to_string(attr)
                    elif fields_line_id.ttype in ['many2one']:
                        m2o_ref = getattr(department_id, fields_line_id.col1.name)
                        attr = ''
                        if m2o_ref:
                            attr = getattr(m2o_ref, fields_line_id.relation_field.name)
                        values = attr or ''
                    if len(split_key) > 1:
                        if split_key[0] not in outdict:
                            outdict[split_key[0]] = {split_key[1]: values}
                        else:
                            outdict[split_key[0]].update({split_key[1]: values})
                    else:
                        outdict[split_key[0]] = values
                parsed_dict = json.dumps(outdict)
                result = requests.request('POST', url + "/department?minorversion=63", headers=headers, data=parsed_dict)
                if result.status_code == 200:
                    response = result.json()
                    qbo_id = int(response.get('Department').get('Id'))
                    department_id.quickbook_id = qbo_id
                    self.last_department_mapping_export = datetime.now()
                    _logger.info(
                        _("Department exported sucessfully! Department Id: %s" % (
                            department_id.quickbook_id)))
                    self._cr.commit()
                else:
                    self.error_message_from_quickbook(result, department_id.name, 'Department')

    # ---------------------------------SALE ORDER-----------------------------

    # @api.multi
    def import_sale_order(self):
        try:
            _logger.info("Sale order")
            company = self.env['res.users'].search(
                [('id', '=', self._uid)]).company_id
            _logger.info("Company is-> {}".format(company))
            if company.access_token:
                _logger.info(
                    "Access token is ---> {}".format(company.access_token))
                headers = {}
                headers['Authorization'] = 'Bearer ' + company.access_token
                headers['accept'] = 'application/json'
                headers['Content-Type'] = 'text/plain'
                if company.import_sale_order_by_date:
                    query = "select * from estimate WHERE Metadata.LastUpdatedTime >= '%s'" % (company.import_sale_order_date)
                else:
                    query = "select * from estimate WHERE Id > '%s' order by Id  STARTPOSITION %s MAXRESULTS %s " % (
                company.quickbooks_last_sale_imported_id, company.start, company.limit)
                _logger.info("Query is -----> {}".format(query))
                data = requests.request('GET', company.url + str(company.realm_id) + "/query?query=" + query,
                                        headers=headers)
                _logger.info("************data{}".format(data.text))
                if data.status_code == 200:
                    recs = []
                    _logger.info("************data{}".format(data.text))

                    parsed_data = json.loads(str(data.text))
                    if 'QueryResponse' in parsed_data:
                        Estimate = parsed_data.get(
                            'QueryResponse').get('Estimate', [])
                    else:
                        Estimate = [parsed_data.get('Estimate')] or []
                    if len(Estimate) == 0:
                        raise UserError(
                            "It seems that all of the Sale Orders are already imported.")
                    if self.import_mapping_vendor_field and self.env.context.get('mapping'):
                        if parsed_data.get('QueryResponse').get('Estimate', []):
                            self.import_mapping_so_id.with_context({'import': True}).json_data = Estimate
                        else:
                            raise UserError("Empty data")
                        return
                    if parsed_data:

                        if parsed_data.get('QueryResponse') and parsed_data.get('QueryResponse').get('Estimate'):
                            custom_tax_id_id = [[6, False, []]]

                            for cust in parsed_data.get('QueryResponse').get('Estimate'):
                                if "CustomerRef" in cust and cust.get('CustomerRef').get('value'):
                                    # searching sales order
                                    sale_order = self.env['sale.order'].search(
                                        [('quickbook_id', '=', cust.get('Id'))])
                                    _logger.info(
                                        "Sale order exists or not!!!!!---->{}".format(sale_order))
                                    if not sale_order:
                                        _logger.info("Creating Sales order...")
                                        _logger.info("Partner value is ---------------> {}".format(
                                            cust.get('CustomerRef').get('value')))
                                        res_partner = self.env['res.partner'].search(
                                            [('qbo_customer_id', '=', cust.get('CustomerRef').get('value')),
                                             ('type', '=', 'contact')], limit=1)
                                        _logger.info(
                                            "RES PARTNER IS -> {}".format(res_partner))
                                        if res_partner:
                                            dict_s = {}

                                            # Update tax state
                                            if 'GlobalTaxCalculation' in cust and cust.get('GlobalTaxCalculation'):
                                                if cust.get('GlobalTaxCalculation') == 'TaxExcluded':
                                                    dict_s[
                                                        'tax_state'] = 'exclusive'
                                                elif cust.get('GlobalTaxCalculation') == 'TaxInclusive':
                                                    dict_s[
                                                        'tax_state'] = 'inclusive'
                                                elif cust.get('GlobalTaxCalculation') == 'NotApplicable':
                                                    dict_s[
                                                        'tax_state'] = 'notapplicable'

                                            if 'Id' in cust and cust.get('Id'):
                                                dict_s[
                                                    'partner_id'] = res_partner.id
                                                dict_s['state'] = 'sale'
                                                dict_s['quickbook_id'] = cust.get(
                                                    'Id')

                                            if 'DocNumber' in cust and cust.get('DocNumber'):
                                                dict_s['name'] = cust.get(
                                                    'DocNumber')

                                            if 'PaymentRefNum' in cust and cust.get('PaymentRefNum'):
                                                dict_s['client_order_ref'] = cust.get(
                                                    'PaymentRefNum')

                                            if 'TotalAmt' in cust and cust.get('TotalAmt'):
                                                dict_s['amount_total'] = cust.get(
                                                    'TotalAmt')

                                            if 'TxnDate' in cust and cust.get('TxnDate'):
                                                dict_s['date_order'] = cust.get(
                                                    'TxnDate')

                                            ele_in_list = len(cust.get('Line'))
                                            dict_t = cust.get(
                                                'Line')[ele_in_list - 1]
                                            _logger.info(
                                                "Dictionary before creating is----> {}".format(dict_t))
                                            #                                         if 'DiscountLineDetail' in dict_t and dict_t.get('DiscountLineDetail'):
                                            #                                             dict_s['check'] = True
                                            #                                             _logger.info("inside dictionary of discount")
                                            #                                             if dict_t.get('DiscountLineDetail').get('DiscountPercent'):
                                            #                                                 dict_s['discount_type'] = 'percentage'
                                            #                                                 print("perc is ***********",'percentage')
                                            #                                                 dict_s['amount'] = dict_t.get('DiscountLineDetail').get('DiscountPercent')
                                            #                                                 print("amount is :", dict_t.get('DiscountLineDetail').get('DiscountPercent'))
                                            #                                                 dict_s['percentage_amt'] = dict_t.get('Amount')
                                            #                                                 print("perc amt is **************",dict_t.get('Amount'))
                                            #                                             else:
                                            #                                                 dict_s['discount_type'] = 'value'
                                            #                                                 print("disc type:",'value')
                                            #                                                 dict_s['amount'] = dict_t.get('Amount')
                                            #                                                 print("amount is ***********",dict_t.get('Amount'))

                                            now = datetime.now()
                                            #                                         dict_s['date_order'] = now.strftime("%Y-%m-%d %H:%M:%S")
                                            _logger.info(
                                                "Dictionary is--->{}:".format(dict_s))
                                            so_obj = self.env[
                                                'sale.order'].create(dict_s)

                                            if so_obj:
                                                self._cr.commit()
                                                _logger.info(
                                                    "WRITING QBO ID TO SALE ORDER {}".format(so_obj.id))
                                                so_obj.write(
                                                    {'quickbook_id': cust.get('Id')})
                                                _logger.info(
                                                    "Object is --->{}".format(so_obj))
                                                _logger.info(
                                                    'Sale Order Created...!!! :: %s', cust.get('Id'))
                                            # ///////////////////////////////////////////////////////////////
                                            custom_tax_id = None
                                            for i in cust.get('Line'):
                                                _logger.info(
                                                    "Particular instance is ------------> {}".format(i))

                                                if 'SalesItemLineDetail' in i and i.get('SalesItemLineDetail'):

                                                    if i.get('SalesItemLineDetail').get('TaxCodeRef'):
                                                        _logger.info(
                                                            "Transaction data!!!")
                                                        if i.get('SalesItemLineDetail').get('TaxCodeRef').get('value'):

                                                            qb_tax_id = i.get('SalesItemLineDetail').get('TaxCodeRef').get(
                                                                'value')
                                                            record = self.env[
                                                                'account.tax']
                                                            tax = record.search([('qbo_tax_id', '=', qb_tax_id),
                                                                                 ('type_tax_use', '=', 'sale')])

                                                            if tax:
                                                                custom_tax_id = [
                                                                    (6, 0, [tax.id])]
                                                            else:
                                                                custom_tax_id = None

                                                if 'SalesItemLineDetail' in i and i.get('SalesItemLineDetail'):
                                                    _logger.info(
                                                        "SalesItem Data")
                                                    res_product = self.env['product.product'].search(
                                                        [('qbo_product_id', '=',
                                                          i.get('SalesItemLineDetail').get('ItemRef').get('value'))])

                                                    if res_product:
                                                        dict_l = {}

                                                        if i.get('Id'):
                                                            dict_l['qb_id'] = int(
                                                                i.get('Id'))

                                                        if i.get('SalesItemLineDetail').get('TaxCodeRef'):
                                                            tax_val = i.get('SalesItemLineDetail').get('TaxCodeRef').get(
                                                                'value')
                                                            if tax_val:
                                                                dict_l[
                                                                    'tax_id'] = custom_tax_id
                                                            # else:
                                                            # dict_l['tax_id']
                                                            # =

                                                    dict_l[
                                                        'product_id'] = res_product.id

                                                    if i.get('SalesItemLineDetail').get('Qty'):
                                                        dict_l['product_uom_qty'] = i.get('SalesItemLineDetail').get(
                                                            'Qty')
                                                    else:
                                                        dict_l[
                                                            'order_id'] = so_obj.id

                                                    if i.get('SalesItemLineDetail').get('UnitPrice'):
                                                        dict_l['price_unit'] = i.get('SalesItemLineDetail').get(
                                                            'UnitPrice')
                                                    else:
                                                        dict_l[
                                                            'product_id'] = res_product.id

                                                        if i.get('SalesItemLineDetail').get('Qty'):
                                                            dict_l['product_uom_qty'] = i.get('SalesItemLineDetail').get(
                                                                'Qty')
                                                        else:
                                                            dict_l[
                                                                'product_uom_qty'] = 0.0

                                                        if i.get('SalesItemLineDetail').get('UnitPrice'):
                                                            dict_l['price_unit'] = i.get('SalesItemLineDetail').get(
                                                                'UnitPrice')
                                                        else:
                                                            dict_l[
                                                                'price_unit'] = 0.0

                                                        if i.get('Description'):
                                                            dict_l['name'] = i.get(
                                                                'Description')
                                                        else:
                                                            dict_l[
                                                                'name'] = 'NA'
                                                        _logger.info(
                                                            "Dictionary for sale order line is --------> {}".format(dict_l))
                                                        create_p = self.env[
                                                            'sale.order.line'].create(dict_l)
                                                        self._cr.commit()
                                                        _logger.info(
                                                            "Sale order line --------------->{}".format(create_p))
                                                        if create_p:
                                                            company.quickbooks_last_sale_imported_id = int(
                                                                cust.get('Id'))
                                            else:
                                                raise UserError('Product ' + str(
                                                    i.get('SalesItemLineDetail').get('ItemRef').get(

                                                        'name')) + ' is not defined in Odoo. Sale Order ' + ' Name : ' + cust.get(
                                                    'DocNumber'))
                                    else:
                                        _logger.info("Else part------")
                                        res_partner = self.env['res.partner'].search(
                                            [('qbo_customer_id', '=', cust.get('CustomerRef').get('value'))])
                                        _logger.info(
                                            "Directing to else part....->{}".format(res_partner))
                                        if res_partner:
                                            dict_s = {}

                                            if cust.get('Id'):
                                                dict_s[
                                                    'partner_id'] = res_partner.id
                                                dict_s['quickbook_id'] = cust.get(
                                                    'Id')
                                                dict_s['state'] = 'sale'

                                            now = datetime.now()
                                            #                                         dict_s['date_order'] = now.strftime("%Y-%m-%d %H:%M:%S")

                                            # Update tax state
                                            if 'GlobalTaxCalculation' in cust and cust.get('GlobalTaxCalculation'):
                                                if cust.get('GlobalTaxCalculation') == 'TaxExcluded':
                                                    dict_s[
                                                        'tax_state'] = 'exclusive'
                                                elif cust.get('GlobalTaxCalculation') == 'TaxInclusive':
                                                    dict_s[
                                                        'tax_state'] = 'inclusive'
                                                elif cust.get('GlobalTaxCalculation') == 'NotApplicable':
                                                    dict_s[
                                                        'tax_state'] = 'notapplicable'

                                            if 'PaymentRefNum' in cust and cust.get('PaymentRefNum'):
                                                dict_s['client_order_ref'] = cust.get(
                                                    'PaymentRefNum')

                                            if 'DocNumber' in cust and cust.get('DocNumber'):
                                                dict_s['name'] = cust.get(
                                                    'DocNumber')

                                            if 'TotalAmt' in cust and cust.get('TotalAmt'):
                                                dict_s['amount_total'] = cust.get(
                                                    'TotalAmt')

                                            if 'TxnDate' in cust and cust.get('TxnDate'):
                                                dict_s['date_order'] = cust.get(
                                                    'TxnDate')

                                            ele_in_list = len(cust.get('Line'))

                                            dict_t = cust.get(
                                                'Line')[ele_in_list - 1]
                                            #                                         if dict_t.get('DiscountLineDetail'):
                                            #                                             dict_s['check'] = True
                                            #
                                            #                                             if dict_t.get('DiscountLineDetail').get('DiscountPercent'):
                                            #                                                 dict_s['discount_type'] = 'percentage'
                                            #                                                 dict_s['amount'] = dict_t.get('DiscountLineDetail').get('DiscountPercent')
                                            #                                                 dict_s['percentage_amt'] = dict_t.get('Amount')
                                            #                                             else:
                                            #                                                 dict_s['discount_type'] = 'value'
                                            #                                                 dict_s['amount'] = dict_t.get('Amount')
                                            _logger.info(
                                                "Dict for update is ----> {}".format(dict_s))
                                            update_so = sale_order.write(
                                                dict_s)
                                            _logger.info(
                                                "update obj {}".format(update_so))
                                            if update_so:
                                                _logger.info(
                                                    'Sale Order Updated...!!! :: %s', cust.get('Id'))
                                            custom_tax_id = None
                                            # discount_amt = 0
                                            for i in cust.get('Line'):
                                                if 'SalesItemLineDetail' in i and i.get('SalesItemLineDetail'):
                                                    if i.get('SalesItemLineDetail').get('TaxCodeRef'):

                                                        if i.get('SalesItemLineDetail').get('TaxCodeRef').get('value'):
                                                            qb_tax_id = i.get('SalesItemLineDetail').get('TaxCodeRef').get(
                                                                'value')
                                                            record = self.env[
                                                                'account.tax']
                                                            tax = record.search([('qbo_tax_id', '=', qb_tax_id),
                                                                                 ('type_tax_use', '=', 'sale')])
                                                            if tax:
                                                                custom_tax_id = [
                                                                    (6, 0, [tax.id])]
                                                            else:
                                                                custom_tax_id = None

                                                if 'SalesItemLineDetail' in i and i.get('SalesItemLineDetail'):
                                                    res_product = self.env['product.product'].search(
                                                        [('qbo_product_id', '=',
                                                          i.get('SalesItemLineDetail').get('ItemRef').get('value'))])
                                                    if res_product:
                                                        s_order_line = self.env['sale.order.line'].search(
                                                            ['&', ('product_id', '=', res_product.id),
                                                             (('order_id', '=', sale_order.id))])

                                                        if s_order_line:

                                                            dict_lp = {}

                                                            if i.get('SalesItemLineDetail').get('Qty'):
                                                                quantity = i.get('SalesItemLineDetail').get(
                                                                    'Qty')
                                                            else:
                                                                quantity = 0

                                                            if i.get('SalesItemLineDetail').get('TaxCodeRef'):

                                                                # print("TAX AVAILABLE : ",
                                                                #       i.get('SalesItemLineDetail').get('TaxCodeRef').get(
                                                                #           'value'))
                                                                tax_val = i.get('SalesItemLineDetail').get(
                                                                    'TaxCodeRef').get(
                                                                    'value')
                                                                if tax_val:
                                                                    # custom_tax_id = [(6, 0, [tax.id])]
                                                                    custom_tax_id_id = custom_tax_id
                                                                else:
                                                                    custom_tax_id_id = None

                                                            if i.get('Id'):
                                                                ol_qb_id = int(
                                                                    i.get('Id'))
                                                            else:
                                                                ol_qb_id = 0

                                                            if i.get('SalesItemLineDetail').get('UnitPrice'):
                                                                sp = i.get('SalesItemLineDetail').get(
                                                                    'UnitPrice')
                                                            else:
                                                                sp = 0

                                                            if 'Description' in i and i.get('Description'):
                                                                description = i.get(
                                                                    'Description')
                                                            else:
                                                                description = 'NA'

                                                            create_po = self.env['sale.order.line'].search(
                                                                ['&', ('product_id', '=', res_product.id),
                                                                 (('order_id', '=', sale_order.id))])

                                                            if create_po:
                                                                res = create_po.update({

                                                                    'product_id': res_product.id,
                                                                    'name': description,
                                                                    'product_uom_qty': quantity,
                                                                    'tax_id': custom_tax_id_id,
                                                                    'qb_id': ol_qb_id,
                                                                    # 'product_uom': 1,
                                                                    'price_unit': sp,
                                                                })
                                                            if create_po:
                                                                company.quickbooks_last_sale_imported_id = int(
                                                                    cust.get('Id'))

                                                        else:
                                                            '''CODE FOR NEW LINE IN EXISTING SALE ORDER'''
                                                            _logger.info(
                                                                "Code for new line in existing sale order")
                                                            res_product = self.env['product.product'].search(
                                                                [('qbo_product_id', '=',
                                                                  i.get('SalesItemLineDetail').get('ItemRef').get(
                                                                      'value'))])

                                                            if res_product:
                                                                dict_l = {}
                                                                if i.get('Id'):
                                                                    dict_l['qb_id'] = int(
                                                                        i.get('Id'))

                                                                # if discount_amt > 0:
                                                                #     dict_l['discount'] = discount_amt

                                                                if i.get('SalesItemLineDetail').get('TaxCodeRef'):

                                                                    # print("TAX AVAILABLE : ",
                                                                    #       i.get('SalesItemLineDetail').get('TaxCodeRef').get(
                                                                    #           'value'))
                                                                    tax_val = i.get('SalesItemLineDetail').get(
                                                                        'TaxCodeRef').get(
                                                                        'value')
                                                                    if tax_val == 'TAX':

                                                                        dict_l[
                                                                            'tax_id'] = custom_tax_id
                                                                    else:
                                                                        dict_l[
                                                                            'tax_id'] = None

                                                                dict_l[
                                                                    'order_id'] = sale_order.id
                                                                # dict_l['order_id'] = sale_order.id

                                                                dict_l[
                                                                    'product_id'] = res_product.id

                                                                if i.get('SalesItemLineDetail').get('Qty'):
                                                                    dict_l['product_uom_qty'] = i.get(
                                                                        'SalesItemLineDetail').get('Qty')
                                                                    # cust.get('Line')[0].get('SalesItemLineDetail').get('Qty')
                                                                else:
                                                                    dict_l[
                                                                        'product_uom_qty'] = 0

                                                                if i.get('SalesItemLineDetail').get('UnitPrice'):
                                                                    dict_l['price_unit'] = i.get(
                                                                        'SalesItemLineDetail').get('UnitPrice')
                                                                else:
                                                                    dict_l[
                                                                        'price_unit'] = 0

                                                                if i.get('Description'):
                                                                    dict_l['name'] = i.get(
                                                                        'Description')
                                                                else:
                                                                    dict_l[
                                                                        'name'] = 'NA'

                                                                # dict_l['product_uom'] = 1
                                                                _logger.info(
                                                                    "Sale order line of update is ----> {}".format(dict_l))
                                                                create_p = self.env[
                                                                    'sale.order.line'].create(dict_l)
                                                                _logger.info(
                                                                    "Sale order line of creation is {}".format(create_p))
                                                                if create_p:
                                                                    company.quickbooks_last_sale_imported_id = int(
                                                                        cust.get('Id'))

                                                    else:
                                                        raise UserError('Product ' + str(
                                                            i.get('SalesItemLineDetail').get('ItemRef').get(

                                                                'name')) + ' is not defined in Odoo. Sale Order ' + ' Name : ' + cust.get(
                                                            'DocNumber'))
                            success_form = self.env.ref(
                                'pragmatic_quickbooks_connector.import_successfull_view', False)
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
                        else:
                            raise UserError(
                                "It seems that all of the Sales Order are already imported!")
        except Exception as e:
            raise UserError(e)

    # --------------------------------- INVOICE  -----------------------------
    @api.model
    def check_if_lines_present(self, cust):
        if cust.get('Line'):
            for i in cust.get('Line'):
                if i.get('SalesItemLineDetail'):
                    return True
                else:
                    return False
        else:
            return False

    # @api.model
    # def check_if_lines_present_vendor_bill(self, cust):
    #     if 'Line' in cust and cust.get('Line'):
    #         for i in cust.get('Line'):
    #             if i.get('ItemBasedExpenseLineDetail'):
    #                 _logger.info("ItemBasedExpenseLineDetail-----------------> {}".format(i.get('ItemBasedExpenseLineDetail')))
    #                 return True
    #             else:
    #                 _logger.info("NO ItemBasedExpenseLineDetail ")
    #                 return False
    #     else:
    #         return False

    # -------------------------------------------- PURCHASE  ORDER  ----------

    # @api.multi
    def import_purchase_order(self):
        try:
            _logger.info("inside purchase order *********************")
            company = self.env['res.users'].search(
                [('id', '=', self._uid)]).company_id
            if company.access_token:
                headers = {}
                headers['Authorization'] = 'Bearer ' + company.access_token
                headers['accept'] = 'application/json'
                headers['Content-Type'] = 'text/plain'
                if company.import_purchase_order_by_date:
                    query = "select * from purchaseorder WHERE Metadata.LastUpdatedTime >= '%s' order by Id" % (company.import_purchase_order_date)
                else:
                    query = "select * from purchaseorder WHERE Id > '%s' order by Id" % (
                        company.quickbooks_last_purchase_imported_id)
                data = requests.request('GET', company.url + str(company.realm_id) + "/query?query=" + query,
                                        headers=headers)
                if data.status_code == 200:
                    recs = []
                    parsed_data = json.loads(str(data.text))
                    if parsed_data:
                        if parsed_data.get('QueryResponse') and parsed_data.get('QueryResponse').get('PurchaseOrder'):
                            if self.import_mapping_po_field and self.import_mapping_po_id and self.env.context.get('mapping'):
                                if parsed_data.get('QueryResponse', False).get('PurchaseOrder', False):
                                    self.import_mapping_po_id.with_context({'import': True}).json_data = \
                                        parsed_data.get('QueryResponse').get('PurchaseOrder')
                                else:
                                    raise UserError("Empty data")
                                return
                            for cust in parsed_data.get('QueryResponse').get('PurchaseOrder'):

                                purchase_order = self.env['purchase.order'].search(
                                    [('quickbook_id', '=', cust.get('Id'))])

                                if not purchase_order:
                                    res_partner = self.env['res.partner'].search(
                                        [('qbo_vendor_id', '=', cust.get('VendorRef').get('value'))], limit=1)

                                    if res_partner:
                                        dict_s = {}

                                        if cust.get('Id'):
                                            dict_s[
                                                'partner_id'] = res_partner.id
                                            dict_s['quickbook_id'] = cust.get(
                                                'Id')
                                        else:
                                            dict_s['parent_id'] = cust.get(
                                                'VendorRef').get('name')

                                        if cust.get('POStatus'):
                                            dict_s['state'] = 'purchase'

                                        if cust.get('DocNumber'):
                                            dict_s['name'] = cust.get(
                                                'DocNumber')

                                        so_obj = self.env[
                                            'purchase.order'].create(dict_s)
                                        if so_obj:
                                            _logger.info(
                                                'PO Created Successfully :: %s', so_obj)

                                        for i in cust.get('Line'):
                                            if i.get('ItemBasedExpenseLineDetail'):
                                                res_product = self.env['product.product'].search(
                                                    [('qbo_product_id', '=',
                                                      i.get('ItemBasedExpenseLineDetail').get('ItemRef').get('value'))])

                                                if res_product:
                                                    dict_l = {}

                                                    dict_l.clear()
                                                    dict_l[
                                                        'order_id'] = so_obj.id
                                                    dict_l[
                                                        'product_id'] = res_product.id

                                                    if i.get('ItemBasedExpenseLineDetail').get('Qty'):
                                                        dict_l['product_qty'] = i.get('ItemBasedExpenseLineDetail').get(
                                                            'Qty')

                                                    if i.get('Id'):
                                                        dict_l['qb_id'] = int(
                                                            i.get('Id'))
                                                        dict_l[
                                                            'date_planned'] = so_obj.date_order

                                                    dict_l['product_uom'] = 1

                                                    if i.get('ItemBasedExpenseLineDetail').get('UnitPrice'):
                                                        dict_l['price_unit'] = i.get('ItemBasedExpenseLineDetail').get(
                                                            'UnitPrice')
                                                    else:
                                                        dict_l[
                                                            'price_unit'] = 0.0

                                                    if i.get('Description'):
                                                        dict_l['name'] = i.get(
                                                            'Description')
                                                    else:
                                                        dict_l['name'] = 'NA'

                                                    create_p = self.env[
                                                        'purchase.order.line'].create(dict_l)
                                                    if create_p:
                                                        company.quickbooks_last_purchase_imported_id = cust.get(
                                                            'Id')
                                                else:
                                                    raise UserError('Product ' + str(
                                                        i.get('ItemBasedExpenseLineDetail').get('ItemRef').get(
                                                            'name')) + ' is not defined in Odoo. Purchase order number :' + cust.get(
                                                        'DocNumber'))
                                else:
                                    _logger.info(
                                        "All Purchase order seems to be imported!")
                            success_form = self.env.ref(
                                'pragmatic_quickbooks_connector.import_successfull_view', False)
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
                            # raise UserError("All Purchase Orders are already imported!")
                        #                                 res_partner = self.env['res.partner'].search(
                        #                                     [('qbo_vendor_id', '=', cust.get('VendorRef').get('value'))])
                        #
                        #                                 if res_partner:
                        #
                        #                                     dict_s = {}
                        #
                        #                                     if cust.get('Id'):
                        #                                         dict_s['partner_id'] = res_partner.id
                        #                                         dict_s['quickbook_id'] = cust.get('Id')
                        # dict_s['purchase_order_id'] = cust.get('DocNumber')
                        # dict_s['state'] = 'purchase'
                        #                                     else:
                        #                                         dict_s['parent_id'] = cust.get('VendorRef').get('name')
                        #
                        #                                     if cust.get('POStatus'):
                        # if cust.get('POStatus') == 'Open':
                        # dict_s['state'] = 'draft'
                        # if cust.get('POStatus') == 'Closed':
                        #                                         dict_s['state'] = 'purchase'
                        #                                     if cust.get('DocNumber'):
                        #                                         dict_s['name'] = cust.get('DocNumber')
                        #
                        #                                     purchase_order.write(dict_s)
                        #                                     _logger.info('PO Updated Successfully..!!')
                        #
                        #                                     for i in cust.get('Line'):
                        #
                        #                                         if i.get('ItemBasedExpenseLineDetail'):
                        #
                        #                                             res_product = self.env['product.product'].search(
                        #                                                 [('qbo_product_id', '=', i.get('ItemBasedExpenseLineDetail').get('ItemRef').get(
                        #                                                     'value'))])
                        #                                             if res_product:
                        #                                                 p_order_line = self.env['purchase.order.line'].search(
                        #                                                     ['&', ('product_id', '=', res_product.id),
                        #                                                      (('order_id', '=', purchase_order.id))], limit=1)
                        #
                        #                                                 if p_order_line:
                        #
                        #                                                     dict_lp = {}
                        #
                        #                                                     if i.get('ItemBasedExpenseLineDetail').get('Qty'):
                        #                                                         quantity = i.get('ItemBasedExpenseLineDetail').get('Qty')
                        #
                        #                                                     if i.get('Id'):
                        #                                                         ol_qb_id = int(i.get('Id'))
                        #
                        #                                                     if i.get('ItemBasedExpenseLineDetail').get('UnitPrice'):
                        #                                                         sp = i.get('ItemBasedExpenseLineDetail').get('UnitPrice')
                        #                                                     else:
                        #                                                         sp = 0.0
                        #
                        #                                                     if i.get('Description'):
                        #                                                         description = i.get('Description')
                        #                                                     else:
                        #                                                         description = 'NA'
                        #
                        #                                                     create_po = self.env['purchase.order.line'].search(
                        #                                                         ['&', ('product_id', '=', res_product.id), (('order_id', '=', purchase_order.id))])
                        #                                                     if create_po:
                        #                                                         res = create_po.update({
                        #
                        #                                                             'product_id': res_product.id,
                        #                                                             'name': description,
                        #                                                             'product_qty': quantity,
                        #                                                             'date_planned': p_order_line.date_order,
                        #                                                             'qb_id': ol_qb_id,
                        #                                                             'product_uom': 1,
                        #                                                             'price_unit': sp,
                        #                                                         })
                        #
                        #                                                     if create_po:
                        #                                                         company.quickbooks_last_purchase_imported_id = cust.get('Id')
                        #
                        #                                                 else:
                        #                                                     '''CREATE NEW PURCHSE ORDER LINES IN EXISTING PURCHASE ORDER'''
                        #
                        #                                                     dict_l = {}
                        #                                                     dict_l.clear()
                        #                                                     dict_l['order_id'] = purchase_order.id
                        #                                                     dict_l['product_id'] = res_product.id
                        #
                        #                                                     if i.get('ItemBasedExpenseLineDetail').get('Qty'):
                        #                                                         dict_l['product_qty'] = i.get('ItemBasedExpenseLineDetail').get('Qty')
                        #
                        #                                                     if i.get('Id'):
                        #                                                         dict_l['qb_id'] = int(i.get('Id'))
                        #                                                         dict_l['date_planned'] = purchase_order.date_order
                        #
                        #                                                     dict_l['product_uom'] = 1
                        #
                        #                                                     if i.get('ItemBasedExpenseLineDetail').get('UnitPrice'):
                        #                                                         dict_l['price_unit'] = i.get('ItemBasedExpenseLineDetail').get('UnitPrice')
                        #                                                     else:
                        #                                                         dict_l['price_unit'] = 0.0
                        #
                        #                                                     if i.get('Description'):
                        #                                                         dict_l['name'] = i.get('Description')
                        #                                                     else:
                        #                                                         dict_l['name'] = 'NA'
                        #
                        #                                                     create_p = self.env['purchase.order.line'].create(dict_l)
                        #                                                     if create_p:
                        #                                                         company.quickbooks_last_purchase_imported_id = cust.get('Id')

                        else:
                            raise UserError(
                                "It seems that all of the Purchase Orders are already imported!")
        except Exception as e:
            raise UserError(e)
    # ---------------------------------VENDOR BILLS---------------------------

    # @api.multi
    def import_vendor_bill_1(self):
        _logger.info("inside vendor bill ****************************")
        company = self.env['res.users'].search([('id', '=', self._uid)]).company_id
        if company.access_token:
            headers = {}
            headers['Authorization'] = 'Bearer ' + self.access_token
            headers['accept'] = 'application/json'
            headers['Content-Type'] = 'text/plain'
            if company.import_bills_by_date:
                query = "select * from bill WHERE Metadata.LastUpdatedTime >= '%s' order by Id" % (company.import_bills_date)
            else:
                query = "select * from bill WHERE Id > '%s' order by Id" % (
                    company.quickbooks_last_vendor_bill_imported_id)

            data = requests.request('GET', self.url + str(self.realm_id) + "/query?query=" + query,
                                    headers=headers)
            if data.status_code == 200:
                _logger.info("Vendor bill data is -------------------->{}".format(data.text))
                recs = []
                parsed_data = json.loads(str(data.text))
                if parsed_data:
                    _logger.info("Parsed data for vendor bill is -------------> {}".format(parsed_data))
                    if parsed_data.get('QueryResponse') and parsed_data.get('QueryResponse').get('Bill'):

                        for cust in parsed_data.get('QueryResponse').get('Bill'):
                            # searching sales order
                            line_present = self.check_if_lines_present_vendor_bill(cust)
                            _logger.info('ORDER LINES NOT PRESENT IN VENDOR BILL :: %s', line_present)
                            if not line_present:
                                continue

                            bill = self.env['account.move'].search(
                                [('qbo_invoice_id', '=', cust.get('Id'))])
                            _logger.info("Bill search is --------------> {}".format(bill))
                            if not bill:

                                _logger.info("No bill.")
                                _logger.info(
                                    "Vendor value is -----------------> {}".format(cust.get('VendorRef').get('value')))
                                res_partner = self.env['res.partner'].search(
                                    [('qbo_vendor_id', '=', cust.get('VendorRef').get('value'))], limit=1)
                                _logger.info("Res partner is -------------------> {}".format(res_partner))
                                if res_partner:
                                    dict_i = {}
                                    if cust.get('Id'):
                                        dict_i['partner_id'] = res_partner.id

                                        dict_i['qbo_invoice_id'] = cust.get('Id')

                                        dict_i['company_id'] = self.id

                                        dict_i['type'] = 'in_invoice'

                                    if cust.get('CurrencyRef'):
                                        if cust.get('CurrencyRef').get('value'):
                                            currency = self.env['res.currency'].search(
                                                [('name', '=', cust.get('CurrencyRef').get('value'))], limit=1)
                                            dict_i['currency_id'] = currency.id

                                    if res_partner.customer_rank:
                                        sale = self.env['account.journal'].search([('type', 'in', ['sale', 'cash'])],
                                                                                  limit=1)
                                        if sale:
                                            dict_i['journal_id'] = sale.id
                                            _logger.info("Journal was attached..")
                                        else:
                                            _logger.info("No Journal was found..")
                                    if res_partner.supplier_rank:
                                        purchase = self.env['account.journal'].search(
                                            [('type', 'in', ['purchase', 'cash'])],
                                            limit=1)
                                        if purchase:
                                            dict_i['journal_id'] = purchase.id
                                            _logger.info("Journal attached..")
                                        else:
                                            _logger.info("No Journal was found...")

                                        # dict_i['journal_id'] = 1
                                        dict_i['reference_type'] = ''
                                    # if cust.get('DocNumber'):
                                    #     dict_i['number'] = cust.get('DocNumber')
                                    if cust.get('Balance'):
                                        dict_i['state'] = 'draft'
                                        # dict_i['residual'] = cust.get('Balance')
                                        # dict_i['residual_signed'] = cust.get('Balance')
                                        dict_i['amount_residual'] = cust.get('Balance')
                                        dict_i['amount_residual_signed'] = cust.get('Balance')
                                    else:
                                        dict_i['amount_residual'] = 0.0
                                        dict_i['amount_residual_signed'] = 0.0

                                    if cust.get('DueDate'):
                                        dict_i['invoice_date_due'] = cust.get('DueDate')
                                    if cust.get('TxnDate'):
                                        dict_i['invoice_date'] = cust.get('TxnDate')

                                    ele_in_list = len(cust.get('Line'))
                                    dict_t = cust.get('Line')[ele_in_list - 1]
                                    #                                     if dict_t.get('DiscountLineDetail'):
                                    #                                         dict_i['check'] = True
                                    #
                                    #                                         if dict_t.get('DiscountLineDetail').get('DiscountPercent'):
                                    #                                             dict_i['discount_type'] = 'percentage'
                                    #                                             dict_i['amount'] = dict_t.get('DiscountLineDetail').get('DiscountPercent')
                                    #                                             dict_i['percentage_amt'] = dict_t.get('Amount')
                                    #                                         else:
                                    #                                             dict_i['discount_type'] = 'value'
                                    #                                             dict_i['amount'] = dict_t.get('Amount')

                                    # if cust.get('TotalTax'):
                                    #     dict_i['amount_tax'] = cust.get('TotalTax')

                                    if cust.get('TotalAmt'):
                                        dict_i['amount_total'] = cust.get('TotalAmt')
                                    _logger.info("Dictionary for creation of vendor bill is ---> {}".format(dict_i))
                                    invoice_obj = self.env['account.move'].create(dict_i)
                                    _logger.info("Invoice object is --------> {}".format(invoice_obj))
                                    if invoice_obj:
                                        _logger.info('Vendor Bill Created Successfully :: %s', cust.get('Id'))

                                    custom_tax_id = None

                                    for i in cust.get('Line'):
                                        dict_ol = {}

                                        if i.get('ItemBasedExpenseLineDetail'):
                                            res_product = self.env['product.product'].search([('qbo_product_id', '=',
                                                                                               i.get(
                                                                                                   'ItemBasedExpenseLineDetail').get(
                                                                                                   'ItemRef').get(
                                                                                                   'value'))])
                                            if res_product:
                                                dict_ol.clear()
                                                dict_ol['move_id'] = invoice_obj.id
                                                dict_ol['product_id'] = res_product.id

                                                if i.get('Id'):
                                                    dict_ol['qb_id'] = int(i.get('Id'))
                                                    dict_ol['tax_ids'] = None

                                                if i.get('ItemBasedExpenseLineDetail').get('Qty'):
                                                    dict_ol['quantity'] = i.get('ItemBasedExpenseLineDetail').get('Qty')

                                                if i.get('ItemBasedExpenseLineDetail').get('UnitPrice'):
                                                    dict_ol['price_unit'] = float(
                                                        i.get('ItemBasedExpenseLineDetail').get('UnitPrice'))
                                                else:
                                                    if not i.get('ItemBasedExpenseLineDetail').get('Qty'):
                                                        dict_ol['quantity'] = 1
                                                        dict_ol['price_unit'] = float(
                                                            i.get('Amount'))
                                                    else:
                                                        dict_ol['price_unit'] = 0.0

                                                if i.get('Description'):
                                                    dict_ol['name'] = i.get('Description')
                                                else:
                                                    dict_ol['name'] = 'NA'
                                                if res_product.property_account_expense_id:
                                                    dict_ol['account_id'] = res_product.property_account_expense_id.id
                                                else:
                                                    dict_ol[
                                                        'account_id'] = res_product.categ_id.property_account_expense_categ_id.id
                                                _logger.info(
                                                    "Creation for invoice lines ---------------> {}".format(dict_ol))
                                                create_p = self.env['account.move.line'].create(dict_ol)
                                                _logger.info("After creation ---------->{}".format(create_p))
                                                if create_p:
                                                    self.quickbooks_last_vendor_bill_imported_id = cust.get('Id')

                                        if i.get('AccountBasedExpenseLineDetail'):
                                            dict_al = {}
                                            dict_al['move_id'] = invoice_obj.id
                                            if i.get('Id'):
                                                dict_al['qb_id'] = int(i.get('Id'))
                                                dict_al['tax_ids'] = None
                                                dict_al['quantity'] = 1

                                            if i.get('Amount'):
                                                dict_al['price_unit'] = float(i.get('Amount'))
                                            else:
                                                dict_al['price_unit'] = 0.0

                                            if i.get('Description'):
                                                dict_al['name'] = i.get('Description')
                                            else:
                                                dict_al['name'] = 'NA'

                                            if i.get('AccountBasedExpenseLineDetail').get('AccountRef'):
                                                account = self.env['account.account'].search([('qbo_id', '=', i.get(
                                                    'AccountBasedExpenseLineDetail').get('AccountRef').get('value'))])
                                                dict_al['account_id'] = account.id

                                            create_p = self.env['account.move.line'].create(dict_al)
                                            if create_p:
                                                company.quickbooks_last_vendor_bill_imported_id = cust.get('Id')
                                    if cust.get('Balance') == 0:
                                        if invoice_obj.state == 'draft':
                                            invoice_obj.action_invoice_open()
                                            invoice_obj.write({
                                                'amount_residual': cust.get('Balance'),
                                                'amount_residual_signed': cust.get('Balance')
                                            })
                            else:
                                _logger.info("Bill exists!!!")
                                res_partner = self.env['res.partner'].search(
                                    [('qbo_vendor_id', '=', cust.get('VendorRef').get('value'))], limit=1)
                                _logger.info("Partner is -----------> {}".format(res_partner))
                                if res_partner:
                                    dict_i = {}

                                    if cust.get('Id'):
                                        dict_i['partner_id'] = res_partner.id
                                        dict_i['qbo_invoice_id'] = cust.get('Id')
                                        dict_i['company_id'] = self.id

                                        dict_i['type'] = 'in_invoice'
                                    if cust.get('CurrencyRef'):
                                        if cust.get('CurrencyRef').get('value'):
                                            currency = self.env['res.currency'].search(
                                                [('name', '=', cust.get('CurrencyRef').get('value'))], limit=1)
                                            dict_i['currency_id'] = currency.id

                                    if res_partner.customer_rank:
                                        sale = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
                                        if sale:
                                            dict_i['journal_id'] = sale.id
                                    if res_partner.supplier_rank:
                                        purchase = self.env['account.journal'].search([('type', '=', 'purchase')],
                                                                                      limit=1)
                                        if purchase:
                                            dict_i['journal_id'] = purchase.id

                                        dict_i['reference_type'] = ''
                                    if cust.get('TotalAmt'):
                                        dict_i['total'] = cust.get('TotalAmt')
                                    # if cust.get('DocNumber'):
                                    #     dict_i['number'] = cust.get('DocNumber')

                                    # if cust.get('Balance'):
                                    #     if cust.get('Balance') != 0.0:
                                    # if not bill.payments_widget:
                                    #     dict_i['state'] = 'draft'
                                    # else:
                                    #     print"\n\npayments_widget :------------------> ",bill,bill.payments_widget
                                    # else:
                                    if not cust.get('Balance'):
                                        if bill.state == 'draft':
                                            bill.action_invoice_open()
                                        # dict_i['state'] = 'paid'

                                    if cust.get('Balance'):
                                        dict_i['amount_residual'] = cust.get('Balance')
                                        dict_i['amount_residual_signed'] = cust.get('Balance')
                                    else:
                                        dict_i['amount_residual'] = 0.0
                                        dict_i['amount_residual_signed'] = 0.0

                                    if cust.get('DueDate'):
                                        dict_i['invoice_date_due'] = cust.get('DueDate')
                                    if cust.get('TxnDate'):
                                        dict_i['invoice_date'] = cust.get('TxnDate')

                                    ele_in_list = len(cust.get('Line'))
                                    dict_t = cust.get('Line')[ele_in_list - 1]
                                    #                                     if dict_t.get('DiscountLineDetail'):
                                    #                                         dict_i['check'] = True
                                    #
                                    #                                         if dict_t.get('DiscountLineDetail').get('DiscountPercent'):
                                    #                                             dict_i['discount_type'] = 'percentage'
                                    #                                             dict_i['amount'] = dict_t.get('DiscountLineDetail').get('DiscountPercent')
                                    #                                             dict_i['percentage_amt'] = dict_t.get('Amount')
                                    #                                         else:
                                    #                                             dict_i['discount_type'] = 'value'
                                    #                                             dict_i['amount'] = dict_t.get('Amount')

                                    if cust.get('Amount'):
                                        dict_i['amount_total'] = cust.get('Amount')
                                    write_inv = bill.write(dict_i)
                                    if write_inv:
                                        _logger.info('Vendor Bill Updated Successfully :: %s', cust.get('Id'))

                                    bill._compute_residual()
                                    for i in cust.get('Line'):

                                        if i.get('ItemBasedExpenseLineDetail'):
                                            res_product = self.env['product.product'].search([('qbo_product_id', '=',
                                                                                               i.get(
                                                                                                   'ItemBasedExpenseLineDetail').get(
                                                                                                   'ItemRef').get(
                                                                                                   'value'))])
                                            if res_product:
                                                p_order_line = self.env['account.move.line'].search(
                                                    ['&', ('product_id', '=', res_product.id),
                                                     (('move_id', '=', bill.id))])

                                                if p_order_line:

                                                    if i.get('Id'):
                                                        ol_qb_id = int(i.get('Id'))

                                                    if i.get('ItemBasedExpenseLineDetail').get('Qty'):
                                                        qty = i.get('ItemBasedExpenseLineDetail').get('Qty')

                                                    if i.get('ItemBasedExpenseLineDetail').get('UnitPrice'):
                                                        sp = float(
                                                            i.get('ItemBasedExpenseLineDetail').get('UnitPrice'))
                                                    else:
                                                        if not i.get('ItemBasedExpenseLineDetail').get('Qty'):
                                                            qty = 1
                                                            sp = float(
                                                                i.get('Amount'))
                                                        else:
                                                            sp = 0.0

                                                    if i.get('Description'):
                                                        description = i.get('Description')
                                                    else:
                                                        description = 'NA'

                                                    # create_p = self.env['account.move.line'].write(dict_ol)

                                                    create_iv = self.env['account.move.line'].search(
                                                        ['&', ('qb_id', '=', int(i.get('Id'))),
                                                         (('move_id', '=', bill.id))])
                                                    if create_iv:
                                                        data_dict = {

                                                            'product_id': res_product.id,
                                                            'name': description,
                                                            'quantity': qty,
                                                            'qb_id': ol_qb_id,
                                                            'price_unit': sp,
                                                            'tax_ids': None,
                                                        }
                                                        if res_product.property_account_expense_id:
                                                            _logger.info("ATTACHING product expense account")
                                                            data_dict.update({
                                                                                 'account_id': res_product.property_account_expense_id.id})
                                                        else:
                                                            _logger.info("ATTACHING category expense account")
                                                            data_dict.update({
                                                                                 'account_id': res_product.categ_id.property_account_expense_categ_id.id})
                                                        res = create_iv.write(data_dict)

                                                    # if discount_amt > 0:
                                                    #     create_iv.write({
                                                    #         'discount': discount_amt
                                                    #     })

                                                    if create_iv:
                                                        _logger.info("Invoice created...")
                                                        company.quickbooks_last_vendor_bill_imported_id = cust.get('Id')

                                                else:
                                                    dict_ol = {}

                                                    dict_ol.clear()
                                                    dict_ol['move_id'] = bill.id
                                                    dict_ol['product_id'] = res_product.id

                                                    if i.get('Id'):
                                                        dict_ol['qb_id'] = int(i.get('Id'))
                                                        dict_ol['tax_ids'] = None

                                                    if i.get('ItemBasedExpenseLineDetail').get('Qty'):
                                                        dict_ol['quantity'] = i.get('ItemBasedExpenseLineDetail').get(
                                                            'Qty')

                                                    if i.get('ItemBasedExpenseLineDetail').get('UnitPrice'):
                                                        dict_ol['price_unit'] = float(
                                                            i.get('ItemBasedExpenseLineDetail').get('UnitPrice'))
                                                    else:
                                                        if not i.get('ItemBasedExpenseLineDetail').get('Qty'):
                                                            dict_ol['quantity'] = 1
                                                            dict_ol['price_unit'] = float(
                                                                i.get('Amount'))
                                                        else:
                                                            dict_ol['price_unit'] = 0.0

                                                    # dict_ol['date_due'] = cust.get('TxnDate')

                                                    if i.get('Description'):
                                                        dict_ol['name'] = i.get('Description')
                                                    else:
                                                        dict_ol['name'] = 'NA'

                                                    if res_product.property_account_expense_id:
                                                        dict_ol[
                                                            'account_id'] = res_product.property_account_expense_id.id
                                                        _logger.info("Attached from product ")
                                                    else:
                                                        dict_ol[
                                                            'account_id'] = res_product.categ_id.property_account_expense_categ_id.id

                                                    create_p = self.env['account.move.line'].create(dict_ol)
                                                    if create_p:
                                                        company.quickbooks_last_vendor_bill_imported_id = cust.get('Id')
                                        if i.get('AccountBasedExpenseLineDetail'):
                                            account_account = self.env['account.account'].search([('qbo_id', '=',
                                                                                                   i.get(
                                                                                                       'AccountBasedExpenseLineDetail').get(
                                                                                                       'AccountRef').get(
                                                                                                       'value'))])
                                            if account_account:
                                                a_order_line = self.env['account.move.line'].search(
                                                    ['&', ('account_id', '=', account_account.id),
                                                     (('move_id', '=', bill.id))])
                                                dict_al = {}
                                                if i.get('Id'):
                                                    dict_al['qb_id'] = int(i.get('Id'))
                                                    dict_al['tax_ids'] = None
                                                    dict_al['quantity'] = 1

                                                if i.get('Amount'):
                                                    dict_al['price_unit'] = float(i.get('Amount'))
                                                else:
                                                    dict_al['price_unit'] = 0.0

                                                if i.get('Description'):
                                                    dict_al['name'] = i.get('Description')
                                                else:
                                                    dict_al['name'] = 'NA'

                                                if i.get('AccountBasedExpenseLineDetail').get('AccountRef'):
                                                    account = self.env['account.account'].search([('qbo_id', '=', i.get(
                                                        'AccountBasedExpenseLineDetail').get('AccountRef').get(
                                                        'value'))])
                                                    if account:
                                                        dict_al['account_id'] = account.id
                                                        _logger.info(
                                                            "Attaching account id from AccountBasedExpenseLineDetail")
                                                    else:
                                                        _logger.error(
                                                            "Unable to fetch Account Based Expense Line Detail")

                                                if not a_order_line:
                                                    dict_al['move_id'] = bill.id
                                                    _logger.info(
                                                        "Account invoice line dict is ---------> {}".format(dict_al))
                                                    create_p = self.env['account.move.line'].create(dict_al)
                                                    if create_p:
                                                        _logger.info(
                                                            "Creation of invoice lines of vendor bills --------------- {}".format(
                                                                create_p))
                                                        company.quickbooks_last_vendor_bill_imported_id = cust.get('Id')
                                                else:
                                                    _logger.info("Redirecting else part account.move.line")
                                                    create_p = self.env['account.move.line'].write(dict_al)
                                                    if create_p:
                                                        _logger.info(
                                                            "Updation  of invoice lines of vendor bills --------------- {}".format(
                                                                create_p))

                                                        company.quickbooks_last_vendor_bill_imported_id = cust.get('Id')
            else:
                raise UserError("Empty Data")
                _logger.warning(_('Empty data'))

    ###################IMPORT CREDIT MEMO###########################################
    # @api.multi
    def import_credit_memo_1(self):
        company = self.env['res.users'].search([('id', '=', self._uid)]).company_id

        if company.access_token:
            headers = {}
            headers['Authorization'] = 'Bearer ' + company.access_token
            headers['accept'] = 'application/json'
            headers['Content-Type'] = 'text/plain'
            if company.import_credit_memo_by_date:
                query = "select * from CreditMemo WHERE Metadata.LastUpdatedTime >= '%s' order by Id" % (company.import_credit_memo_date)
            else:
                query = "select * from CreditMemo WHERE Id > '%s' order by Id" % (
                    company.quickbooks_last_credit_note_imported_id)

            data = requests.request('GET', self.url + str(self.realm_id) + "/query?query=" + query,
                                    headers=headers)
            if data.status_code == 200:
                recs = []
                parsed_data = json.loads(str(data.text))
                count = 0

                if parsed_data:
                    if parsed_data.get('QueryResponse') and parsed_data.get('QueryResponse').get('CreditMemo'):
                        for cust in parsed_data.get('QueryResponse').get('CreditMemo'):
                            return_val = self.check_account_id(cust)
                            if return_val:
                                line_present = self.check_if_lines_present(cust)
                                _logger.info('ORDER LINES PRESENT IN INVOICE :: %s', line_present)
                                if not line_present:
                                    continue

                                count = count + 1
                                account_invoice = self.env['account.move'].search(
                                    [('qbo_invoice_id', '=', cust.get('Id'))])
                                _logger.info("ACC invoice is -----> {}".format(account_invoice))
                                if not account_invoice:

                                    res_partner = self.env['res.partner'].search(
                                        [('qbo_customer_id', '=', cust.get('CustomerRef').get('value'))])
                                    _logger.info(
                                        "Partner is ---> {}".format(res_partner))
                                    if res_partner:
                                        dict_i = {}

                                        if cust.get('Id'):
                                            dict_i[
                                                'partner_id'] = res_partner.id
                                            dict_i['qbo_invoice_id'] = cust.get(
                                                'Id')
                                            dict_i['type'] = 'out_refund'

                                            # dict_i['name'] = "INVOICE"
                                            # dict_i['account_id'] = 0
                                            dict_i['company_id'] = self.id

                                        if cust.get('CurrencyRef'):
                                            if cust.get('CurrencyRef').get('value'):
                                                currency = self.env['res.currency'].search(
                                                    [('name', '=', cust.get('CurrencyRef').get('value'))], limit=1)
                                                dict_i[
                                                    'currency_id'] = currency.id

                                        if res_partner.customer_rank:
                                            sale = self.env['account.journal'].search(
                                                [('type', '=', 'sale')], limit=1)
                                            if sale:
                                                dict_i['journal_id'] = sale.id
                                            else:
                                                sale = self.env['account.journal'].search([('type', '=', 'bank')],
                                                                                          limit=1)
                                                if sale:
                                                    dict_i[
                                                        'journal_id'] = sale.id
                                        if res_partner.supplier_rank:
                                            purchase = self.env['account.journal'].search([('type', '=', 'purchase')],
                                                                                          limit=1)
                                            if purchase:
                                                dict_i[
                                                    'journal_id'] = purchase.id
                                            else:
                                                purchase = self.env['account.journal'].search([('type', '=', 'bank')],
                                                                                              limit=1)
                                                if purchase:
                                                    dict_i[
                                                        'journal_id'] = purchase.id

                                            # dict_i['journal_id'] = 1
                                            dict_i['reference_type'] = ''

                                        if cust.get('DocNumber'):
                                            dict_i['name'] = cust.get(
                                                'DocNumber')
                                            # dict_i['number'] = cust.get('DocNumber')

                                        if cust.get('Balance'):
                                            dict_i['state'] = 'draft'
                                            dict_i['amount_residual'] = cust.get(
                                                'Balance')
                                            dict_i['amount_residual_signed'] = cust.get(
                                                'Balance')
                                            # dict_i['residual'] = cust.get('Balance')
                                            # dict_i['residual_signed'] = cust.get('Balance')
                                        else:
                                            dict_i['amount_residual'] = 0.0
                                            dict_i[
                                                'amount_residual_signed'] = 0.0

                                        if cust.get('DueDate'):
                                            dict_i['invoice_date_due'] = cust.get(
                                                'DueDate')
                                        if cust.get('TxnDate'):
                                            dict_i['invoice_date'] = cust.get(
                                                'TxnDate')

                                        ele_in_list = len(cust.get('Line'))
                                        #       ele_in_list)
                                        dict_t = cust.get(
                                            'Line')[ele_in_list - 1]
                                        #                                         if dict_t.get('DiscountLineDetail'):
                                        #                                             dict_i['check'] = True
                                        #
                                        #                                             if dict_t.get('DiscountLineDetail').get('DiscountPercent'):
                                        #                                                 dict_i['discount_type'] = 'percentage'
                                        #                                                 dict_i['amount'] = dict_t.get('DiscountLineDetail').get('DiscountPercent')
                                        #                                                 dict_i['percentage_amt'] = dict_t.get('Amount')
                                        #                                             else:
                                        #                                                 dict_i['discount_type'] = 'value'
                                        #                                                 dict_i['amount'] = dict_t.get('Amount')

                                        # if cust.get('TotalTax'):
                                        #     dict_i['amount_tax'] = cust.get('TotalTax')
                                        #
                                        if cust.get('TotalAmt'):
                                            dict_i['total'] = cust.get(
                                                'TotalAmt')

                                        _logger.info(
                                            "Dictionary for creation is ---> {}".format(dict_i))
                                        invoice_obj = self.env[
                                            'account.move'].create(dict_i)
                                        _logger.info(
                                            "Invoice obj is -----> {}".format(invoice_obj))
                                        if invoice_obj:
                                            # self._cr.commit()
                                            _logger.info(
                                                'Credit Memo  Created Successfully..!! :: %s', invoice_obj)

                                        # if invoice_obj:
                                        #     tax_call = invoice_obj._onchange_invoice_line_ids()
                                        #     print("TAX CALL----------->",tax_call)
                                        custom_tax_id = None
                                        # print"\n\n\n\nLINE :
                                        # -----------------> ",
                                        # cust.get('Line')

                                        for i in cust.get('Line'):
                                            dict_ol = {}
                                            if cust.get('TxnTaxDetail').get('TxnTaxCodeRef'):
                                                if cust.get('TxnTaxDetail').get('TxnTaxCodeRef').get('value'):

                                                    qb_tax_id = cust.get('TxnTaxDetail').get('TxnTaxCodeRef').get(
                                                        'value')
                                                    record = self.env[
                                                        'account.tax']
                                                    tax = record.search(
                                                        [('qbo_tax_id', '=', qb_tax_id)])
                                                    if tax:
                                                        custom_tax_id = [
                                                            (6, 0, [tax.id])]
                                                        _logger.info(
                                                            "TAX ATTACHED {}".format(tax.id))
                                                    else:
                                                        custom_tax_id = None

                                            if 'SalesItemLineDetail' in i and i.get('SalesItemLineDetail'):
                                                res_product = self.env['product.product'].search(
                                                    [('qbo_product_id', '=',
                                                      i.get('SalesItemLineDetail').get('ItemRef').get('value'))])
                                                if res_product:

                                                    dict_ol.clear()
                                                    dict_ol[
                                                        'move_id'] = invoice_obj.id

                                                    dict_ol[
                                                        'product_id'] = res_product.id

                                                    if i.get('Id'):
                                                        dict_ol['qb_id'] = int(
                                                            i.get('Id'))

                                                    # ---------------------------TAX--------------------------------------
                                                    if i.get('SalesItemLineDetail').get('TaxCodeRef'):

                                                        tax_val = i.get('SalesItemLineDetail').get(
                                                            'TaxCodeRef').get(
                                                            'value')
                                                        if tax_val == 'TAX':

                                                            dict_ol[
                                                                'tax_ids'] = custom_tax_id
                                                        else:
                                                            dict_ol[
                                                                'tax_ids'] = None

                                                    if i.get('SalesItemLineDetail').get('Qty'):
                                                        dict_ol['quantity'] = i.get(
                                                            'SalesItemLineDetail').get('Qty')

                                                    if i.get('SalesItemLineDetail').get('UnitPrice'):
                                                        dict_ol['price_unit'] = float(
                                                            i.get('SalesItemLineDetail').get('UnitPrice'))
                                                    else:
                                                        if not i.get('SalesItemLineDetail').get('Qty'):
                                                            dict_ol[
                                                                'quantity'] = 1
                                                            dict_ol['price_unit'] = float(
                                                                i.get('Amount'))
                                                        else:
                                                            dict_ol[
                                                                'price_unit'] = 0

                                                    if 'Description' in i and i.get('Description'):
                                                        dict_ol['name'] = i.get(
                                                            'Description')
                                                    else:
                                                        dict_ol['name'] = 'NA'

                                                    if res_product.property_account_income_id:
                                                        dict_ol[
                                                            'account_id'] = res_product.property_account_income_id.id
                                                        _logger.info(
                                                            "PRODUCT has income account set")
                                                    else:
                                                        dict_ol[
                                                            'account_id'] = res_product.categ_id.property_account_income_categ_id.id
                                                        _logger.info(
                                                            "No Income account was set, taking from product category..")
                                                    if 'account_id' in dict_ol:
                                                        _logger.info(
                                                            "\n\n Invoice Line is  ---> {}".format(dict_ol))
                                                        create_p = self.env[
                                                            'account.move.line'].create(dict_ol)
                                                        if create_p:
                                                            self._cr.commit()
                                                            _logger.info(
                                                                "Invoice Line Committed!!!")
                                                            create_p.move_id._onchange_invoice_line_ids()
                                                            company.quickbooks_last_invoice_imported_id = cust.get(
                                                                'Id')
                                                        else:
                                                            _logger.error(
                                                                "Invoice line was not created.")
                                                    else:
                                                        _logger.error(
                                                            "NO ACCOUNT ID WAS ATTACHED !")
                                        if cust.get('Balance') == 0:
                                            if invoice_obj.state == 'draft':
                                                invoice_obj.action_invoice_open()
                                                if cust.get('DocNumber'):
                                                    invoice_obj.write({'name': cust.get('DocNumber'),
                                                                       'amount_residual': cust.get('Balance'),
                                                                       'amount_residual_signed': cust.get('Balance')})

                                else:
                                    res_partner = self.env['res.partner'].search(
                                        [('qbo_customer_id', '=', cust.get('CustomerRef').get('value'))])

                                    if res_partner:
                                        dict_i = {}

                                        if 'Id' in cust and cust.get('Id'):
                                            dict_i[
                                                'partner_id'] = res_partner.id
                                            dict_i['qbo_invoice_id'] = cust.get(
                                                'Id')
                                            # dict_i['name'] = "INVOICE"
                                            # dict_i['account_id'] = 0
                                            dict_i['company_id'] = self.id
                                            # dict_i['type'] = 'out_refund'

                                        if 'CurrencyRef' in cust and cust.get('CurrencyRef'):
                                            if cust.get('CurrencyRef').get('value'):
                                                currency = self.env['res.currency'].search(
                                                    [('name', '=', cust.get('CurrencyRef').get('value'))], limit=1)
                                                dict_i[
                                                    'currency_id'] = currency.id

                                        if res_partner.customer_rank:
                                            sale = self.env['account.journal'].search([('type', '=', 'sale')],
                                                                                      limit=1)
                                            if sale:
                                                dict_i['journal_id'] = sale.id
                                        if res_partner.supplier_rank:
                                            purchase = self.env['account.journal'].search(
                                                [('type', '=', 'purchase')],
                                                limit=1)
                                            if purchase:
                                                dict_i[
                                                    'journal_id'] = purchase.id

                                            # dict_i['journal_id'] = 1
                                            dict_i['reference_type'] = ''

                                        if 'TotalAmt' in cust and cust.get('TotalAmt'):
                                            dict_i['total'] = cust.get(
                                                'TotalAmt')
                                        if 'DocNumber' in cust and cust.get('DocNumber'):
                                            dict_i['name'] = cust.get(
                                                'DocNumber')
                                            # dict_i['number'] = cust.get('DocNumber')

                                        if 'Balance' in cust and cust.get('Balance'):
                                            # if not account_invoice.payments_widget:
                                            #     dict_i['state'] = 'draft'
                                            # else:
                                            # print"payments_widget
                                            # :------------------>
                                            # ",account_invoice,account_invoice.payments_widget
                                            dict_i['amount_residual'] = cust.get(
                                                'Balance')
                                            dict_i['amount_residual_signed'] = cust.get(
                                                'Balance')
                                            # dict_i['residual'] = cust.get('Balance')
                                            # dict_i['residual_signed'] = cust.get('Balance')
                                        else:
                                            # dict_i['state'] = 'paid'
                                            dict_i['amount_residual'] = 0.0
                                            dict_i[
                                                'amount_residual_signed'] = 0.0
                                            # dict_i['residual'] = 0.0
                                            # dict_i['residual_signed'] = 0.0
                                            if account_invoice.state == 'draft':
                                                account_invoice.action_invoice_open()

                                        if 'DueDate' in cust and cust.get('DueDate'):
                                            dict_i['invoice_date_due'] = cust.get(
                                                'DueDate')
                                        if 'TxnDate' in cust and cust.get('TxnDate'):
                                            dict_i['invoice_date'] = cust.get(
                                                'TxnDate')

                                        ele_in_list = len(cust.get('Line'))
                                        dict_t = cust.get(
                                            'Line')[ele_in_list - 1]
                                        #                                         if dict_t.get('DiscountLineDetail'):
                                        #                                             dict_i['check'] = True
                                        #
                                        #                                             if dict_t.get('DiscountLineDetail').get('DiscountPercent'):
                                        #                                                 dict_i['discount_type'] = 'percentage'
                                        #                                                 dict_i['amount'] = dict_t.get('DiscountLineDetail').get('DiscountPercent')
                                        #                                                 dict_i['percentage_amt'] = dict_t.get('Amount')
                                        #                                             else:
                                        #                                                 dict_i['discount_type'] = 'value'
                                        #                                                 dict_i['amount'] = dict_t.get('Amount')

                                        write_inv = account_invoice.write(
                                            dict_i)
                                        if write_inv:
                                            _logger.info(
                                                'Credit Memo Updated Successfully..!! :: %s', cust.get('Id'))

                                        account_invoice._onchange_invoice_line_ids()

                                        custom_tax_id_id = None
                                        custom_tax_id = None
                                        # print"\n\n\n\nLINE :
                                        # -----------------> ",
                                        # cust.get('Line')

                                        for i in cust.get('Line'):
                                            if 'TxnTaxDetail' in cust and cust.get('TxnTaxDetail'):
                                                if 'TxnTaxCodeRef' in cust.get('TxnTaxDetail') and cust.get('TxnTaxDetail').get('TxnTaxCodeRef'):
                                                    if cust.get('TxnTaxDetail').get('TxnTaxCodeRef').get('value'):

                                                        qb_tax_id = cust.get('TxnTaxDetail').get('TxnTaxCodeRef').get(
                                                            'value')
                                                        record = self.env[
                                                            'account.tax']
                                                        tax = record.search(
                                                            [('qbo_tax_id', '=', qb_tax_id)])
                                                        if tax:
                                                            custom_tax_id = [
                                                                (6, 0, [tax.id])]
                                                        else:
                                                            custom_tax_id = None

                                            if 'SalesItemLineDetail' in i and i.get('SalesItemLineDetail'):
                                                res_product = self.env['product.product'].search(
                                                    [('qbo_product_id', '=',
                                                      i.get('SalesItemLineDetail').get('ItemRef').get('value'))])

                                                if res_product:
                                                    p_order_line = self.env['account.move.line'].search(
                                                        ['&', ('product_id', '=', res_product.id),
                                                         (('move_id', '=', account_invoice.id))])

                                                    if p_order_line:

                                                        if i.get('Id'):
                                                            ol_qb_id = int(
                                                                i.get('Id'))

                                                        if i.get('SalesItemLineDetail').get('Qty'):
                                                            qty = i.get(
                                                                'SalesItemLineDetail').get('Qty')
                                                        else:
                                                            qty = 0

                                                        if i.get('SalesItemLineDetail').get('UnitPrice'):
                                                            sp = float(
                                                                i.get('SalesItemLineDetail').get('UnitPrice'))
                                                        else:
                                                            if not i.get('SalesItemLineDetail').get('Qty'):
                                                                qty = 1
                                                                sp = float(
                                                                    i.get('Amount'))
                                                            else:
                                                                sp = 0.0

                                                        if i.get('SalesItemLineDetail').get('TaxCodeRef'):

                                                            # print("TAX AVAILABLE : ",
                                                            #       i.get('SalesItemLineDetail').get('TaxCodeRef').get(
                                                            #           'value'))
                                                            tax_val = i.get('SalesItemLineDetail').get(
                                                                'TaxCodeRef').get(
                                                                'value')
                                                            if tax_val == 'TAX':

                                                                custom_tax_id_id = custom_tax_id
                                                            else:
                                                                custom_tax_id_id = None

                                                        if i.get('Description'):
                                                            description = i.get(
                                                                'Description')
                                                        else:
                                                            description = 'NA'

                                                        income_id = None

                                                        if res_product.property_account_income_id.id:
                                                            income_id = res_product.property_account_income_id.id
                                                        else:
                                                            income_id = res_product.categ_id.property_account_income_categ_id.id

                                                        # create_p = self.env['account.move.line'].write(dict_ol)

                                                        create_iv = self.env['account.move.line'].search(
                                                            ['&', ('qb_id', '=', int(i.get('Id'))),
                                                             (('move_id', '=', account_invoice.id))])
                                                        # search([['qb_id', '=', i.get('Id')]])
                                                        if create_iv:
                                                            res = create_iv.write({

                                                                'product_id': res_product.id,
                                                                'name': description,
                                                                'quantity': qty,
                                                                'account_id': income_id,
                                                                'qb_id': ol_qb_id,
                                                                'price_unit': sp,
                                                                'tax_ids': custom_tax_id_id,
                                                            })

                                                        if create_iv:
                                                            company.quickbooks_last_credit_note_imported_id = cust.get(
                                                                'Id')

                                                    else:

                                                        dict_ol = {}
                                                        res_product_acc = self.env[
                                                            'product.product'].search([])

                                                        #                                                     print("**********PRODUCT ACCOUNT CHECK************",res_product_acc.property_account_income_id)
                                                        dict_ol.clear()
                                                        dict_ol[
                                                            'move_id'] = account_invoice.id
                                                        dict_ol[
                                                            'product_id'] = res_product.id

                                                        if i.get('Id'):
                                                            dict_ol['qb_id'] = int(
                                                                i.get('Id'))

                                                        if i.get('SalesItemLineDetail').get('TaxCodeRef'):

                                                            tax_val = i.get('SalesItemLineDetail').get(
                                                                'TaxCodeRef').get(
                                                                'value')
                                                            if tax_val == 'TAX':
                                                                dict_ol[
                                                                    'tax_ids'] = custom_tax_id
                                                            else:
                                                                dict_ol[
                                                                    'tax_ids'] = None

                                                        if i.get('SalesItemLineDetail').get('Qty'):
                                                            dict_ol['quantity'] = i.get('SalesItemLineDetail').get(
                                                                'Qty')

                                                        if i.get('SalesItemLineDetail').get('UnitPrice'):
                                                            dict_ol['price_unit'] = float(
                                                                i.get('SalesItemLineDetail').get('UnitPrice'))
                                                        else:
                                                            if not i.get('SalesItemLineDetail').get('Qty'):
                                                                dict_ol[
                                                                    'quantity'] = 1
                                                                dict_ol['price_unit'] = float(
                                                                    i.get('Amount'))
                                                            else:
                                                                dict_ol[
                                                                    'price_unit'] = 0.0

                                                        if i.get('Description'):
                                                            dict_ol['name'] = i.get(
                                                                'Description')
                                                        else:
                                                            dict_ol[
                                                                'name'] = 'NA'
                                                        if res_product.property_account_income_id:
                                                            dict_ol[
                                                                'account_id'] = res_product.property_account_income_id.id
                                                        else:
                                                            dict_ol[
                                                                'account_id'] = res_product.categ_id.property_account_income_categ_id.id

                                                            create_p = self.env[
                                                                'account.move.line'].create(dict_ol)
                                                            if create_p:
                                                                company.quickbooks_last_credit_note_imported_id = cust.get(
                                                                    'Id')
            else:
                raise UserError("Empty Data")
                _logger.warning(_('Empty data'))

    # @api.multi
    def export_customers_mapping(self):
        company = self.env['res.users'].search([('id', '=', self._uid)]).company_id
        if company.last_customer_mapping_export:
            res_partner = self.env['res.partner'].search([
                # ('check_update_flag', '=', True),
                ('customer_rank', '>', 0),
                ('type', '=', 'contact'),
                ('write_date', '>=', company.last_customer_mapping_export)
            ])
        else:
            res_partner = self.env['res.partner'].search([
                ('customer_rank', '>', 0),
                ('qbo_vendor_id', '=', False),
                ('qbo_customer_id', '=', False)])
        if self.export_mapping_customer_field and self.export_mapping_customer_id:
            url_str = self.get_import_query_url_1()
            url = url_str.get('url')
            headers = url_str.get('headers')
            for contact in res_partner:
                outdict = {}
                if contact.customer_rank and contact.type == 'contact':
                    for fields_line_id in self.export_mapping_customer_id.fields_lines:
                        split_key = fields_line_id.value.split('.')
                        attr = getattr(contact, fields_line_id.col1.name)
                        if not attr:
                            continue
                        if fields_line_id.ttype in ['datetime', 'date', 'boolean', 'integer', 'float', 'char', 'text', 'monetary']:
                            values = attr
                        elif fields_line_id.ttype in ['many2one']:
                            values = attr.name or False
                        elif fields_line_id.ttype in ['one2many']:
                            values = str(attr.parent_id.id)
                        if len(split_key) > 1:
                            if split_key[0] not in outdict:
                                outdict[split_key[0]] = {split_key[1]: values}
                            else:
                                outdict[split_key[0]].update({split_key[1] : values})
                        else:
                            outdict[split_key[0]] = values
                if contact.qbo_customer_id:
                    realmId = self.realm_id
                    if self.access_token:
                        sql_query = "select Id,SyncToken from customer Where Id = '{}'".format(
                            str(contact.qbo_customer_id))

                        result = requests.request('GET', url + "/query?query=" + sql_query, headers=headers)
                        if result.status_code == 200:
                            parsed_result = result.json()
                            if parsed_result.get('QueryResponse') and parsed_result.get('QueryResponse').get(
                                    'Customer'):
                                customer_id_retrieved = parsed_result.get('QueryResponse').get('Customer')[0].get('Id')
                                syncToken = ''
                                if customer_id_retrieved:
                                    ''' HIT UPDATE REQUEST '''
                                    syncToken = parsed_result.get('QueryResponse').get('Customer')[0].get('SyncToken')
                                    outdict.update({
                                        self.export_mapping_customer_id.search_field_qbo: customer_id_retrieved,
                                        'SyncToken': syncToken,
                                        'sparse': "true",
                                    })
                    contact.sendDataToQuickbooksForUpdate(outdict)
                    QBQ_od = contact.sendDataToQuickbook(outdict)
                else:
                    QBQ_od = contact.sendDataToQuickbook(outdict)
                    contact.write({'qbo_customer_id': QBQ_od})
                    contact._cr.commit()
            company.last_customer_mapping_export = fields.Datetime.now()

    # @api.multi
    def export_customers(self):
        res_partner = self.env['res.partner'].search([])

        for contact in res_partner:
            if contact.id == 1 or contact.id == 3:
                _logger.info(_("There is no any record to be exported."))
            else:
                if contact.customer_rank and contact.type == 'contact':
                    contact.exportCustomer()

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

    def export_vendors_mapping(self):
        company = self.env['res.users'].search([('id', '=', self._uid)]).company_id
        if company.last_vendor_mapping_export:
            res_partner = self.env['res.partner'].search([
                # ('check_update_flag', '=', True),
                ('supplier_rank', '>', 0),
                ('write_date', '>=', company.last_vendor_mapping_export),
                ('type', '=', 'contact')
            ])
        else:
            res_partner = self.env['res.partner'].search([
                ('supplier_rank', '>', 0),
                ('qbo_vendor_id', '=', False),
                ('qbo_customer_id', '=', False)
            ])
        if self.export_mapping_vendor_field and self.export_mapping_vendor_id:
            url_str = self.get_import_query_url_1()
            url = url_str.get('url')
            headers = url_str.get('headers')
            for contact in res_partner:
                outdict = {}
                for fields_line_id in self.export_mapping_vendor_id.fields_lines:
                    split_key = fields_line_id.value.split('.')
                    attr = getattr(contact, fields_line_id.col1.name)
                    if not attr:
                        continue
                    if fields_line_id.ttype in ['boolean', 'integer', 'float', 'char', 'text', 'monetary']:
                        values = attr
                    elif fields_line_id.ttype == 'datetime':
                        values = fields.Datetime.to_string(attr)
                    elif fields_line_id.ttype == 'date':
                        values = fields.Date.to_string(attr)
                    elif fields_line_id.ttype in ['many2one']:
                        values = attr.name or False
                    elif fields_line_id.ttype in ['one2many']:
                        values = str(attr.parent_id.id)
                    if len(split_key) > 1:
                        if split_key[0] not in outdict:
                            outdict[split_key[0]] = {split_key[1]: values}
                        else:
                            outdict[split_key[0]].update({split_key[1] : values})
                    else:
                        outdict[split_key[0]] = values
                if contact.qbo_vendor_id:
                    sql_query = "select Id,SyncToken from vendor Where Id = '{}'".format(
                        str(contact.qbo_vendor_id))
                    result = requests.request('GET', url + "/query?query=" + sql_query, headers=headers)
                    if result.status_code == 200:
                        parsed_result = result.json()
                        if parsed_result.get('QueryResponse') and parsed_result.get('QueryResponse').get('Vendor'):
                            customer_id_retrieved = parsed_result.get('QueryResponse').get('Vendor')[0].get('Id')
                            if customer_id_retrieved:
                                ''' HIT UPDATE REQUEST '''
                                syncToken = parsed_result.get('QueryResponse').get('Vendor')[0].get('SyncToken')
                                outdict.update({
                                    self.export_mapping_vendor_id.search_field_qbo: customer_id_retrieved,
                                    'SyncToken': syncToken,
                                    'sparse': "true",
                                })
                    contact.sendVendorDataToQuickbooksForUpdate(outdict)
                else:
                    QBQ_od = contact.sendVendorDataToQuickbook(outdict)
                    contact.write({'qbo_vendor_id': QBQ_od})
                    contact._cr.commit()
            company.last_vendor_mapping_export = fields.Datetime.now()

    # @api.multi
    def export_vendors(self):
        res_partner = self.env['res.partner'].search([])
        for contact in res_partner:
            if contact.id == 1 or contact.id == 3:
                _logger.info(_("There is no any record to be exported."))
            else:
                if contact.supplier_rank:
                    contact.exportVendor()
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

    # @api.multi
    def export_accounts(self):
        accounts = self.env['account.account'].search([])

        for account in accounts:
            if not account.qbo_id:
                account.export_to_qbo()
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
    # @api.multi

    # @api.multi
    def export_tax(self):
        taxes = self.env['account.tax'].search([('amount_type','!=','group')])
        for tax in taxes:
            tax.export_to_qbo()
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
    # @api.multi
    # def export_tax_agency(self):
    #     taxes = self.env['account.tax.agency'].search([])
    #     print("TAX AGENCY : ----------------------> ", taxes)
    #     for tax in taxes:
    #         print("AGENCY : ----------------------> ", tax)
    #         tax.export_to_qbo()

    # @api.multi
    def export_products(self):
        products = self.env['product.product'].search([])
        if not products:
            raise UserError('There is no any record to be exported.')
        for product in products:
            product.export_product_to_qbo()
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

    # @api.multi
    def export_payment_method(self):
        payment_method = self.env['account.journal'].search(
            [('type', 'in', ['cash', 'bank'])])
        if not payment_method:
            raise UserError('There is no any record to be exported.')
        for method in payment_method:
            if not method.qbo_method_id:
                # print("\n\n--- method ---",method)
                method.export_to_qbo()
            else:
                _logger.info(_("There is no any record to be exported."))
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

    def export_payment_terms_mapping(self):
        if self.last_payment_term_mapping_export:
            apt_ids = self.env['account.payment.term'].search([
                ('write_date', '>=', self.last_payment_term_mapping_export),
            ])
        else:
            apt_ids = self.env['account.payment.term'].search([('x_quickbooks_id', '=', False)])
        if self.export_mapping_payment_term_id and self.export_mapping_payment_term_field:
            url_str = self.get_import_query_url_1()
            url = url_str.get('url')
            headers = url_str.get('headers')
            for apt_id in apt_ids:
                outdict = {}
                for fields_line_id in self.export_mapping_payment_term_id.fields_lines:
                    split_key = fields_line_id.value.split('.')
                    attr = getattr(apt_id, fields_line_id.col1.name)
                    if not attr:
                        attr = ''
                    if fields_line_id.ttype in ['boolean', 'integer', 'float', 'char', 'text', 'monetary']:
                        values = attr
                    elif fields_line_id.ttype == 'datetime':
                        values = fields.Datetime.to_string(attr)
                    if len(split_key) > 1:
                        if split_key[0] not in outdict:
                            outdict[split_key[0]] = {split_key[1]: values}
                        else:
                            outdict[split_key[0]].update({split_key[1]: values})
                    else:
                        outdict[split_key[0]] = values
                if apt_id.x_quickbooks_id:
                    sql_query = "select Id,SyncToken from term Where Id = '{}'".format(apt_id.x_quickbooks_id)
                    result1 = requests.request('GET', url + "/query?query=" + sql_query, headers=headers)
                    parsed_result = result1.json()
                    outdict.update({
                        'SyncToken': parsed_result.get('QueryResponse').get('Term')[0].get('SyncToken'),
                        'Id': apt_id.x_quickbooks_id,
                    })
                outdict.update({'DueDays': apt_id.line_ids and apt_id.line_ids[0].days or 0.0})
                parsed_dict = json.dumps(outdict)
                result = requests.request('POST', url + "/term", headers=headers, data=parsed_dict)
                if result.status_code == 200:
                    parsed_result = result.json()
                    apt_id.x_quickbooks_id = parsed_result.get('Term').get('Id')
                    self.last_payment_term_mapping_export = datetime.now()
                    _logger.info(_("Payment Terms Id: %s" % (apt_id.x_quickbooks_id)))
                    self._cr.commit()
                else:
                    self.error_message_from_quickbook(result, apt_id.name, 'Payment Terms')

    # @api.multi
    def export_payment_terms(self):
        payment_term = self.env['account.payment.term'].search([])
        if not payment_term:
            raise UserError('There is no any record to be exported.')
        for term in payment_term:
            term.export_payment_term_to_quickbooks()
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

    def export_sale_order_mapping(self):
        # sales = self.env['sale.order'].search([('quickbook_id', '=', False)])
        if self.last_so_mapping_export:
            sales = self.env['sale.order'].search([
                ('write_date', '>=', self.last_so_mapping_export),
                ('state', '=', 'sale'),
                ('quickbook_id', '=', False)])
        else:
            sales = self.env['sale.order'].search([
                ('state', '=', 'sale'),
                ('quickbook_id', '=', False)])
        if self.export_mapping_so_field and self.export_mapping_so_id:
            url_str = self.get_import_query_url_1()
            url = url_str.get('url')
            headers = url_str.get('headers')
            for sale_id in sales:
                tax_ids = sale_id.order_line.mapped('tax_id').filtered(lambda x: x.qbo_tax_id)
                if not tax_ids:
                    tax_id = self.env['account.tax'].search([('type_tax_use', '=', 'sale')], limit=1)
                    qb_tax_id = tax_id.qbo_tax_id
                else:
                    qb_tax_id = tax_ids[0].qbo_tax_id
                outdict = {'TxnTaxDetail': {'TxnTaxCodeRef': {'value': qb_tax_id}}}
                for fields_line_id in self.export_mapping_so_id.fields_lines:
                    split_key = fields_line_id.value.split('.')
                    attr = getattr(sale_id, fields_line_id.col1.name)
                    if not attr:
                        continue
                    if fields_line_id.ttype in ['boolean', 'integer', 'float', 'char', 'text', 'monetary']:
                        values = attr
                    elif fields_line_id.ttype == 'selection' and fields_line_id.value == 'GlobalTaxCalculation':
                        if sale_id.tax_state == 'exclusive':
                            values = "TaxExcluded"
                        elif sale_id.tax_state == 'inclusive':
                            values = "TaxInclusive"
                        elif sale_id.tax_state == 'notapplicable':
                            values = "NotApplicable"
                    elif fields_line_id.ttype == 'datetime':
                        values = fields.Datetime.to_string(attr)
                    elif fields_line_id.ttype == 'date':
                        values = fields.Date.to_string(attr)
                    elif fields_line_id.ttype in ['many2one']:
                        m2o_ref = getattr(sale_id, fields_line_id.col1.name)
                        attr = getattr(m2o_ref, fields_line_id.relation_field.name)
                        values = attr or ''
                    elif fields_line_id.ttype in ['one2many']:
                        line_list = []
                        for line in attr:
                            line_val = {'DetailType': 'SalesItemLineDetail'}
                            for sub_field in fields_line_id.sub_field_object_id.sub_field_ids:
                                sub_split_key = sub_field.qb_field.split('.')
                                sub_attr = getattr(line, sub_field.field_id.name)
                                if sub_field.ttype == 'many2one':
                                    sub_attr = getattr(sub_attr, sub_field.relation_field.name)
                                    if sub_field.relation == 'product.product' and not sub_attr:
                                        sub_attr = self.env['product.template'].get_qbo_product_ref(sub_attr)
                                    value = sub_attr or ""
                                else:
                                    value = sub_attr or ""
                                if len(sub_split_key) == 1:
                                    line_val.update({sub_field.qb_field: value})
                                elif len(sub_split_key) == 2:
                                    if sub_field.field_id.name == 'price_unit' and line.discount:
                                        value = value - (value * (line.discount / 100))
                                    if sub_split_key[0] not in line_val:
                                        line_val.update({sub_split_key[0]: {sub_split_key[1]: value}})
                                    else:
                                        line_val[sub_split_key[0]].update({sub_split_key[1]: value})
                                    # line_val[sub_split_key[0]] = {sub_split_key[1]: values}
                                elif len(sub_split_key) == 3:
                                    tax_type = "NON"
                                    if line.tax_id:
                                        tax_type = "TAX"
                                    if sub_split_key[0] == 'SalesItemLineDetail':
                                        line_val.update({sub_split_key[0]: {
                                            sub_split_key[1]: {
                                                sub_split_key[
                                                    2]: line.product_id.qbo_product_id or line.product_id.product_tmpl_id.qbo_product_id},
                                            "TaxCodeRef": {"value": tax_type}
                                        }})
                                    else:
                                        line_val.update({sub_split_key[0]: {
                                            sub_split_key[1]: {
                                                sub_split_key[
                                                    2]: line.product_id.qbo_product_id or line.product_id.product_tmpl_id.qbo_product_id}}})
                            line_list.append(line_val)
                        values = line_list
                    if len(split_key) > 1:
                        if split_key[0] not in outdict:
                            outdict[split_key[0]] = {split_key[1]: values}
                        else:
                            outdict[split_key[0]].update({split_key[1]: values})
                    else:
                        outdict[split_key[0]] = values
                parsed_dict = json.dumps(outdict)
                result = requests.request('POST', url + "/estimate",
                                          headers=headers, data=parsed_dict)
                if result.status_code == 200:
                    response = result.json()
                    qbo_id = int(response.get('Estimate').get('Id'))
                    sale_id.quickbook_id = qbo_id
                    self.last_so_mapping_export = datetime.now()
                    self._cr.commit()
                    _logger.info(_("%s exported successfully to QBO" % (sale_id.name)))
                else:
                    self.error_message_from_quickbook(result, sale_id.name, 'Sale Order')

    # @api.multi
    def export_sale_order(self):
        sales = self.env['sale.order'].search([])
        if not sales:
            raise UserError('There is no any record to be exported.')

        if len(sales) == 1:
            if sales.state not in ['done', 'sale']:
                raise ValidationError(
                    _("Only confirmed Sales Order is exported to QBO."))

        for sale in sales:
            if sale.quickbook_id and sale.state == 'sale':
                _logger.info(
                    _("Sale Order is already exported to QBO. %s" % sale))
            elif not sale.quickbook_id:
                _logger.info('_______')
                sale.exportSaleOrder()
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

    # @api.multi
    def export_invoice(self):
        invoices = self.env['account.move'].search([])
        if not invoices:
            raise UserError('There is no any record to be exported.')
        for inv in invoices:
            if inv.partner_id.customer_rank:
                if inv.state == 'open' and inv.qbo_invoice_id:
                    _logger.info(
                        _("Invoice is already exported to QBO. %s" % inv))
                else:
                    if not inv.qbo_invoice_id:
                        if inv.move_type != 'out_refund' or inv.move_type != 'in_refund':
                            inv.export_to_qbo()
                        else:
                            _logger.info(
                                _("This '%s' can not be exported as this is refund type." % inv.name))
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

    def export_invoice_mapping(self):
        move_type = 'out_invoice'
        last_mapping_export = self.last_inv_mapping_export
        export_name = 'Invoice'
        query_type = "/invoice"
        if self.env.context.get('credit'):
            export_name = 'Credit Notes'
            move_type = 'out_refund'
            last_mapping_export = self.last_credit_mapping_export
            query_type = "/creditmemo"
        if last_mapping_export:
            invoice_ids = self.env['account.move'].search([
                ('write_date', '>=', last_mapping_export),
                ('qbo_invoice_id', '=', False),
                ('state', '=', 'posted'),
                ('move_type', '=', move_type)
            ])
        else:
            invoice_ids = self.env['account.move'].search([
                ('qbo_invoice_id', '=', False),
                ('state', '=', 'posted'),
                ('move_type', '=', move_type)
            ])
        url_str = self.get_import_query_url_1()
        url = url_str.get('url')
        headers = url_str.get('headers')
        for invoice_id in invoice_ids:
            tax_ids = invoice_id.invoice_line_ids.mapped('tax_ids').filtered(lambda x: x.qbo_tax_id)
            if not tax_ids:
                tax_id = self.env['account.tax'].search([('type_tax_use', '=', 'sale'), ('qbo_tax_id', '!=', False)], limit=1)
                qb_tax_id = tax_id.qbo_tax_id
            else:
                qb_tax_id = tax_ids[0].qbo_tax_id
            if qb_tax_id:
                outdict = {'TxnTaxDetail': {'TxnTaxCodeRef': {'value': qb_tax_id}}}
            else:
                outdict = {}
            for fields_line_id in self.export_mapping_inv_id.fields_lines:
                split_key = fields_line_id.value.split('.')
                if fields_line_id.col1.name == 'qbo_invoice_name':
                    attr = getattr(invoice_id, 'name')
                elif fields_line_id.col1.name == 'currency_id':
                    continue
                else:
                    attr = getattr(invoice_id, fields_line_id.col1.name)
                if not attr:
                    continue
                if fields_line_id.ttype in ['boolean', 'integer', 'float', 'char', 'text', 'monetary']:
                    values = attr
                elif fields_line_id.ttype == 'selection' and fields_line_id.value == 'GlobalTaxCalculation':
                    if invoice_id.tax_state == 'exclusive':
                        values = "TaxExcluded"
                    elif invoice_id.tax_state == 'inclusive':
                        values = "TaxInclusive"
                    elif invoice_id.tax_state == 'notapplicable':
                        values = "NotApplicable"
                elif fields_line_id.ttype == 'datetime':
                    values = fields.Datetime.to_string(attr)
                elif fields_line_id.ttype == 'date':
                    values = fields.Date.to_string(attr)
                elif fields_line_id.ttype in ['many2one']:
                    m2o_ref = getattr(invoice_id, fields_line_id.col1.name)
                    attr = getattr(m2o_ref, fields_line_id.relation_field.name)
                    values = attr or ''
                elif fields_line_id.ttype in ['one2many']:
                    line_list = []
                    for line in attr:
                        line_val = {
                            'DetailType': 'SalesItemLineDetail',
                        }
                        for sub_field in fields_line_id.sub_field_object_id.sub_field_ids:
                            sub_split_key = sub_field.qb_field.split('.')
                            sub_attr = getattr(line, sub_field.field_id.name)
                            if sub_field.ttype == 'many2one':
                                if sub_field.relation == 'product.product' and not sub_attr:
                                    sub_attr = self.env['product.template'].get_qbo_product_ref(sub_attr)
                                value = sub_attr or ""
                            else:
                                value = sub_attr or ""
                            if len(sub_split_key) == 1:
                                line_val.update({sub_field.qb_field: value})
                            elif len(sub_split_key) == 2:
                                if sub_field.field_id.name == 'price_unit' and line.discount:
                                    value = value - (value * (line.discount / 100))
                                if sub_split_key[0] not in line_val:
                                    line_val.update({sub_split_key[0]: {sub_split_key[1]: value}})
                                else:
                                    line_val[sub_split_key[0]].update({sub_split_key[1]: value})
                                # line_val[sub_split_key[0]] = {sub_split_key[1]: values}
                            elif len(sub_split_key) == 3:
                                tax_type = "NON"
                                if line.tax_ids:
                                    tax_type = "TAX"
                                if sub_split_key[0] == 'SalesItemLineDetail':
                                    line_val.update({sub_split_key[0]: {
                                        sub_split_key[1]: {
                                            sub_split_key[
                                                2]: line.product_id.qbo_product_id or line.product_id.product_tmpl_id.qbo_product_id},
                                        "TaxCodeRef": {"value": tax_type}
                                    }})
                                else:
                                    line_val.update({sub_split_key[0]: {
                                        sub_split_key[1]: {
                                            sub_split_key[
                                                2]: line.product_id.qbo_product_id or line.product_id.product_tmpl_id.qbo_product_id}}})
                        line_list.append(line_val)
                    values = line_list
                if len(split_key) > 1:
                    if split_key[0] not in outdict:
                        outdict[split_key[0]] = {split_key[1]: values}
                    else:
                        outdict[split_key[0]].update({split_key[1]: values})
                else:
                    outdict[split_key[0]] = values
            result = requests.request('POST', url + query_type,
                                      headers=headers, data=json.dumps(outdict))
            if result.status_code == 200:
                response = result.json()
                if self.env.context.get('credit'):
                    invoice_id.qbo_invoice_id = response.get('CreditMemo').get('Id')
                    invoice_id.qbo_invoice_name = response.get('CreditMemo').get('DocNumber')
                    self.last_credit_mapping_export = datetime.now()
                else:
                    invoice_id.qbo_invoice_id = response.get('Invoice').get('Id')
                    invoice_id.qbo_invoice_name = response.get('Invoice').get('DocNumber')
                    self.last_inv_mapping_export = datetime.now()
                self._cr.commit()
                _logger.info(_("%s exported successfully to QBO" % (invoice_id.name)))
            else:
                self.error_message_from_quickbook(result, invoice_id.name, export_name)

    def export_bills_mapping(self):
        if self.last_bill_mapping_export:
            invoice_ids = self.env['account.move'].search([
                ('write_date', '>=', self.last_bill_mapping_export.date()),
                ('qbo_invoice_id', '=', False),
                ('state', '=', 'posted'),
                ('move_type', '=', 'in_invoice')
            ])
        else:
            invoice_ids = self.env['account.move'].search([
                ('qbo_invoice_id', '=', False),
                ('state', '=', 'posted'),
                ('move_type', '=', 'in_invoice')
            ])
        url_str = self.get_import_query_url_1()
        url = url_str.get('url')
        headers = url_str.get('headers')
        for invoice_id in invoice_ids:
            tax_ids = invoice_id.invoice_line_ids.mapped('tax_ids').filtered(lambda x: x.qbo_tax_id)
            if not tax_ids:
                tax_id = self.env['account.tax'].search([('type_tax_use', '=', 'purchase'), ('qbo_tax_id', '!=', False)], limit=1)
                qb_tax_id = tax_id.qbo_tax_id or tax_id.qbo_tax_rate_id
            else:
                qb_tax_id = tax_ids[0].qbo_tax_id
            if qb_tax_id:
                outdict = {'TxnTaxDetail': {'TxnTaxCodeRef': {'value': qb_tax_id}}}
            else:
                outdict = {}
            for fields_line_id in self.export_mapping_bill_id.fields_lines:
                split_key = fields_line_id.value.split('.')
                if fields_line_id.col1.name == 'qbo_invoice_name':
                    attr = getattr(invoice_id, 'name')
                elif fields_line_id.col1.name == 'currency_id':
                    continue
                else:
                    attr = getattr(invoice_id, fields_line_id.col1.name)
                if not attr:
                    continue
                if fields_line_id.ttype in ['boolean', 'integer', 'float', 'char', 'text', 'monetary']:
                    values = attr
                elif fields_line_id.ttype == 'selection' and fields_line_id.value == 'GlobalTaxCalculation':
                    if invoice_id.tax_state == 'exclusive':
                        values = "TaxExcluded"
                    elif invoice_id.tax_state == 'inclusive':
                        values = "TaxInclusive"
                    elif invoice_id.tax_state == 'notapplicable':
                        values = "NotApplicable"
                elif fields_line_id.ttype == 'datetime':
                    values = fields.Datetime.to_string(attr)
                elif fields_line_id.ttype == 'date':
                    values = fields.Date.to_string(attr)
                elif fields_line_id.ttype in ['many2one']:
                    m2o_ref = getattr(invoice_id, fields_line_id.col1.name)
                    attr = getattr(m2o_ref, fields_line_id.relation_field.name)
                    values = attr or ''
                elif fields_line_id.ttype in ['one2many']:
                    line_list = []
                    for line in attr:
                        line_val = {
                            'DetailType': 'ItemBasedExpenseLineDetail',
                        }
                        for sub_field in fields_line_id.sub_field_object_id.sub_field_ids:
                            sub_split_key = sub_field.qb_field.split('.')
                            sub_attr = getattr(line, sub_field.field_id.name)
                            if sub_field.ttype == 'many2one':
                                if sub_field.relation == 'product.product' and not sub_attr:
                                    sub_attr = self.env['product.template'].get_qbo_product_ref(sub_attr)
                                value = sub_attr or ""
                            else:
                                value = sub_attr or ""
                            if len(sub_split_key) == 1:
                                line_val.update({sub_field.qb_field: value})
                            elif len(sub_split_key) == 2:
                                if sub_field.field_id.name == 'price_unit' and line.discount:
                                    value = value - (value * (line.discount / 100))
                                if sub_split_key[0] not in line_val:
                                    line_val.update({sub_split_key[0]: {sub_split_key[1]: value}})
                                else:
                                    line_val[sub_split_key[0]].update({sub_split_key[1]: value})
                                # line_val[sub_split_key[0]] = {sub_split_key[1]: values}
                            elif len(sub_split_key) == 3:
                                tax_type = "NON"
                                if line.tax_ids:
                                    tax_type = "TAX"
                                if sub_split_key[0] == 'ItemBasedExpenseLineDetail':
                                    line_val.update({sub_split_key[0]: {
                                        sub_split_key[1]: {
                                            sub_split_key[
                                                2]: line.product_id.qbo_product_id or line.product_id.product_tmpl_id.qbo_product_id},
                                        "TaxCodeRef": {"value": tax_type}
                                    }})
                                else:
                                    line_val.update({sub_split_key[0]: {
                                        sub_split_key[1]: {
                                            sub_split_key[
                                                2]: line.product_id.qbo_product_id or line.product_id.product_tmpl_id.qbo_product_id}}})
                        line_list.append(line_val)
                    values = line_list
                if len(split_key) > 1:
                    if split_key[0] not in outdict:
                        outdict[split_key[0]] = {split_key[1]: values}
                    else:
                        outdict[split_key[0]].update({split_key[1]: values})
                else:
                    outdict[split_key[0]] = values
            result = requests.request('POST', url + "/bill",
                                      headers=headers, data=json.dumps(outdict))
            if result.status_code == 200:
                response = result.json()
                invoice_id.qbo_invoice_id = response.get('Bill').get('Id')
                invoice_id.qbo_invoice_name = response.get('Bill').get('DocNumber')
                self.last_bill_mapping_export = datetime.now()
                self._cr.commit()
                _logger.info(_("%s exported successfully to QBO" % (invoice_id.name)))
            else:
                self.error_message_from_quickbook(result, invoice_id.name, 'Bill')

    def export_purchase_order_mapping(self):
        if self.last_po_mapping_export:
            purchase = self.env['purchase.order'].search([
                ('write_date', '>=', self.last_po_mapping_export),
                ('state', '=', 'purchase'),
                ('quickbook_id', '=', False)
            ])
        else:
            purchase = self.env['purchase.order'].search([
                ('state', '=', 'purchase'),
                ('quickbook_id', '=', False)])
        if self.export_mapping_po_field and self.export_mapping_po_id:
            url_str = self.get_import_query_url_1()
            url = url_str.get('url')
            headers = url_str.get('headers')
            for purchase_id in purchase:
                # tax_ids = purchase_id.order_line.mapped('taxes_id').filtered(lambda x: x.qbo_tax_id)
                # if not tax_ids:
                #     tax_id = self.env['account.tax'].search([('type_tax_use', '=', 'purchase')], limit=1)
                #     qb_tax_id = tax_id.qbo_tax_id
                # else:
                #     qb_tax_id = tax_ids[0].qbo_tax_id
                # outdict = {'TxnTaxDetail': {'TxnTaxCodeRef': {'value': qb_tax_id}}}
                outdict = {}
                for fields_line_id in self.export_mapping_po_id.fields_lines:
                    split_key = fields_line_id.value.split('.')
                    attr = getattr(purchase_id, fields_line_id.col1.name)
                    if not attr:
                        continue
                    if fields_line_id.ttype in ['boolean', 'integer', 'float', 'char', 'text', 'monetary']:
                        values = attr
                    elif fields_line_id.ttype == 'selection' and fields_line_id.value == 'GlobalTaxCalculation':
                        if purchase_id.tax_state == 'exclusive':
                            values = "TaxExcluded"
                        elif purchase_id.tax_state == 'inclusive':
                            values = "TaxInclusive"
                        elif purchase_id.tax_state == 'notapplicable':
                            values = "NotApplicable"
                    elif fields_line_id.ttype == 'datetime':
                        values = fields.Datetime.to_string(attr)
                    elif fields_line_id.ttype == 'date':
                        values = fields.Date.to_string(attr)
                    elif fields_line_id.ttype in ['many2one']:
                        m2o_ref = getattr(purchase_id, fields_line_id.col1.name)
                        attr = getattr(m2o_ref, fields_line_id.relation_field.name)
                        values = attr or ''
                    elif fields_line_id.ttype in ['one2many']:
                        line_list = []
                        for line in attr:
                            line_val = {
                                'DetailType': 'ItemBasedExpenseLineDetail',
                            }
                            for sub_field in fields_line_id.sub_field_object_id.sub_field_ids:
                                sub_split_key = sub_field.qb_field.split('.')
                                sub_attr = getattr(line, sub_field.field_id.name)
                                if sub_field.ttype == 'many2one':
                                    if sub_field.relation == 'product.product' and not sub_attr:
                                        sub_attr = self.env['product.template'].get_qbo_product_ref(sub_attr)
                                    value = sub_attr or ""
                                else:
                                    value = sub_attr or ""
                                if len(sub_split_key) == 1:
                                    line_val.update({sub_field.qb_field: value})
                                elif len(sub_split_key) == 2:
                                    if sub_split_key[0] not in line_val:
                                        line_val.update({sub_split_key[0]: {sub_split_key[1]: value}})
                                    else:
                                        line_val[sub_split_key[0]].update({sub_split_key[1]: value})
                                elif len(sub_split_key) == 3:
                                    line_val.update({sub_split_key[0]: {
                                        sub_split_key[1]: {
                                            sub_split_key[
                                                2]: line.product_id.qbo_product_id or line.product_id.product_tmpl_id.qbo_product_id}}})
                            line_list.append(line_val)
                        values = line_list
                    if len(split_key) > 1:
                        if split_key[0] not in outdict:
                            outdict[split_key[0]] = {split_key[1]: values}
                        else:
                            outdict[split_key[0]].update({split_key[1]: values})
                    else:
                        outdict[split_key[0]] = values
                parsed_dict = json.dumps(outdict)
                result = requests.request('POST', url + "/purchaseorder",
                                          headers=headers, data=parsed_dict)
                if result.status_code == 200:
                    response = result.json()
                    qbo_id = response.get('PurchaseOrder').get('Id')
                    purchase_id.quickbook_id = qbo_id
                    self.last_po_mapping_export = datetime.now()
                    self._cr.commit()
                    _logger.info(_("%s exported successfully to QBO" % (purchase_id.name)))
                else:
                    self.error_message_from_quickbook(result, purchase_id.name, 'Purchase Order')

    # @api.multi
    def export_purchase_order(self):
        purchase = self.env['purchase.order'].search([])
        if not purchase:
            raise UserError('There is no any record to be exported.')
        for order in purchase:
            if order.state == 'purchase' and order.quickbook_id:
                _logger.info(
                    _("Purchase Order is already exported to QBO. %s" % order))
            else:
                order.exportPurchaseOrder()
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

    def export_customer_payment(self):
        customer_payments = self.env['account.payment'].search(
            [('payment_type', '=', 'inbound')])
        if not customer_payments:
            raise UserError('There is no record to be exported to QBO.')
        for payment in customer_payments:
            if payment.qbo_payment_id:
                _logger.info(
                    "Customer Payment is already exported to QBO.%s" % payment)
            else:
                payment.export_to_qbo()
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

    def export_vendor_payment(self):
        vendor_payments = self.env['account.payment'].search(
            [('payment_type', '=', 'outbound')])
        if not vendor_payments:
            raise UserError('There is no record to be exported to QBO.')
        for payment in vendor_payments:
            if payment.qbo_bill_payment_id:
                _logger.info(
                    "Vendor Payment is already exported to QBO.%s" % payment)
            else:
                payment.export_to_qbo()
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

    # @api.multi
    def export_vendor_bill(self):
        invoices = self.env['account.move'].search([])
        if not invoices:
            raise UserError('There is no any record to be exported.')
        for inv in invoices:
            if inv.partner_id.supplier_rank:
                if inv.state == 'open' and inv.qbo_invoice_id:
                    _logger.info(
                        _("Invoice is already exported to QBO. %s" % inv))
                else:
                    if not inv.qbo_invoice_id:
                        if inv.move_type != 'out_refund' or inv.move_type != 'in_refund':
                            inv.export_to_qbo()
                        else:
                            _logger.info(
                                _("This '%s' can not be exported as this is refund type." % inv.name))
                    # inv.export_to_qbo()
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

    # @api.multi
    def export_department(self):
        department = self.env['hr.department'].search([])
        if not department:
            raise UserError('There is no any record to be exported.')
        for dept in department:
            dept.exportDepartment()
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

    # @api.multi
    def export_employee(self):
        employee = self.env['hr.employee'].search([])
        if not employee:
            raise UserError('There is no any record to be exported.')
        for emp in employee:
            emp.export_Employees_to_qbo()
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

        #

    ##########################################################################
    def import_journal_entry_cron(self):
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        _logger.info("Cron company is-> {}".format(company))

        '''
        This function will import journal entry from qbo
        '''
        # For importing journal entry from qbo
        company.import_journal_entry()
        _logger.info("--------Journal Entry imported successfully.")
        self._cr.commit()

    def import_journal_entry(self):
        """IMPORT JournalEntry FROM JournalEntry TO ODOO"""
        _logger.info(
            "\n\n\n<-----------------------------------JournalEntry-------------------------------------->", )

        if not self.journal_entry:
            raise UserError(
                "Journal Entry is not defined in the configuration.")

        res = self.journal_main_function()
        _logger.info("RESPONSE : %s", res)

        success_form = self.env.ref(
            'pragmatic_quickbooks_connector.import_successfull_view', False)
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

    def journal_main_function(self):
        _logger.info(
            "Inside journal_main_function ****************************")
        company = self
        if company.access_token:
            headers = {}
            headers['Authorization'] = 'Bearer ' + self.access_token
            headers['accept'] = 'application/json'
            headers['Content-Type'] = 'text/plain'

            if company.import_je_by_date:
                query = "select * from JournalEntry WHERE Metadata.LastUpdatedTime > '%s' order by Id " % (
                    company.import_je_date)
            else:
                query = "select * from JournalEntry WHERE Id > '%s' order by Id" % (
                    company.quickbooks_last_journal_entry_imported_id)

            data = requests.request('GET', self.url + str(self.realm_id) + "/query?query=" + query,
                                    headers=headers)
            if data:
                _logger.info(
                    "JournalEntry data is -------------------->{}".format(data.text))
                recs = []
                parsed_data = json.loads(str(data.text))
                if parsed_data:
                    _logger.info(
                        "Parsed data for JournalEntry is -------------> {}".format(parsed_data))
                    if parsed_data.get('QueryResponse') and parsed_data.get('QueryResponse').get('JournalEntry'):
                        for JournalEntry in parsed_data.get('QueryResponse').get('JournalEntry'):
                            _logger.info(
                                _('JournalEntry Record : \n\n\n\nJournalEntry From Quickbooks : %s\n\n\n\n' % JournalEntry))

                            self.create_journal_entry(JournalEntry)

            else:
                raise UserError("Empty Data")
                _logger.warning(_('Empty data'))

    def create_journal_entry(self, rec):

        journal_entry = {}
        if rec.get('Id'):
            _logger.info("PROCESSING JournalEntry NUMBER : %s", rec.get('Id'))

        journal_id = self.journal_entry
        journal_entry['journal_id'] = journal_id.id

        journal_object = self.env['account.move'].search([('qbo_invoice_id', '=', rec.get('Id')),
                                                          ('company_id',
                                                           '=', self.id),
                                                          ('move_type',
                                                           '=', 'entry')
                                                          ], limit=1)
        _logger.info('Journal Object : %s %s %s' %
                     (journal_object, rec, rec.get('Id')))
        if not journal_object:
            journal_entry['move_type'] = 'entry'  # For Journal

            if 'PrivateNote' in rec and rec.get('PrivateNote'):
                journal_entry['ref'] = rec.get('PrivateNote')

            if 'Id' in rec and rec.get('Id'):
                journal_entry['qbo_invoice_id'] = rec.get('Id')

            if 'TxnDate' in rec and rec.get('TxnDate'):
                journal_date = rec.get('TxnDate')
                journal_entry['date'] = journal_date

            journal_entry['line_ids'] = []

            if 'Line' in rec and rec.get('Line'):

                for line in rec.get('Line'):
                    line_ids = self.create_journal_line_entries(line, rec,
                                                                lineAmountType=rec.get(
                                                                    'LineAmountTypes'),
                                                                rec_id=rec.get('Id'))
                    if line_ids:
                        currency_id = self.env['res.currency'].browse(
                            line_ids.get('currency_id'))
                        if currency_id:
                            balance = line_ids.get('amount_currency')
                            balance = currency_id._convert(balance,
                                                           self.currency_id,
                                                           self,
                                                           fields.Date.today()
                                                           )
                            _logger.info(
                                'Balance=======================' + str(balance))
                            line_ids['debit'] = balance > 0 and balance or 0.0
                            line_ids['credit'] = balance < 0 and - \
                                balance or 0.0
                        journal_entry['line_ids'].append((0, 0, line_ids))

                account_journal_id = self.env[
                    'account.move'].create(journal_entry)
                account_journal_id.action_post()
                self._cr.commit()
                self.quickbooks_last_journal_entry_imported_id = account_journal_id.qbo_invoice_id
                _logger.info(
                    '%s Journal Imported Successfully....' % rec.get('ID'))
        else:
            _logger.info('%s Journal Already Imported ....' % rec.get('ID'))

    def create_journal_line_entries(self, line, rec={}, lineAmountType=None, rec_id=None, account_id=None, is_tax=0):

        line_ids = {}
        account_obj = self.env['account.account']

        if line.get('Description'):
            line_ids['name'] = line.get('Description')
        else:
            line_ids['name'] = 'None'
            # raise ValidationError('Description missing at line level (QBO Record Id : {}) and line : {}'.format(rec_id, line))

        if is_tax == 0:
            if lineAmountType == "Inclusive":
                if line.get('LineAmount') > 0:
                    line_ids['debit'] = abs(
                        line.get('LineAmount')) - abs(line.get('TaxAmount'))
                else:
                    line_ids['credit'] = abs(
                        line.get('LineAmount')) - abs(line.get('TaxAmount'))
            else:
                if 'JournalEntryLineDetail' in line:
                    if line.get('JournalEntryLineDetail').get('PostingType') == 'Debit':
                        line_ids['debit'] = abs(line.get('Amount'))
                    elif line.get('JournalEntryLineDetail').get('PostingType') == 'Credit':
                        line_ids['credit'] = abs(line.get('Amount'))
        else:
            if 'JournalEntryLineDetail' in line:
                if line.get('JournalEntryLineDetail').get('PostingType') == 'Debit':
                    line_ids['debit'] = line.get('Amount')
                elif line.get('JournalEntryLineDetail').get('PostingType') == 'Credit':
                    line_ids['credit'] = abs(line.get('Amount'))

        if rec.get('CurrencyRef').get('value') != self.currency_id.name:
            if 'JournalEntryLineDetail' in line:
                if line.get('JournalEntryLineDetail').get('PostingType') == 'Debit':
                    line_ids['amount_currency'] = -1 * abs(line.get('Amount'))
                if line.get('JournalEntryLineDetail').get('PostingType') == 'Credit':
                    line_ids['amount_currency'] = abs(line.get('Amount'))

            if rec.get('CurrencyRef').get('value'):
                currency = self.env['res.currency'].search(
                    [('name', '=', rec.get('CurrencyRef').get('value'))], limit=1)
                line_ids['currency_id'] = currency.id
            if line_ids.get('credit'):
                del line_ids['credit']
            if line_ids.get('debit'):
                del line_ids['debit']
        if account_id is None:
            if 'JournalEntryLineDetail' in line:
                account_id = account_obj.search([('qbo_id', '=', line.get(
                    'JournalEntryLineDetail').get('AccountRef').get('value'))])

        if account_id:
            line_ids['account_id'] = account_id.id

        return line_ids

    def export_journal_entry_cron(self):
        invoices = self.env['account.move'].search([])
        if not invoices:
            raise UserError('There is no any record to be exported.')

        for inv in invoices:
            # print('\n\nInvoice : ', inv)
            if inv.move_type in ['entry']:
                inv.export_journal_entry()

##########################################################################
