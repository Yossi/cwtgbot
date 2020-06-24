from timezonefinder import TimezoneFinder

from utils import send
from .decorators import log, send_typing_action


@send_typing_action
@log
def location(update, context):
    tf = TimezoneFinder()
    latitude, longitude = update.effective_message.location.latitude, update.effective_message.location.longitude
    context.user_data['location'] = round(latitude, 3), round(longitude, 3)
    context.user_data.user_data['timezone'] = tf.timezone_at(lat=latitude, lng=longitude)
    text = f'Saving your location as {context.user_data["location"]} making your timezone be {context.user_data["timezone"]}'
    send(text, update, context)
