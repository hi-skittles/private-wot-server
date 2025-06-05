# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/html/__init__.py
# Compiled at: 2012-03-03 08:49:06
from debug_utils import LOG_CURRENT_EXCEPTION
from helpers import i18n
import re
_getText_re = re.compile('\\_\\(([^)]+)\\)', re.U | re.M)

def _search(match):
    return i18n.makeString(match.group(1)) if match.group(1) else ''


def escape(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')


def translation(text):
    result = text
    try:
        try:
            result = _getText_re.sub(_search, text)
        except re.error:
            LOG_CURRENT_EXCEPTION()

    finally:
        return result
