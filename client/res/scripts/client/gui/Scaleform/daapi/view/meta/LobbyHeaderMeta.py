# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LobbyHeaderMeta.py
# Compiled at: 2014-11-13 03:22:46
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class LobbyHeaderMeta(DAAPIModule):

    def menuItemClick(self, alias):
        self._printOverrideError('menuItemClick')

    def showLobbyMenu(self):
        self._printOverrideError('showLobbyMenu')

    def showExchangeWindow(self):
        self._printOverrideError('showExchangeWindow')

    def showExchangeXPWindow(self):
        self._printOverrideError('showExchangeXPWindow')

    def showPremiumDialog(self):
        self._printOverrideError('showPremiumDialog')

    def onPayment(self):
        self._printOverrideError('onPayment')

    def showSquad(self):
        self._printOverrideError('showSquad')

    def fightClick(self, mapID, actionName):
        self._printOverrideError('fightClick')

    def as_setScreenS(self, alias):
        return self.flashObject.as_setScreen(alias) if self._isDAAPIInited() else None

    def as_creditsResponseS(self, credits):
        return self.flashObject.as_creditsResponse(credits) if self._isDAAPIInited() else None

    def as_goldResponseS(self, gold):
        return self.flashObject.as_goldResponse(gold) if self._isDAAPIInited() else None

    def as_doDisableNavigationS(self):
        return self.flashObject.as_doDisableNavigation() if self._isDAAPIInited() else None

    def as_doDisableHeaderButtonS(self, btnId, isEnabled):
        return self.flashObject.as_doDisableHeaderButton(btnId, isEnabled) if self._isDAAPIInited() else None

    def as_updateSquadS(self, isInSquad):
        return self.flashObject.as_updateSquad(isInSquad) if self._isDAAPIInited() else None

    def as_nameResponseS(self, fullName, name, clan, isTeamKiller, isClan):
        return self.flashObject.as_nameResponse(fullName, name, clan, isTeamKiller, isClan) if self._isDAAPIInited() else None

    def as_setClanEmblemS(self, tID):
        return self.flashObject.as_setClanEmblem(tID) if self._isDAAPIInited() else None

    def as_setPremiumParamsS(self, isPremiumAccount, btnLabel, doLabel, isYear, disableTTHeader, disableTTBody):
        return self.flashObject.as_setPremiumParams(isPremiumAccount, btnLabel, doLabel, isYear, disableTTHeader, disableTTBody) if self._isDAAPIInited() else None

    def as_updateBattleTypeS(self, battleTypeName, battleTypeIcon, isEnabled):
        return self.flashObject.as_updateBattleType(battleTypeName, battleTypeIcon, isEnabled) if self._isDAAPIInited() else None

    def as_setServerS(self, name):
        return self.flashObject.as_setServer(name) if self._isDAAPIInited() else None

    def as_setWalletStatusS(self, walletStatus):
        return self.flashObject.as_setWalletStatus(walletStatus) if self._isDAAPIInited() else None

    def as_setFreeXPS(self, freeXP, useFreeXP):
        return self.flashObject.as_setFreeXP(freeXP, useFreeXP) if self._isDAAPIInited() else None

    def as_disableFightButtonS(self, isDisabled, toolTip):
        return self.flashObject.as_disableFightButton(isDisabled, toolTip) if self._isDAAPIInited() else None

    def as_setFightButtonS(self, label):
        return self.flashObject.as_setFightButton(label) if self._isDAAPIInited() else None

    def as_setCoolDownForReadyS(self, value):
        return self.flashObject.as_setCoolDownForReady(value) if self._isDAAPIInited() else None

    def as_showBubbleTooltipS(self, message, duration):
        return self.flashObject.as_showBubbleTooltip(message, duration) if self._isDAAPIInited() else None
