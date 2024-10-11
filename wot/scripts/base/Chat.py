from bwdebug import DEBUG_MSG


class Chat(object):
    def __init__(self):
        pass

    def ackCommand(self, INT64, UINT8, FLOAT64, INT64_2, INT64_3):
        # exposed
        DEBUG_MSG('Chat::ackCommand: %i %i %f %i %i' % (INT64, UINT8, FLOAT64, INT64_2, INT64_3))
        pass


    def chatCommandFromClient(self, requestID, commandIndex, channelID, INT64, INT16, STRING1, STRING2):
        # exposed
        DEBUG_MSG('Chat::chatCommandFromClient: %i %i %i %i %i %s %s' % (requestID, commandIndex, channelID, INT64, INT16, STRING1, STRING2))
        pass

