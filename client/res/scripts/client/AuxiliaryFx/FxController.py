# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AuxiliaryFx/FxController.py
# Compiled at: 2012-04-06 12:55:19


class IAuxiliaryVehicleFx:

    def __init__(self, vehicle, fxManager):
        self._vehicle = vehicle
        self._fxManager = fxManager

    def destroy(self):
        pass

    def executeShotEffect(self):
        pass

    def executeHitEffect(self):
        pass

    def update(self, vehicle):
        pass


class AuxiliaryFxController:

    def __init__(self, fxControllers):
        self.__controllers = fxControllers

    def destroy(self):
        for controller in self.__controllers:
            controller.destroy()

        self.__controllers = None
        return

    def executeShotEffect(self):
        for controller in self.__controllers:
            controller.executeShotEffect()

    def executeHitEffect(self):
        for controller in self.__controllers:
            controller.executeHitEffect()

    def update(self, vehicle):
        for controller in self.__controllers:
            controller.update(vehicle)
