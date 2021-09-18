from bot_class import HotelBot, types
from flask import Flask, request
from dotenv import load_dotenv
from typing import Callable, Any
import api_requests as req
from loguru import logger
import functools
import os

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

server = Flask(__name__)
bot = HotelBot(TOKEN)
maps_url = 'https://www.google.com/maps/dir//{},{}'


@server.route('/' + TOKEN, methods=['POST'])
def getMessage() -> Any:
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook() -> Any:
    bot.remove_webhook()
    bot.set_webhook(url=os.getenv('WEBHOOK_LINK') + TOKEN)
    return "!", 200


def program_interrupt_decorator(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args):
        if bot.program_interrupt_handler(*args):
            bot.send_message(args[0].chat.id, '⏪ Возврат в главное меню...')
            bot.welcome_message(*args)
        else:
            return func(*args)

    return wrapper


@bot.message_handler(content_types=['text'], func=lambda message: message.text not in bot.commands)
def wrong_message_handler(message: types.Message) -> None:
    bot.wrong_input_message(message)


@bot.message_handler(
    content_types=['audio', 'photo', 'voice', 'video', 'document', 'location', 'contact', 'sticker'])
def wrong_message_type_handler(message: types.Message) -> None:
    logger.info(f'User {message.chat.id}. Sent incorrect message type')
    bot.wrong_input_message(message)


@bot.message_handler(commands=['start', 'help'])
def welcome_message(message: types.Message) -> None:
    logger.info(f'User {message.chat.id}. Sent {message.text} message')
    bot.welcome_message(message)


@bot.message_handler(commands=['lowprice'])
def lowprice_command(message: types.Message) -> None:
    logger.info(f'User {message.chat.id}. Sent {message.text} message')
    bot.sorting_type = 'PRICE'
    bot.send_message(message.chat.id, '🔎 Введите город для поиска: ')
    bot.register_next_step_handler(message, get_regions_dict)


@bot.message_handler(commands=['highprice'])
def lowprice_command(message: types.Message) -> None:
    logger.info(f'User {message.chat.id}. Sent {message.text} message')
    bot.sorting_type = 'PRICE_HIGHEST_FIRST'
    bot.send_message(message.chat.id, '🔎 Введите город для поиска: ')
    bot.register_next_step_handler(message, get_regions_dict)


@bot.message_handler(commands=['bestdeal'])
def lowprice_command(message: types.Message) -> None:
    logger.info(f'User {message.chat.id}. Sent {message.text} message')
    bot.sorting_type = 'BEST_SELLER'
    bot.send_message(message.chat.id, '🔎 Введите город для поиска: ')
    bot.register_next_step_handler(message, get_regions_dict)


@program_interrupt_decorator
def get_regions_dict(message: types.Message) -> None:
    logger.info(f'User {message.chat.id}. Sent {message.text} message')
    bot.send_message(message.chat.id, '🔎 Идет поиск регионов. Ожидайте...')
    bot.regions_dict = req.HotelApiRequests.regions_request(message.text)
    if bot.regions_inline_keyboard(message, bot.regions_dict):
        bot.register_next_step_handler(message, get_regions_dict)


@bot.callback_query_handler(func=lambda call: True)
def inline_keyboard_handler(call) -> None:
    if call.data in bot.regions_dict:
        bot.city_id = bot.regions_dict[call.data]
        if bot.sorting_type == 'BEST_SELLER':
            bot.send_message(call.message.chat.id, '🔎 Введите диапазон цен для поиска (мин-макс): ')
            bot.register_next_step_handler(call.message, get_prices_range)
        else:
            bot.send_message(call.message.chat.id, '🏨 Введите количество отелей для показа: ')
            bot.register_next_step_handler(call.message, hotels_count_max_check)


