# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/validators.py
# Compiled at: 2014-10-25 11:58:42
from gui.shared.fortifications import isFortificationEnabled

def questHasThisAchievementAsBonus(name, block):
    from gui.server_events import g_eventsCache
    for records in g_eventsCache.getQuestsDossierBonuses().itervalues():
        if (block, name) in records:
            return True

    return False


def alreadyAchieved(achievementClass, name, block, dossier):
    return achievementClass.checkIsInDossier(block, name, dossier)


def requiresFortification():
    return isFortificationEnabled()


def accountIsRoaming(dossier):
    return dossier.isInRoaming()
