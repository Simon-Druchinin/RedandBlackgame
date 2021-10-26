import os
import re
import json
import random
import time
from typing import NoReturn

from game.SETTINGS import JSON_PATH
from game.exceptions import NotCorrectColorIndex

class RedBlack:
    def __init__(self, user_color_index, bet, game_mode):
        self.red_numbers: list = [number for number in range(1, 51)]
        self.black_numbers: list = [number for number in range(51, 101)]
        self.green_numbers: list = [0 for number in range(15)]

        self.game_box: list = self.red_numbers + self.black_numbers + self.green_numbers

        self.bet: int = bet
        self.game_mode: int = game_mode
        self.user_number: int = self.__from_color_index_to_number(user_color_index)
    
    def start_game(self):
        self.__shuffle_game_box()
        self.game_number = self.__generate_number()

    def get_prize_color_bet(self) -> int:
        if ((self.game_number in self.red_numbers and \
            self.user_number in self.red_numbers) or \
            (self.game_number in self.black_numbers and \
            self.user_number in self.black_numbers)) and \
            (self.game_mode == 0):
            return self.bet * 2
        
        elif not (self.user_number + self.game_number) and (self.game_mode == 0):
            return self.bet * 14
        
        elif (self.user_number == self.game_number) and (self.game_mode == 1):
            return self.bet * 30
        
        elif (self.user_number == self.game_number) and (self.game_mode == 2):
            return self.bet * 50

        return 0
    
    def check_correct_index_color(function):
        def wrapper(self, user_color_index, *args, **kwargs):
            if user_color_index not in range(0, 3) and self.game_mode != 1 and self.game_mode != 2:
                raise NotCorrectColorIndex("Введите корректный индекс цвета")
            return function(self, user_color_index, *args, **kwargs)
        return wrapper

    def __shuffle_game_box(self) -> list:
        return random.shuffle(self.game_box)
    
    def __generate_number(self) -> int:
        return random.sample(self.game_box, 1)[0]

    @check_correct_index_color
    def __from_color_index_to_number(self, user_color_index) -> int:
        if user_color_index == 1:
            return random.sample(self.red_numbers, 1)[0]
        
        elif user_color_index == 2:
            return random.sample(self.black_numbers, 1)[0]
        
        elif self.game_mode == 1 or self.game_mode == 2:
            return user_color_index
        
        return 0
    
    def _write_to_json(self, JSON_PATH, user) -> NoReturn:
        JSON_PATH += "game_data.json"

        if os.stat(JSON_PATH).st_size:
            with open(JSON_PATH, 'r', encoding='utf-8') as read_file:
                data = json.load(read_file)
        else:
            data = []


        data.append({user.username: {"game_mode": self.game_mode,
                                    "win_number": self.game_number,
                                    "user_number": self.user_number,
                                    "user_bet": self.bet,
                                    "user_prize": self.get_prize_color_bet()}})

        with open(JSON_PATH, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False)

class GameInterface:
    def __init__(self, game):
        self.game = game

    def drop_effect(function):
        def wrapper(self, *args, **kwargs):
            game_number_index = self.game.game_box.index(self.game.game_number)
            delay = random.randint(20, 40)
            
            if game_number_index >= delay:
                numbers = self.game.game_box[game_number_index - 20:game_number_index]
            else:
                numbers = self.game.game_box[game_number_index:game_number_index + 20]

            for index, number in enumerate(numbers, 1):
                print(f"{number}\n", end='')
                time.sleep(.1 + index/25)
            return function(self, *args, **kwargs)
        return wrapper

    @drop_effect
    def game_result_information(self) -> NoReturn:
        if self.game.game_number in self.game.red_numbers:
            print(f"Выпало красное -- {self.game.game_number}")
        
        elif self.game.game_number in self.game.black_numbers:
            print(f"Выпало чёрное -- {self.game.game_number}")
        
        else:
            print(f"Выпало зелёное -- {self.game.game_number}")
    
    def checking_winning(self) -> NoReturn:
        game_result = self.game.get_prize_color_bet()
        if game_result <= 0:
            print("К сожалению вы проиграли")
        else:
            print("Поздравляем с победой!")

class Registration:
    @staticmethod
    def is_signed_up(username) -> bool:
        users_list = User.get_users_list(JSON_PATH)
        for user in users_list:
            if username == next(iter(user)):
                return True

        return False

    def __init__(self, user_hash):
        self.username: str = user_hash["username"]
        self.password: str = user_hash["password"]
        
    def is_username_and_password_valid(function):
        def wrapper(self, *args, **kwargs):
            if not re.match(r".{8,}", self.password):
                return False
            
            if not re.match(r"@[^\d]+", self.username):
                return False

            return function(self, *args, **kwargs)
        return wrapper
    
    @is_username_and_password_valid
    def check_data(self, password_repeat: str) -> bool:
        return self.password == password_repeat

