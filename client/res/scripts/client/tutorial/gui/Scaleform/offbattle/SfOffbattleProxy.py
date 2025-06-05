# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/gui/Scaleform/offbattle/SfOffbattleProxy.py
# Compiled at: 2013-07-28 12:08:50
from tutorial.gui import GUI_EFFECT_NAME
from tutorial.gui.Scaleform import effects_player
from tutorial.gui.Scaleform.lobby.SfLobbyProxy import SfLobbyProxy
from tutorial.gui.Scaleform.offbattle import settings

class SfOffbattleProxy(SfLobbyProxy):

    def __init__(self):
        effects = {GUI_EFFECT_NAME.SHOW_DIALOG: effects_player.ShowDialogEffect(settings.DIALOG_ALIAS_MAP),
         GUI_EFFECT_NAME.SHOW_WINDOW: effects_player.ShowWindowEffect(settings.WINDOW_ALIAS_MAP),
         GUI_EFFECT_NAME.UPDATE_CONTENT: effects_player.UpdateContentEffect()}
        super(SfOffbattleProxy, self).__init__(effects_player.EffectsPlayer(effects))

    def getViewSettings(self):
        return settings.OFFBATTLE_VIEW_SETTINGS