@program_interrupt_decorator
def get_prices_range(message: types.Message) -> None:
    logger.info(f'User {message.chat.id}. Sent {message.text} message')
    if bot.ranges_input_check(message, bot.prices_range_dict):
        bot.send_message(message.chat.id, '❌ Неверный ввод диапазона. Введите еще раз (мин-макс): ')
        bot.register_next_step_handler(message, get_prices_range)
    else:
        bot.send_message(message.chat.id, '🔎 Введите диапазон расстояния от центра для поиска в км (мин-макс): ')
        bot.register_next_step_handler(message, get_dist_range)


@program_interrupt_decorator
def get_dist_range(message: types.Message) -> None:
    logger.info(f'User {message.chat.id}. Sent {message.text} message')
    if bot.ranges_input_check(message, bot.dist_from_center_range_dict):
        bot.send_message(message.chat.id, '❌ Неверный ввод диапазона. Введите еще раз (мин-макс): ')
        bot.register_next_step_handler(message, get_dist_range)
    else:
        bot.send_message(message.chat.id, '🏨 Введите количество отелей для показа: ')
        bot.register_next_step_handler(message, hotels_count_max_check)


@program_interrupt_decorator
def hotels_count_max_check(message):
    if bot.has_cyrillic(message):
        logger.info(f'User {message.chat.id}. Cyrillic in int only input')
        bot.send_message(message.chat.id, '❌ Неверный ввод количества. Введите еще раз: ')
        bot.register_next_step_handler(message, hotels_count_max_check)
    elif int(message.text) > req.HotelApiRequests.max_hotels_count_to_request:
        logger.info(f'User {message.chat.id}. Sent more than max hotels to show')
        bot.send_message(message.chat.id, '❌ Максимальное количество отелей для показа: 25. Введите еще раз: ')
        bot.register_next_step_handler(message, hotels_count_max_check)
    else:
        get_hotels(message)


@program_interrupt_decorator
def get_hotels(message: types.Message) -> None:
    logger.info(f'User {message.chat.id}. Sent {message.text} message')

    bot.hotels_to_show = int(message.text)

    logger.info(f'User {message.chat.id}. Searching for hotels')
    bot.send_message(message.chat.id, '🔎 Ищем отели. Подождите пожалуйста...')

    hotels_list = []

    if bot.sorting_type == 'BEST_SELLER':
        try:
            hotels_list = req.HotelApiRequests.hotels_request(bot.city_id, bot.hotels_to_show, bot.sorting_type,
                                                              bot.prices_range_dict['min'],
                                                              bot.prices_range_dict['max'])
            hotels_list.sort(key=lambda x: (x.hotel_dist_from_center))
        except Exception:
            logger.error(f'User {message.chat.id}. Error while getting a hotels list')
    else:
        try:
            hotels_list = req.HotelApiRequests.hotels_request(bot.city_id, bot.hotels_to_show, bot.sorting_type)
        except Exception:
            logger.error(f'User {message.chat.id}. Error while getting a hotels list')

    if len(hotels_list) < 1:
        logger.info(f'User {message.chat.id}. hotels_list len less than 1')
        bot.send_message(message.chat.id, '❓ Отели в этом регионе не найдены. Вы верно ввели город?')
        bot.welcome_message(message)

    if bot.sorting_type == 'BEST_SELLER':
        try:
            for hotel in hotels_list:
                if hotel.hotel_dist_from_center < bot.dist_from_center_range_dict['max']:
                    bot.print_hotels(message, hotel, maps_url)
                pass
        except Exception:
            logger.error(f'User {message.chat.id}. Error while trying a print hotels to chat')
        else:
            logger.info(f'User {message.chat.id}. Hotels block done without errors!')
    else:
        try:
            for hotel in hotels_list:
                bot.print_hotels(message, hotel, maps_url)
        except Exception:
            logger.error('Error while trying a print hotels to chat')
        else:
            logger.info(f'User {message.chat.id}. Hotels block done without errors!')


if __name__ == "__main__":
    logger.add('bot_info.log', filter=lambda x: x['level'].name == 'INFO', retention="7 days")
    logger.add('bot_errors.log', level='ERROR', retention="7 days")
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
