# -*- coding: utf-8 -*-
"""The @@jvzoo view that handles JVZoo purchase notifications."""


from zope.component import getAdapter
from five import grok
from plone import api
from niteoweb.ipn.core.interfaces import IIPN
from niteoweb.ipn.jvzoo.interfaces import SecretKeyNotSet
from Products.CMFCore.interfaces import ISiteRoot

import hashlib
import logging

logger = logging.getLogger("niteoweb.ipn.jvzoo")


class JVZoo(grok.view):
    """A view for handling IPN POST requests from JVZOO."""

    grok.context(ISiteRoot)
    grok.require('zope2.View')

    def render(self):
        """Handler for JVZoo IPN POST requests."""
        # check for POST request
        if not self.request.form:
            return 'No POST request.'

        # prepare values
        params = dict(self.request.form)
        settings = api.portal.get_registry_record(
            'niteoweb.ipn.jvzoo.interfaces.IJVZooSettings')
        params['secretkey'] = settings.secretkey

        try:
            # verify and parse post
            self._verify_POST(params)
            data = self._parse_POST(params)

            # call action in niteoweb.ipn based on transaction type
            ipn = getAdapter(self.context, IIPN)
            if data['transaction_type'] in ['SALE', 'BILL', 'UNCANCEL-REBILL']:
                ipn.enable_member()
            elif data['transaction_type'] in ['RFND', 'CGBK',
                                              'INSF', 'CANCEL-REBILL']:
                # TODO: make the if clause above nicer ^^
                ipn.disable_member()
            else:
                raise Exception

        except KeyError as ex:
            msg = "POST parameter missing: %s" % ex
            logger.error(msg)
            return msg

        except AssertionError:
            msg = "Checksum verification failed."
            logger.error(msg)
            return msg

        except Exception as ex:
            msg = "POST handling failed: %s" % ex
            logger.error(msg)
            return msg

        return 'POST successfully parsed.'

    def _verify_POST(self, params):
        """Verifies if received POST is a valid JVZoo POST request.

        :param params: POST parameters sent by JVZoo Notification Service
        :type params: dict

        """
        if not params['secretkey']:
            raise SecretKeyNotSet('JVZoo secret-key is not set.')
        strparams = ""
        for key in iter(sorted(params.iterkeys())):
            if key in ['cverify', 'secretkey']:
                continue
            strparams += params[key] + "|"
        strparams += params['secretkey']
        sha = hashlib.sha1(strparams.encode('utf-8')).hexdigest().upper()
        assert params['cverify'] == sha[:8], 'Checksum verification failed.'

    def _parse_POST(self, params):
        """Parse POST from JVZoo and extract information we need.

        :param params: POST parameters sent by JVZoo Notification Service
        :type params: dict

        """
        return {
            'email': params['ccustemail'],
            'fullname': u"%s" % params['ccustname'].decode("utf-8"),
            'product_id': params['cproditem'],
            'product_name': params['cprodtitle'],
            'affiliate': params['ctransaffiliate'],
            'transaction_type': params['ctransaction'],
        }
