# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/custom/__init__.py
# Compiled at: 2013-08-30 21:11:30


def init():
    from dossiers2.custom.cache import buildCache
    buildCache()
    from dossiers2.custom.dependencies import init as dependencies_init
    dependencies_init()
