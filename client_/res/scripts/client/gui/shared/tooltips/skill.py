# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/skill.py
# Compiled at: 2013-12-10 09:18:08
from gui.shared.tooltips import TOOLTIP_TYPE, ToolTipData, ToolTipAttrField

class SkillTooltipData(ToolTipData):

    def __init__(self, context):
        super(SkillTooltipData, self).__init__(context, TOOLTIP_TYPE.SKILL)
        self.fields = (ToolTipAttrField(self, 'name', 'userName'),
         ToolTipAttrField(self, 'shortDescr', 'shortDescription'),
         ToolTipAttrField(self, 'descr', 'description'),
         ToolTipAttrField(self, 'level'),
         ToolTipAttrField(self, 'type'),
         ToolTipAttrField(self, 'count'))
