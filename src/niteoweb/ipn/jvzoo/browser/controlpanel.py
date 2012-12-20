# -*- coding: utf-8 -*-
"""JVZoo control panel configlet."""

from niteoweb.ipn.jvzoo import JVZooMessageFactory as _
from niteoweb.ipn.jvzoo.interfaces import IJVZooSettings
from plone.app.registry.browser import controlpanel


class JVZooSettingsEditForm(controlpanel.RegistryEditForm):
    """Form for configuring niteoweb.ipn.jvzoo."""

    schema = IJVZooSettings
    label = _(u"JVZoo settings")
    description = _(u"""Configure integration with JVZoo IPN.""")


class JVZooSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = JVZooSettingsEditForm
