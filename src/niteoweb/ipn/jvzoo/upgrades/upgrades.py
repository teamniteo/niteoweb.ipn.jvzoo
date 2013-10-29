# -*- coding: utf-8 -*-
"""Upgrade steps for addon niteoweb.ipn.jvzoo."""


def upgrade_1_to_2(context):
    """Upgrade steps for version 1.5"""
    context.runImportStepFromProfile(
        'profile-niteoweb.ipn.jvzoo:default', 'memberdata-properties'
    )
