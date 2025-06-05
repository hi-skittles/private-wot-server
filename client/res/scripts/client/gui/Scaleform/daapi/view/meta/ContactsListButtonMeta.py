# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ContactsListButtonMeta.py
# Compiled at: 2014-05-24 06:53:35
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ContactsListButtonMeta(DAAPIModule):

    def as_setContactsCountS(self, num):
        return self.flashObject.as_setContactsCount(num) if self._isDAAPIInited() else None
