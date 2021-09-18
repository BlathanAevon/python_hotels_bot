from typing import Any, Dict


class Hotels:
    """Класс отелей для бота HotelBot
     для удобства хранения
      и возврата данных"""

    def __init__(self, name: str, address: str, rating: int, dist_from_center: float, price: Any,
                 coordinates: Dict) -> None:
        self.__hotel_name = name
        self.__hotel_rating = int(round(rating, 0))
        self.__hotel_address = address
        self.__hotel_dist_from_center = dist_from_center
        self.__hotel_price_for_night = price
        self.__hotel_coordinates_dict = coordinates

    def __str__(self) -> str:
        return f'{self.__hotel_name}\n\t{self.__hotel_address}\n\t{self.__hotel_rating}\n\t{self.__hotel_dist_from_center}\n\t{self.__hotel_price_for_night}'

    @property
    def hotel_name(self) -> str:
        """Getter for hotel name"""
        return self.__hotel_name

    @hotel_name.setter
    def hotel_name(self, value: str) -> None:
        """Setter for hotel name"""
        self.__hotel_name = value

    @property
    def hotel_rating(self) -> int:
        """Getter for hotel rating"""
        return self.__hotel_rating

    @hotel_rating.setter
    def hotel_rating(self, value: int) -> None:
        """Setter for hotel rating"""
        self.__hotel_rating = value

    @property
    def hotel_address(self) -> str:
        """Getter for hotel address"""
        return self.__hotel_address

    @hotel_address.setter
    def hotel_address(self, value: str) -> None:
        """Setter for hotel address"""
        self.__hotel_address = value

    @property
    def hotel_dist_from_center(self) -> float:
        """Getter for hotel distance from center"""
        return self.__hotel_dist_from_center

    @hotel_dist_from_center.setter
    def hotel_dist_from_center(self, value: float) -> None:
        """Setter for hotel distance from center"""
        self.__hotel_dist_from_center = value

    @property
    def hotel_price_for_night(self) -> Any:
        """Getter for hotel price for night"""
        return self.__hotel_price_for_night

    @hotel_price_for_night.setter
    def hotel_price_for_night(self, value: Any) -> None:
        """Setter for hotel price for night"""
        self.__hotel_price_for_night = value

    @property
    def hotel_coordinates_dict(self) -> Any:
        """Getter for hotel coordinates list"""
        return self.__hotel_coordinates_dict

    @hotel_coordinates_dict.setter
    def hotel_coordinates_dict(self, value: Any) -> None:
        """Setter for coordinates list"""
        self.__hotel_coordinates_dict = value
