# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/SoundManagerMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class SoundManagerMeta(DAAPIModule):

    def soundEventHandler(self, group, state, type, id):
        self._printOverrideError('soundEventHandler')
