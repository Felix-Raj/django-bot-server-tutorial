from django.core.exceptions import ObjectDoesNotExist
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import random
from django.utils.decorators import method_decorator
from django.http.response import HttpResponse
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from stats.models import BotUser, BotHit


def get_message_from_request(request):
    received_message = {}
    decoded_request = json.loads(request.body.decode('utf-8'))
    print(f'decoded_request {decoded_request}')

    if 'message' in decoded_request.keys():
        received_message = decoded_request['message']
        received_message['chat_id'] = received_message['from']['id']  # simply for easier reference
    elif 'callback_query' in decoded_request.keys():
        received_message = decoded_request.get('callback_query').get('message')
        received_message['chat_id'] = received_message.get('chat').get('id')
        received_message.update({'text': decoded_request.get('callback_query').get('data')})

    print(f'received_message {received_message}')
    return received_message


def send_messages(message, token):
    # Ideally process message in some way. For now, let's just respond
    jokes = {
        'stupid': ["""Yo' Mama is so stupid, she needs a recipe to make ice cubes.""",
                   """Yo' Mama is so stupid, she thinks DNA is the National Dyslexics Association."""],
        'fat': ["""Yo' Mama is so fat, when she goes to a restaurant, instead of a menu, she gets an estimate.""",
                """ Yo' Mama is so fat, when the cops see her on a street corner, they yell, "Hey you guys, break it up!" """],
        'dumb': ["""This is fun""",
                 """This isn't fun"""]
    }

    post_message_url = "https://api.telegram.org/bot{0}/sendMessage".format(token)

    result_message = {'chat_id': message[
        'chat_id']}  # the response needs to contain just a chat_id and text field for  telegram to accept it
    if 'fat' in message['text']:
        result_message['text'] = random.choice(jokes['fat'])

    elif 'stupid' in message['text']:
        result_message['text'] = random.choice(jokes['stupid'])

    elif 'dumb' in message['text']:
        result_message['text'] = random.choice(jokes['dumb'])

    else:
        result_message[
            'text'] = "I don't know any responses for that. If you're interested in yo mama jokes tell me fat, stupid or dumb."
        result_message['reply_markup'] = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('Fat', callback_data='fat'),
                InlineKeyboardButton('Stupid', callback_data='stupid'),
                InlineKeyboardButton('Dumb', callback_data='dumb')
            ]
        ]).to_dict()

    response_msg = json.dumps(result_message)
    print(f'response message {response_msg}')
    status = requests.post(post_message_url, headers={
        "Content-Type": "application/json"}, data=response_msg)


def update_stats(request):
    decoded_request = json.loads(request.body.decode('utf-8'))
    print(f'update_stats, decoded_request {decoded_request}')

    if 'callback_query' in decoded_request.keys():
        callback_query = decoded_request.get('callback_query')
        user = callback_query.get('from')
        username = user.get('username')
        user_id = user.get('id')
        button = decoded_request.get('callback_query').get('data')
        bot_user, _ = BotUser.objects.get_or_create(
            user_id=user_id, username=username
        )
        try:
            bot_hit = BotHit.objects.get(user=bot_user, button=button)
        except ObjectDoesNotExist:
            bot_hit = BotHit(user=bot_user, button=button, count=0)
            bot_hit.save()

        bot_hit.count += 1
        bot_hit.save()


class TelegramBotView(generic.View):

    # csrf_exempt is necessary because the request comes from the Telegram server.
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle messages in whatever format they come
    def post(self, request, *args, **kwargs):
        TELEGRAM_TOKEN = 'PASTE_TOKEN'
        update_stats(request)
        message = get_message_from_request(request)
        send_messages(message, TELEGRAM_TOKEN)

        return HttpResponse()
