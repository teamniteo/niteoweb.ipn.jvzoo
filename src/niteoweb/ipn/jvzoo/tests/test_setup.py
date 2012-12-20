# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from niteoweb.ipn.jvzoo.testing import IntegrationTestCase
from Products.CMFCore.utils import getToolByName
from AccessControl import Unauthorized
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import getMultiAdapter
from plone.app.testing import logout

import unittest2 as unittest


class TestInstall(IntegrationTestCase):
    """Test installation of niteoweb.ipn.jvzoo into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = getToolByName(self.portal, 'portal_quickinstaller')

    def test_product_installed(self):
        """Test if niteoweb.ipn.jvzoo is installed in portal_quickinstaller."""
        self.failUnless(
            self.installer.isProductInstalled('niteoweb.ipn.jvzoo'))

    def test_uninstall(self):
        """Test if niteoweb.ipn.jvzoo is cleanly uninstalled."""
        self.installer.uninstallProducts(['niteoweb.ipn.jvzoo'])
        self.failIf(self.installer.isProductInstalled('niteoweb.ipn.jvzoo'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that INiteowebIpnJvzooLayer is registered."""
        from niteoweb.ipn.jvzoo.interfaces import INiteowebIpnJvzooLayer
        from plone.browserlayer import utils
        self.failUnless(INiteowebIpnJvzooLayer in utils.registered_layers())

    # controlpanel.xml
    def test_jvzoo_controlpanel_available(self):
        """Test if jvzoo control panel configlet is available."""
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST),
            name="jvzoo-settings"
        )
        view = view.__of__(self.portal)
        self.assertTrue(view())

    # browser/configure.zcml
    def test_jvzoo_controlpanel_view_protected(self):
        """Check that access to jvzoo settings is restricted."""
        logout()
        with self.assertRaises(Unauthorized):
            self.portal.restrictedTraverse('@@jvzoo-settings')

    # registry.xml
    def test_record_secretkey(self):
        """Test that the secretkey record is in the registry."""
        registry = getUtility(IRegistry)
        record_secretkey = registry.records[
            'niteoweb.ipn.jvzoo.interfaces.IJVZooSettings.secretkey']

        from niteoweb.ipn.jvzoo.interfaces import IJVZooSettings
        self.assertIn('secretkey', IJVZooSettings)
        self.assertEquals(record_secretkey.value, None)


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above."""
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
