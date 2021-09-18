from dotenv import load_dotenv
from typing import List, Dict
import hotels_class as hotels
from abc import ABC
import datetime
import requests
import os

load_dotenv()


class HotelApiRequests(ABC):
    max_hotels_count_to_request = 25

    check_in = datetime.date.today() + datetime.timedelta(days=1)
    check_out = datetime.date.today() + datetime.timedelta(days=2)

    @classmethod
    def regions_request(cls, city: str) -> Dict:
        regions_dict = dict()
        url = "https://hotels4.p.rapidapi.com/locations/search"
        querystring = {"query": city, "locale": "ru_RU"}
        headers = {
            'x-rapidapi-key': os.getenv('RAPIDAPI_KEY'),
            'x-rapidapi-host': "hotels4.p.rapidapi.com"
        }
        response = requests.request("GET", url, headers=headers, params=querystring).json()
        try:
            for entities in response['suggestions'][0]['entities']:
                regions_dict[entities['name']] = entities['destinationId']
        except Exception:
            return regions_dict

        return regions_dict

    @classmethod
    def hotels_request(cls, region_id: str, count_to_request: int, sorting_type: str, min_price=None,
                       max_price=None) -> List:
        url = "https://hotels4.p.rapidapi.com/properties/list"

        if min_price and max_price:
            querystring = {"destinationId": region_id, "pageNumber": "1", "pageSize": count_to_request,
                           "checkIn": cls.check_in,
                           "checkOut": cls.check_out, "adults1": "1", "priceMin": min_price, "priceMax": max_price,
                           "sortOrder": sorting_type, "locale": "ru_RU", "currency": "RUB"}
        else:
            querystring = {"destinationId": region_id, "pageNumber": "1", "pageSize": count_to_request,
                           "checkIn": cls.check_in,
                           "checkOut": cls.check_out, "adults1": "1", "sortOrder": sorting_type, "locale": "ru_RU",
                           "currency": "RUB"}

        headers = {
            'x-rapidapi-key': os.environ['RAPIDAPI_KEY'],
            'x-rapidapi-host': "hotels4.p.rapidapi.com"
        }
        response = requests.request("GET", url, headers=headers, params=querystring).json()

        hotels_list = []
        for hotel in response['data']['body']['searchResults']['results']:
            coordinates_dict = {}
            coordinates_dict['lat'] = hotel['coordinate']['lat']
            coordinates_dict['lon'] = hotel['coordinate']['lon']
            if 'streetAddress' not in hotel['address']:
                hotels_list.append(hotels.Hotels(hotel['name'],
                                                 'Не указан',
                                                 hotel['starRating'],
                                                 float(
                                                     hotel['landmarks'][0]['distance'].replace(',', '.').strip(' км')),
                                                 int(hotel['ratePlan']['price']['current'].replace(',', '').strip(
                                                     ' RUB')),
                                                 coordinates_dict
                                                 ))

            else:
                hotels_list.append(hotels.Hotels(hotel['name'],
                                                 hotel['address']['streetAddress'],
                                                 hotel['starRating'],
                                                 float(
                                                     hotel['landmarks'][0]['distance'].replace(',', '.').strip(' км')),
                                                 int(hotel['ratePlan']['price']['current'].replace(',', '').strip(
                                                     ' RUB')),
                                                 coordinates_dict
                                                 ))
        return hotels_list
