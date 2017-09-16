import datetime
import time
import hmac
import hashlib
from copy import deepcopy
import json

from tapioca import (
    TapiocaAdapter, JSONAdapterMixin, generate_wrapper_from_adapter)
from tapioca.tapioca import TapiocaClient, TapiocaInstantiator, TapiocaClientExecutor

from .resource_mapping import RESOURCE_MAPPING, MESSAGE_TYPES, PUBLIC_RESOURCE_MAPPING


class BlinkTradeClientAdapter(JSONAdapterMixin, TapiocaAdapter):
    resource_mapping = RESOURCE_MAPPING

    def get_api_root(self, api_params):
        return '%s/tapi/v1/message' % api_params['api_url']

    def get_nonce(self):
        dt = datetime.datetime.now()
        return str(int((time.mktime(dt.timetuple()) + dt.microsecond / 1000000.0) * 1000000)
                   ).encode('utf-8')

    def get_signature(self, api_params, nonce):
        secret = api_params['secret'].encode('utf-8')
        return hmac.new(secret, nonce, digestmod=hashlib.sha256).hexdigest()

    def get_headers(self, api_params):
        nonce = self.get_nonce()
        return {
            'user-agent': 'blinktrade_tools/0.1',
            # You must POST a JSON message
            'Content-Type': 'application/json',
            # Your APIKey
            'APIKey': api_params['key'],
            # The nonce must be an integer, always greater than the previous one.
            'Nonce': nonce,
            # Use the API Secret  to sign the nonce using HMAC_SHA256 algo
            'Signature': self.get_signature(api_params, nonce)
        }

    def format_data_to_request(self, data):
        if data:
            return data
        else:
            return {}

    def get_request_kwargs(self, api_params, *args, **kwargs):
        params = super(BlinkTradeClientAdapter, self).get_request_kwargs(
            api_params, *args, **kwargs)

        extra_data = params['data']
        resource = params.pop('resource')
        data = deepcopy(MESSAGE_TYPES[resource['message_type']])

        data.update(extra_data)
        params['data'] = json.dumps(data)

        params['headers'].update(self.get_headers(api_params))
        params['verify'] = True
        params['url'] = params['url'].rstrip('/')

        return params


class TapiocaBlinkTradeClient(TapiocaClient):
    def _wrap_in_tapioca_executor(self, data, *args, **kwargs):
        request_kwargs = kwargs.pop('request_kwargs', self._request_kwargs)
        return TapiocaBlinkTradeClientExecutor(
            self._instatiate_api(), data=data,
            api_params=self._api_params,
            request_kwargs=request_kwargs,
            refresh_token_by_default=self._refresh_token_default,
            refresh_data=self._refresh_data,
            session=self._session,
            *args, **kwargs)

    def _wrap_in_tapioca(self, data, *args, **kwargs):
        request_kwargs = kwargs.pop('request_kwargs', self._request_kwargs)
        return TapiocaBlinkTradeClient(
            self._instatiate_api(), data=data,
            api_params=self._api_params,
            request_kwargs=request_kwargs,
            refresh_token_by_default=self._refresh_token_default,
            refresh_data=self._refresh_data,
            session=self._session,
            *args, **kwargs)


class TapiocaBlinkTradeClientExecutor(TapiocaClientExecutor):
    def _make_request(self, request_method, refresh_token=None, *args, **kwargs):
        kwargs['resource'] = self._resource
        return super(TapiocaBlinkTradeClientExecutor, self)._make_request(
            request_method, refresh_token=refresh_token,
            *args, **kwargs)


class TapiocaBlinkTradeInstantiator(TapiocaInstantiator):
    def __call__(self, serializer_class=None, session=None, **kwargs):
        refresh_token_default = kwargs.pop('refresh_token_by_default', False)
        return TapiocaBlinkTradeClient(
            self.adapter_class(serializer_class=serializer_class),
            api_params=kwargs, refresh_token_by_default=refresh_token_default,
            session=session)


class BLinkTradePulbicAdapter(JSONAdapterMixin, TapiocaAdapter):
    resource_mapping = PUBLIC_RESOURCE_MAPPING

    def get_api_root(self, api_params):
        return '%s/api/v1/%s' % (api_params['api_url'], api_params['currency'])


BlinkTradePublic = generate_wrapper_from_adapter(BLinkTradePulbicAdapter)
BlinkTrade = TapiocaBlinkTradeInstantiator(BlinkTradeClientAdapter)
