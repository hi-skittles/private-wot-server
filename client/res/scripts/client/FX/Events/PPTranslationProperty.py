# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Events/PPTranslationProperty.py
# Compiled at: 2010-08-25 08:58:21
from FX.Event import Event
from FX.Event import IMMEDIATE_EVENT
from FX import s_sectionProcessors
import BigWorld
import PostProcessing
import Math
from bwdebug import *

class PPTranslationProperty(Event):
    """
    This class implements an Event that gets the world position
    of the SFX source, and sets it on a post-processing chain actor.
    """

    def load(self, pSection, prereqs=None):
        self.propName = pSection.asString
        return self

    def go(self, effect, actor, source, target, **kargs):
        duration = effect.totalDuration
        try:
            self.v4 = Math.Vector4Translation(source.root)
        except:
            try:
                self.v4 = Math.Vector4Translation(source.model.root)
            except:
                self.v4 = Math.Vector4Translation(source.source)

        PostProcessing.setMaterialProperty(actor, self.propName, self.v4)
        return duration

    def stop(self, actor, source, target):
        pass

    def duration(self, actor, source, target):
        pass

    def eventTiming(self):
        return IMMEDIATE_EVENT


s_sectionProcessors['PPTranslationProperty'] = PPTranslationProperty
