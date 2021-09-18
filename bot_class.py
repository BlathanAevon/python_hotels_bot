from hotels_class import Hotels
from typing import Type, Dict
from telebot import types
import telebot
import re
from loguru import logger


class HotelBot(telebot.TeleBot):
    """Класс-наследник telebot
    для написания сценариев для
    основного бота в main.py"""
    commands = ['/lowprice', '/highprice', '/bestdeal', '/start', '/help']
    currency = 'руб.'
    regions_dict = {}
    city_id = ''
    hotels_to_show = 0
    sorting_type = ''
    prices_range_dict = {}
    dist_from_center_range_dict = {}

    def __init__(self, token: str) -> None:
        super().__init__(token)

    def program_interrupt_handler(self, message: telebot.types.Message) -> bool:
        if message.text in self.commands:
            return True

    def wrong_input_message(self, message: telebot.types.Message) -> None:
        try:
            err_msg = '⁉ Такому меня не учили. Напиши /help'
            self.send_message(message.chat.id, err_msg)
        except Exception:
            logger.error(f'Error while sending a message to user {message.chat.id}')

    def welcome_message(self, message: telebot.types.Message) -> None:
        try:
            self.send_message(message.chat.id, '*Команды бота:*'
                                               '\n🛎 /lowprice - поиск самых дешевых отелей в городе\n'
                                               '\n🛎 /highprice - поиск самых дорогих отелей в городе\n'
                                               '\n🛎 /bestdeal - поиск лучших отелей по цене/качеству/расстоянию от центра\n',
                              parse_mode='Markdown')
        except Exception:
            logger.error(f'Error while sending a message to user {message.chat.id}')

    def regions_inline_keyboard(self, message: telebot.types.Message, regions_dict) -> bool:
        try:
            keyboard = types.InlineKeyboardMarkup()
            if len(regions_dict) == 0:
                err_msg = '❌ Такой город не найден. Введите еще раз: '
                self.send_message(message.chat.id, err_msg)
                return True
            else:
                for region in regions_dict:
                    city_key = types.InlineKeyboardButton(text=region, callback_data=region)
                    keyboard.add(city_key)
                question = '🌎 Выберите регион: '
                self.send_message(message.chat.id, text=question, reply_markup=keyboard)
        except Exception:
            logger.error(f'Error while sending a regions inline keyboard to user {message.chat.id}')

    def ranges_input_check(self, message: telebot.types.Message, dict_name: Dict) -> bool:
        if len(re.findall(r'\d*-\d*', message.text)) == 1:
            ranges_list = re.split(r'd*\s*-\s*d*', message.text)
            if int(ranges_list[0]) > int(ranges_list[1]):
                return True
            try:
                dict_name['min'] = int(ranges_list[0])
                dict_name['max'] = int(ranges_list[1])
                return False
            except Exception:
                logger.info(f'User {message.chat.id}. Incorrect input a range')
                return True
        logger.info(f'User {message.chat.id}. Incorrect input a range')
        return True

    @classmethod
    def has_cyrillic(cls, message):
        return bool(re.search('[а-яА-Я]', message.text))

    def best_deal_condition_check(self, hotel: Type[Hotels]) -> bool:
        try:
            if self.sorting_type == 'BEST_SELLER':
                if hotel.hotel_dist_from_center < self.dist_from_center_range_dict['max']:
                    return True
                else:
                    return False
            else:
                return True
        except Exception:
            logger.error(f'Error while checking a bestdeal condition')

    def print_hotels(self, message: telebot.types.Message, hotel: Type[Hotels], maps_url):
        keyboard = types.InlineKeyboardMarkup()
        map_key = types.InlineKeyboardButton(text='Показать на карте',
                                             url=maps_url.format(hotel.hotel_coordinates_dict['lat'],
                                                                 hotel.hotel_coordinates_dict['lon']))
        keyboard.add(map_key)
        self.send_message(message.chat.id, f'*{hotel.hotel_name}*\n'
                                           f'Адресс: {hotel.hotel_address}'
                                           f'\nРейтинг: {"".join(["⭐" for _ in range(hotel.hotel_rating)])}\n'
                                           f'Расстояние от центра города: {hotel.hotel_dist_from_center:,} км.\n'
                                           f'Цена за ночь:  *{hotel.hotel_price_for_night:,}* {self.currency}',
                          parse_mode='Markdown',
                          reply_markup=keyboard)
