# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/VoiceChatManagerMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class VoiceChatManagerMeta(DAAPIModule):

    def isPlayerSpeaking(self, accountDBID):
        self._printOverrideError('isPlayerSpeaking')

    def isVivox(self):
        self._printOverrideError('isVivox')

    def isYY(self):
        self._printOverrideError('isYY')

    def isVOIPEnabled(self):
        self._printOverrideError('isVOIPEnabled')

    def as_onPlayerSpeakS(self, accountDBID, isSpeak, isHimself):
        return self.flashObject.as_onPlayerSpeak(accountDBID, isSpeak, isHimself) if self._isDAAPIInited() else None
