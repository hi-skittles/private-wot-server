# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/economics.py
# Compiled at: 2015-02-03 01:48:09


def getActionPrc(price, defaultPrice):

    def calculate(price, defaultPrice):
        return 0 if defaultPrice == 0 or price == defaultPrice else int(round((1 - float(price) / defaultPrice) * 100))

    if isinstance(price, tuple):
        goldPrc = calculate(price[1], defaultPrice[1])
        creditPrc = calculate(price[0], defaultPrice[0])
        return goldPrc or creditPrc
    return calculate(price, defaultPrice)


def calcRentPackages(vehicle, proxy):
    result = []
    if proxy is not None and vehicle.isRentable:
        rentCost = proxy.shop.getVehicleRentPrices().get(vehicle.intCD, {})
        defaultRentCost = proxy.shop.defaults.getVehicleRentPrices().get(vehicle.intCD, {})
        if len(rentCost) and len(defaultRentCost) is not None:
            for key in sorted(rentCost.keys()):
                rentPrice = rentCost[key].get('cost', (0, 0))
                defaultRentPrice = defaultRentCost.get(key, {}).get('cost', rentPrice)
                result.append({'days': key,
                 'rentPrice': rentPrice,
                 'defaultRentPrice': defaultRentPrice})

    return result
