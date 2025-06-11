# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Helpers/CallbackHelpers.py
# Compiled at: 2010-05-19 05:06:42
"""This module contains a number of helper functions intended simplify
implementing callback functions in a safe way.
"""
import BigWorld

def IgnoreCallbackIfDestroyed(function):

    def checkIfDestroyed(self, *args, **kwargs):
        assert isinstance(self, BigWorld.Entity)
        return function(self, *args, **kwargs) if not self.isDestroyed else None

    return checkIfDestroyed
