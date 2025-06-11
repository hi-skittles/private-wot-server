# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/xmpp/xmpp_string_utils.py
# Compiled at: 2014-12-20 09:27:53
from external_strings_utils import unicode_from_utf8
from messenger.proto.xmpp.errors import ClientContactError, ClientIntLimitError
from messenger.proto.xmpp.xmpp_constants import CONTACT_LIMIT, CONTACT_ERROR_ID, LIMIT_ERROR_ID
from messenger.proto.xmpp.xmpp_string_grep import ResourcePrep
from messenger.proto.xmpp.xmpp_string_grep import XmppStringPrepError

def validateRosterItemGroup(name):
    if not name:
        return ('', ClientContactError(CONTACT_ERROR_ID.GROUP_EMPTY))
    else:
        try:
            name = ResourcePrep.prepare(name)
        except XmppStringPrepError:
            return ('', ClientContactError(CONTACT_ERROR_ID.GROUP_INVALID_NAME, name))

        length = len(name)
        return (name.encode('utf-8'), ClientIntLimitError(LIMIT_ERROR_ID.GROUP_INVALID_LENGTH, CONTACT_LIMIT.GROUP_MIN_LENGTH, CONTACT_LIMIT.GROUP_MAX_LENGTH)) if CONTACT_LIMIT.GROUP_MIN_LENGTH > length or CONTACT_LIMIT.GROUP_MAX_LENGTH < length else (name.encode('utf-8'), None)


def validateContactNote(note):
    if not note:
        return ('', ClientContactError(CONTACT_ERROR_ID.NOTE_EMPTY))
    else:
        return (note, ClientIntLimitError(LIMIT_ERROR_ID.NOTE_INVALID_LENGTH, CONTACT_LIMIT.NOTE_MIN_CHARS_COUNT, CONTACT_LIMIT.NOTE_MAX_CHARS_COUNT)) if len(unicode_from_utf8(note)[0]) not in xrange(CONTACT_LIMIT.NOTE_MIN_CHARS_COUNT, CONTACT_LIMIT.NOTE_MAX_CHARS_COUNT + 1) else (note, None)
