# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from niteoweb.ipn.jvzoo.testing import IntegrationTestCase
from Products.CMFCore.utils import getToolByName

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


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above."""
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
