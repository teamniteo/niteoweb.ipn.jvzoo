# -*- coding: utf-8 -*-
"""Test all aspects of the @@jvzoo view."""

from niteoweb.ipn.jvzoo.testing import IntegrationTestCase
from plone import api
from zope.testing.loggingsupport import InstalledHandler

import mock

log = InstalledHandler('niteoweb.ipn.jvzoo')

KEY_RECORD = 'niteoweb.ipn.jvzoo.interfaces.IJVZooSettings.secretkey'


class TestJVZoo(IntegrationTestCase):
    """Test runtime flow through @@jvzoo."""

    def setUp(self):
        """Prepare testing environment."""
        self.portal = self.layer['portal']
        self.view = self.portal.restrictedTraverse('jvzoo')

    def tearDown(self):
        """Clean up after yourself."""
        log.clear()

    def _assert_log_record(self, level, msg):
        """Utility method for testing log output."""
        self.assertEqual(log.records[0].name, 'niteoweb.ipn.jvzoo')
        self.assertEqual(log.records[0].levelname, level)
        self.assertEqual(log.records[0].getMessage(), msg,)
        log.records.pop(0)

    def test_call_with_no_POST(self):
        """Test @@jvzoo's response when POST is empty."""
        html = self.view()
        self.failUnless('No POST request.' in html)
        self._assert_log_record('WARNING', 'No POST request.')

    def test_call_with_missing_parameter(self):
        """Test @@jvzoo's response when POST is missing a parameter."""

        # put something into self.request.form so it's not empty
        self.portal.REQUEST.form = dict(foo='bar')

        # set secretkey
        api.portal.set_registry_record(KEY_RECORD, u'secret')

        # test html
        html = self.view()
        self.assertEqual(html, "POST parameter missing: 'cverify'")

        # test log output
        self.assertEqual(len(log.records), 1)
        self._assert_log_record(
            'WARNING',
            "POST parameter missing: 'cverify'",
        )

    def test_call_with_missing_secret_key(self):
        """Test @@jvzoo's response when JVZoo secret-key is not set."""

        # put something into self.request.form so it's not empty
        self.portal.REQUEST.form = dict(foo='bar')

        # test html
        html = self.view()
        self.assertEqual(
            html, "POST handling failed: JVZoo secret-key is not set.")

        # test log output
        self.assertEqual(len(log.records), 1)
        self._assert_log_record(
            'WARNING',
            "POST handling failed: JVZoo secret-key is not set.",
        )

    @mock.patch('niteoweb.ipn.jvzoo.browser.jvzoo.JVZoo._verify_POST')
    def test_call_with_invalid_checksum(self, verify_post):
        """Test @@jvzoo's response when checksum cannot be verified."""

        # put something into self.request.form so it's not empty
        self.portal.REQUEST.form = dict(foo='bar')

        # mock return from _verify_POST
        verify_post.side_effect = AssertionError

        # test html
        html = self.view()
        self.assertEqual(html, 'Checksum verification failed.')

        # test log output
        self.assertEqual(len(log.records), 1)
        self._assert_log_record(
            'WARNING',
            "Checksum verification failed.",
        )

    @mock.patch('niteoweb.ipn.jvzoo.browser.jvzoo.JVZoo._verify_POST')
    def test_call_with_internal_exception(self, verify_post):
        """Test @@jvzoo's response when there is an internal problem."""

        # put something into self.request.form so it's not empty
        self.portal.REQUEST.form = dict(foo='bar')

        # mock return from _verify_POST
        verify_post.side_effect = Exception('Internal foo.')

        # test html
        html = self.view()
        self.assertEqual(html, 'POST handling failed: Internal foo.')

        # test log output
        self.assertEqual(len(log.records), 1)
        self._assert_log_record(
            'WARNING',
            "POST handling failed: Internal foo.",
        )

    @mock.patch('niteoweb.ipn.jvzoo.browser.jvzoo.JVZoo._verify_POST')
    @mock.patch('niteoweb.ipn.jvzoo.browser.jvzoo.JVZoo._parse_POST')
    def test_call_with_valid_POST(self, parse_post, verify_post):
        """Test @@jvzoo's response when POST is valid."""

        # put something into self.request.form so it's not empty
        self.portal.REQUEST.form = dict(value='non empty value')

        # mock post handling
        verify_post.return_value = True
        parse_post.return_value = dict(
            email='jsmith@email.com',
            transaction_type='SALE'
        )

        # test html
        html = self.view()
        self.assertEqual('Done.', html)

        # test log output
        self.assertEqual(len(log.records), 2)

        self._assert_log_record(
            'INFO',
            "POST successfully parsed for 'jsmith@email.com'.",
        )

        self._assert_log_record(
            'INFO',
            "Calling 'enable_member' in niteoweb.ipn.core.",
        )


