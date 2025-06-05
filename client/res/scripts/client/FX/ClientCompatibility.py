# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/ClientCompatibility.py
# Compiled at: 2009-11-10 10:34:37
import BigWorld
if BigWorld.component == 'editor':

    def addMat(a, b):
        pass


    def delMat(a):
        pass


    BigWorld.addMat = addMat
    BigWorld.delMat = delMat

    def player():
        return None


    BigWorld.player = player
