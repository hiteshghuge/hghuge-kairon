from typing import Text

from kairon.chat.handlers.channels.business_messages import BusinessMessagesHandler
from kairon.chat.handlers.channels.hangouts import HangoutsHandler
from kairon.chat.handlers.channels.messenger import MessengerHandler, InstagramHandler
from kairon.chat.handlers.channels.msteams import MSTeamsHandler
from kairon.chat.handlers.channels.slack import SlackHandler
from kairon.chat.handlers.channels.telegram import TelegramHandler
from kairon.chat.handlers.channels.whatsapp import WhatsappHandler
from kairon.chat.handlers.channels.line import LineHandler
from kairon.shared.constants import ChannelTypes


class ChannelHandlerFactory:

    __implementations = {
        ChannelTypes.WHATSAPP.value: WhatsappHandler,
        ChannelTypes.HANGOUTS.value: HangoutsHandler,
        ChannelTypes.SLACK.value: SlackHandler,
        ChannelTypes.MESSENGER.value: MessengerHandler,
        ChannelTypes.MSTEAMS.value: MSTeamsHandler,
        ChannelTypes.TELEGRAM.value: TelegramHandler,
        ChannelTypes.INSTAGRAM.value: InstagramHandler,
        ChannelTypes.BUSINESS_MESSAGES.value: BusinessMessagesHandler,
        ChannelTypes.LINE.value: LineHandler
    }

    @staticmethod
    def get_handler(channel: Text):
        return ChannelHandlerFactory.__implementations[channel]
