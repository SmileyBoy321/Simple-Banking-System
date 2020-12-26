"""Bank app thing"""
from random import randint, sample
from sys import exit as sysexit
import sqlite3


class Bank:
    """Main application class"""

    def __init__(self):
        self.balance_value = None
        self.choice = None
        self.card_number_input = None
        self.card_pin_input = None
        self.card_number = None
        self.pin_code = None
        self.rows = None
        self.card_num_by2 = None
        self.card_num_minus9 = None
        self.sum_of_numbers = None
        self.last_digit = None
        self.card_num_str = None
        self.card_num = None
        self.row = None
        self.conn = sqlite3.connect("card.s3db")
        self.cur = self.conn.cursor()
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS card (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                number TEXT, 
                pin TEXT, 
                balance INTEGER
            );"""
        )

    def user_choice(self):
        """Get user input"""
        self.choice = int(input())
        print()
        return self.choice

    def card_and_pin(self):
        """Get card nr and pin"""
        print("Enter your card number:")
        self.card_number_input = int(input())
        print("Enter your PIN:")
        self.card_pin_input = int(input())

    def create_an_account(self):
        """Create account"""
        self.card_number = self.luhn_algorithm()
        self.pin_code = randint(1000, 9999)
        self.cur.execute(
            f"""INSERT INTO card (number, pin, balance) VALUES ({self.card_number}, {self.pin_code}, 0 );"""
        )
        self.conn.commit()
        print("Your card has been created")
        print(f"Your card number:\n{self.card_number}")
        print(f"Your card PIN:\n{self.pin_code}")

    def log_into_account(self):
        """Log in to account"""
        self.cur.execute(f"SELECT * FROM card WHERE number = {self.card_number_input}")
        self.rows = self.cur.fetchall()
        try:
            if self.card_number_input == int(
                self.rows[0][1]
            ) and self.card_pin_input == int(self.rows[0][2]):
                print("\nYou have successfully logged in!")
                return True
            print("\nWrong card number or PIN!")
            return False
        except Exception:
            print("\nWrong card number or PIN!")
            return False

    def show_balance(self):
        """Show balance"""
        self.cur.execute(f"SELECT * FROM card WHERE number = {self.card_number_input}")
        self.balance_value = self.cur.fetchall()
        print("Balance:", self.balance_value[0][3])

    def add_income(self):
        self.cur.execute(f"SELECT * FROM card WHERE number = {self.card_number_input}")
        self.balance_value = self.cur.fetchall()
        print("Enter income:\n")
        user_income = int(input())
        self.cur.execute(
            f"UPDATE card SET balance={self.balance_value[0][3] + user_income} WHERE number={self.card_number_input}"
        )
        self.conn.commit()
        print("Income was added!")

    def do_transfer(self):
        self.cur.execute(
            f"SELECT number, balance FROM card WHERE number = {self.card_number_input}"
        )
        your_card = self.cur.fetchone()
        print("Transfer\nEnter card number:\n")
        client_card = int(input())
        self.cur.execute(
            f"SELECT number, balance FROM card WHERE number = {client_card}"
        )
        client_card_copy = self.cur.fetchone()
        try:
            if self.checkLuhn(str(client_card)):
                if self.card_number_input == client_card_copy[0]:
                    print("You can't transfer money to the same account!")
                else:
                    print("Enter how much money you want to transfer:")
                    transfer_money = int(input())
                    if your_card[1] < transfer_money:
                        print("Not enough money!")
                    else:
                        self.cur.execute(
                            f"""
                            UPDATE card SET balance={client_card_copy[1] + transfer_money} 
                            WHERE number={client_card_copy[0]}
                            """
                        )
                        self.cur.execute(
                            f"UPDATE card SET balance={your_card[1] - transfer_money} WHERE number={your_card[0]}"
                        )
                        self.conn.commit()
                        print("Success!")
            else:
                print(
                    "Probably you made a mistake in the card number. Please try again!"
                )
        except TypeError:
            print("Such a card does not exist")

    def close_account(self):
        self.cur.execute(f"DELETE FROM card WHERE number={self.card_number_input}")
        self.conn.commit()
        print("The account has been closed!")

    def luhn_algorithm(self):
        self.card_num = [4, 0, 0, 0, 0, 0]
        self.card_num.extend([int(i) for i in sample(range(10), 9)])
        self.card_num_by2 = [
            self.card_num[i] * 2 if i % 2 == 0 else self.card_num[i]
            for i in range(len(self.card_num))
        ]
        self.card_num_minus9 = [
            num - 9 if num > 9 else num for num in self.card_num_by2
        ]
        self.sum_of_numbers = sum(self.card_num_minus9)
        self.last_digit = 0

        for i in range(10):
            if (self.sum_of_numbers + i) % 10 == 0:
                self.last_digit = i
        self.card_num.append(self.last_digit)
        self.card_num_str = "".join([str(i) for i in self.card_num])
        self.card_num = int(self.card_num_str)

        return self.card_num

    def checkLuhn(self, cardNo):

        nDigits = len(cardNo)
        nSum = 0
        isSecond = False

        for i in range(nDigits - 1, -1, -1):
            d = ord(cardNo[i]) - ord("0")

            if isSecond == True:
                d = d * 2

            # We add two digits to handle
            # cases that make two digits after
            # doubling
            nSum += d // 10
            nSum += d % 10

            isSecond = not isSecond

        if nSum % 10 == 0:
            return True
        else:
            return False


def main():
    """Main function for application"""
    bank = Bank()

    while True:
        print("\n1. Create an account\n2. Log into account\n0. Exit")
        choice = bank.user_choice()
        if choice == 1:
            bank.create_an_account()
        elif choice == 2:
            bank.card_and_pin()
            if bank.log_into_account():
                print(
                    "\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit"
                )
            else:
                continue
            while True:
                choice = bank.user_choice()
                if choice == 1:
                    bank.show_balance()
                    print(
                        "\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit"
                    )
                elif choice == 2:
                    bank.add_income()
                    print(
                        "\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit"
                    )
                elif choice == 3:
                    bank.do_transfer()
                elif choice == 4:
                    bank.close_account()
                elif choice == 5:
                    print("\nYou have successfully logged out!")
                    break
                elif choice == 0:
                    print("Bye!")
                    sysexit()
                else:
                    print(
                        "\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit"
                    )
                    continue
        else:
            print("Bye!")
            sysexit()


if __name__ == "__main__":
    main()