class User:
    @staticmethod
    def sign_up(username: str, password: str) -> list:
        if Registration.is_signed_up(username):
            return None

        user_hash = {"username": username,
                    "password": password,
                    "bank": 100}
        user = User(user_hash)
        user._write_to_json(JSON_PATH)

        message = f"Welcome {user.username}. Your password: {user.password}"

        return message, user
    
    @staticmethod
    def log_in(username: str, password: str) -> list:
        status = None
        user = None
        if Registration.is_signed_up(username):
            user = User.get_user_instance(username)

            if user.password == password:
                status = f"Welcome back, {user.username}!"
            
        return status, user

    @staticmethod
    def get_users_list(JSON_PATH) -> list:
        JSON_PATH += "user_data.json"
        users_list = []

        if os.stat(JSON_PATH).st_size:
            with open(JSON_PATH, "r", encoding="utf-8") as read_file:
                users_list = json.load(read_file)
            
        return users_list
    
    @staticmethod
    def get_user_instance(username: str):
        users_list = User.get_users_list(JSON_PATH)
        for user_dict in users_list:
            if username == next(iter(user_dict)):
                user_hash = {"username": next(iter(user_dict))}
                user_hash.update(user_dict[username])
                user = User(user_hash)
        
        return user

    def __init__(self, user_hash):
        self.username = user_hash["username"]
        self.password = user_hash["password"]
        self.bank = user_hash["bank"]

    def get_bonus_money(function):
        def wrapper(self, money_amount, *args, **kwargs):
            if money_amount >= 1000:
                self.bank += money_amount // 10
            return function(self, money_amount, *args, **kwargs)
        return wrapper

    @get_bonus_money
    def _add_money_to_bank(self, money_amount: int) -> NoReturn:
        self.bank += money_amount

    def get_bank(self) -> str:
        return f"Ваш банк -- {self.bank}"

    def update_user_bank(self, bet: int) -> int:
        return self.bank + bet

    def __get_user_hash(self) -> dict:
        user_hash = {
            "bank": self.bank,
            "password": self.password
        }

        return user_hash
    
    def _write_to_json(self, JSON_PATH) -> NoReturn:
        JSON_PATH += "user_data.json"

        if os.stat(JSON_PATH).st_size:
            with open(JSON_PATH, 'r', encoding='utf-8') as read_file:
                data = json.load(read_file)
        else:
            data = []


        if os.stat(JSON_PATH).st_size:
            for num, user in enumerate(data):
                if next(iter(user)) == self.username:
                    data[num] = {self.username: self.__get_user_hash()}
                    break
            else:
                data.append({self.username: self.__get_user_hash()})

        with open(JSON_PATH, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False)

def registration():
    while True:
        reg_choice = input("For sign up print '1'!\nPrint '2' to login.\nPress Enter to exit\n")
        if reg_choice == '1':
            username = input("Enter username: ")
            password = input("Create password: ")
            password_repeat = input("Repeat password: ")

            registration = Registration({"username": username,
                                        "password": password})

            if not registration.check_data(password_repeat):
                print("\nWarning!")
                print('Nicname must start with "@" symbol\nPassword length must be more than 8 symbols\n')
                continue

            data = User.sign_up(username, password)
            if data is None:
                print("\n!Username is taken!\n")
            else:
                status = data[0]
                user = data[1]
                print(status)
                return user

        elif reg_choice == '2':
            print("Log in...")
            username = input("Enter username: ")
            password = input("Enter your password: ")

            data = User.log_in(username, password)

            status = data[0]
            user = data[1]

            if status is not None:
                print(status)
                return user
            
            else:
                print("\n!Username or password is incorrect!\n")

        else:
            print("Bye!")
            return None

def game_roulette(user):
    print("Добро пожаловать  в игру!")
    while user.bank > 0:
        print(user.get_bank())
        game_mode_choice = int(input(
            "Какой вид игры хотите выбрать?\n"
            "0.) Угадать: Красное(x2), Чёрное(x2), Зелёное(x14).\n"
            "1.) Угадать: Число(x30).\n"
            "2.) Довериться удаче: число, загаданное компьютером должно выпасть на рулетке(x50).\n"))
        user_bet = int(input("Введите вашу ставку(не больше 300): "))

        while user_bet > 300 or user_bet > user.bank:
            print("Ставка не может быть выше 300 или выше вашего банка!")
            user_bet = int(input("Введите вашу ставку(не больше 300): "))

        if game_mode_choice == 0:
            print("Выберете цвет:\n0. Зелёное\n1. Красное\n2. Чёрное\n")
            user_bet_choice = int(input("Цвет (выберете цифрой): "))
        
        elif game_mode_choice == 1:
            print("Выберете число от 0 до 100 (включительно)")
            user_bet_choice = int(input("Напишите цифру: "))
        
        else:
            user_bet_choice = random.randint(0, 100)

        user.bank -= user_bet

        game = RedBlack(user_bet_choice, user_bet, game_mode_choice)
        game.start_game()
        prize = game.get_prize_color_bet()

        console = GameInterface(game)

        console.game_result_information()
        console.checking_winning()

        user.bank += prize
        game._write_to_json(JSON_PATH, user)
        print(user.get_bank())
        user_choice = input("Нажмите:\nEnter.) Продолжить играть\n"
        "1.) Выход из программы\n"
        "2.) Добавить денег в банк\n")

        if user_choice == "1":
            return 0

        elif user_choice == "2":
            money_amount = int(input("Введите сумму: "))
            user._add_money_to_bank(money_amount)

        else:
            continue
    
def main() -> NoReturn:
    user = registration()
    game_roulette(user)
    user._write_to_json(JSON_PATH)
    print("До встречи!")


if __name__ == "__main__":
    main()