class TestTransactionTypesToActionsMapping(TestJVZoo):
    """Test how Transaction Types map to niteoweb.ipn.core actions."""

    @mock.patch('niteoweb.ipn.jvzoo.browser.jvzoo.JVZoo._verify_POST')
    @mock.patch('niteoweb.ipn.jvzoo.browser.jvzoo.JVZoo._parse_POST')
    def _simulate_transaction(self, parse_post, verify_post, ttype=None):
        """Simulate a transaction of a certain type from JVZoo."""

        # put something into self.request.form so it's not empty
        self.portal.REQUEST.form = dict(value='non empty value')

        verify_post.return_value = True
        parse_post.return_value = dict(
            email='jsmith@email.com',
            transaction_type=ttype,
        )

        html = self.view()
        self.assertEqual(len(log.records), 2)
        self.assertEqual('Done.', html)

    def test_SALE(self):
        """Test SALE Transaction Type."""
        self._simulate_transaction(ttype='SALE')

        # test log output
        msg = log.records[1].getMessage()
        self.assertEqual(msg, "Calling 'enable_member' in niteoweb.ipn.core.")

    def test_BILL(self):
        """Test BILL Transaction Type."""
        self._simulate_transaction(ttype='BILL')

        # test log output
        msg = log.records[1].getMessage()
        self.assertEqual(msg, "Calling 'enable_member' in niteoweb.ipn.core.")

    def test_RFND(self):
        """Test RFND Transaction Type."""
        self._simulate_transaction(ttype='RFND')

        # test log output
        msg = log.records[1].getMessage()
        self.assertEqual(msg, "Calling 'disable_member' in niteoweb.ipn.core.")

    def test_CGBK(self):
        """Test CGBK Transaction Type."""
        self._simulate_transaction(ttype='CGBK')

        # test log output
        msg = log.records[1].getMessage()
        self.assertEqual(msg, "Calling 'disable_member' in niteoweb.ipn.core.")

    def test_INSF(self):
        """Test INSF Transaction Type."""
        self._simulate_transaction(ttype='INSF')

        # test log output
        msg = log.records[1].getMessage()
        self.assertEqual(msg, "Calling 'disable_member' in niteoweb.ipn.core.")

    def test_CANCEL_REBILL(self):
        """Test CANCEL-REBILL Transaction Type."""
        self._simulate_transaction(ttype='CANCEL-REBILL')

        # test log output
        msg = log.records[1].getMessage()
        self.assertEqual(msg, "Calling 'disable_member' in niteoweb.ipn.core.")

    def test_UNCANCEL_REBILL(self):
        """Test UNCANCEL-REBILL Transaction Type."""
        self._simulate_transaction(ttype='UNCANCEL-REBILL')

        # test log output
        msg = log.records[1].getMessage()
        self.assertEqual(msg, "Calling 'enable_member' in niteoweb.ipn.core.")


class TestUtils(IntegrationTestCase):
    """Test utility methods in @@jvzoo."""

    def setUp(self):
        """Prepare testing environment."""
        self.portal = self.layer['portal']
        self.view = self.portal.restrictedTraverse('jvzoo')

    def test_verify_POST(self):
        """Test POST verification process."""
        params = dict(
            secretkey='secret',
            ccustname='fullname',
            cverify='38CFCDED',
        )
        self.view._verify_POST(params)
        self.assertTrue(True)

    def test_parse_POST(self):
        """Test that POST parameters are correctly mirrored into member
        fields.
        """
        post_params = dict(
            ccustname='fullname',
            ccustemail='email',
            ctransreceipt='payment_id',
            cproditem='product_id',
            cprodtitle='product_name',
            ctransaffiliate='affiliate',
            ctransaction='SALE',
        )

        expected = dict(
            fullname=u'fullname',
            email='email',
            product_id='product_id',
            product_name='product_name',
            affiliate='affiliate',
            payment_id='payment_id',
            transaction_type='SALE',
        )

        result = self.view._parse_POST(post_params)
        self.assertEqual(result, expected)
