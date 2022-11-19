from odoo import http, _
from odoo.http import request
import requests
import base64
import json
import logging
from datetime import datetime, timedelta

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class Custom_Quickbook_controller(http.Controller):

    @http.route('/get_auth_code', type="http", auth="public", website=True)
    def get_auth_code(self, **kwarg):
        '''Get access Token and store in object'''

        flag = False
        _logger.info('------------------ {}'.format(kwarg))
        if kwarg.get('code'):
            company_id = http.request.env['res.users'].sudo().search([('id', '=', http.request.uid)],
                                                                       limit=1).company_id
            _logger.info('Company Id ------------------ {}'.format(company_id))
            if company_id:
                company_id.write({
                    'auth_code': kwarg.get('code'),
                    'realm_id': kwarg.get('realmId')
                })
                request._cr.commit()

                client_id = company_id.client_id
                client_secret = company_id.client_secret
                redirect_uri = company_id.request_token_url

                raw_b64 = str(client_id) + ":" + str(client_secret)
                raw_b64 = raw_b64.encode('utf-8')
                converted_b64 = base64.b64encode(raw_b64).decode('utf-8')
                auth_header = 'Basic ' + converted_b64
                headers = {}
                headers['Authorization'] = str(auth_header)
                headers['accept'] = 'application/json'
                payload = {
                    'code': str(kwarg.get('code')),
                    'redirect_uri': redirect_uri,
                    'grant_type': 'authorization_code'
                }

                access_token = requests.post(company_id.access_token_url, data=payload, headers=headers)
                if access_token:
                    parsed_token_response = json.loads(access_token.text)
                    if parsed_token_response:
                        company_id.write({
                            'access_token': parsed_token_response.get('access_token'),
                            'qbo_refresh_token': parsed_token_response.get('refresh_token'),
                            'access_token_expire_in': datetime.now() + timedelta(
                                seconds=parsed_token_response.get('expires_in')),
                            'refresh_token_expire_in': datetime.now() + timedelta(
                                seconds=parsed_token_response.get('x_refresh_token_expires_in'))
                        })

                        request._cr.commit()
                        _logger.info(_("Authorized successfully...!!"))
                        flag = True
        if flag:
            return "Authenticated Successfully..!! \n You can close this window now"
        else:
            return "Something went wrong, Authentication was not completed Successfully..!!"

