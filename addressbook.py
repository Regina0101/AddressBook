from datetime import datetime
from collections import UserDict
from abc import ABC, abstractmethod
import pickle


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Contact is already exist"
        except KeyError as e:
            return f"Contact not found: {e}"
        except Exception as e:
            return f"Error: {e}"
    return inner


class Field(ABC):
    def __init__(self, value):
        self.value = self.validate(value)

    @abstractmethod
    def validate(self, value):
        pass

    def __str__(self):
        return f"{self.value}"


class Name(Field):
    def validate(self, value):
        return value

class Phone(Field):
    def validate(self, value):
        if not isinstance(value, str):
            self.value = str(value)
        if len(str(value)) != 10:
            raise ValueError("Phone number must be a 10-digit string")
        return value


class Birthday(Field):
    def __init__(self, value):
        self.value = value

    def validate(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            return value
        except ValueError:
            raise ValueError("Date is not correct format. Format should be dd.mm.yyyy")

    def __repr__(self):
        birthday_date = datetime.strptime(self.value, "%d.%m.%Y").date()
        return f"Birthday date is: {birthday_date.strftime('%d.%m.%Y')}"

class Record:
    def __init__(self, name: str, phone: str, birthday = None):
        self.name = Name(name)
        self.phone = Phone(phone)
        self.birthday = Birthday(birthday) if birthday else None

    def __repr__(self):
        return f"Name: {self.name} Phone: {self.phone} Birthday: {self.birthday}"

class AddressBook(UserDict):
    @input_error
    def add_contact(self, name, phone, birthday = None):
        record = Record(name=name, phone=phone, birthday=birthday)
        self.data[name] = record

    @input_error
    def add_birthday(self, name, birthday):
        if name in self.data:
            self.data[name].birthday = Birthday(birthday)
        else:
            raise ValueError("Contact not found")

    @input_error
    def show_phone(self, name):
        if name in self.data:
            record = self.data[name]
            return record.phone
        else:
            raise ValueError("Contact not found")

    def chane_phone(self, name, phone):
        if name in self.data:
            self.data[name].phone = phone
            return f"{self.data[name].name} changed phone number to {self.data[name].phone}"


    @input_error
    def delete_contact(self, name):
        if name in self.data:
            del self.data[name]
            return "Contact was deleted"
        else:
            raise ValueError("Contact not found")

    def show_birthday(self, name):
        if name in self.data:
            return f"{self.data[name].name} was born {self.data[name].birthday}"

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.today().date()
        current_week = today.isocalendar()[1]

        for name, record in self.data.items():
            if record.birthday is not None:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_week = birthday_date.isocalendar()[1]
                if current_week == birthday_week:
                    upcoming_birthdays.append((name, record.birthday))

        return upcoming_birthdays

    def __repr__(self):
        return f"Contacts: {self.data}"


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()



def parse_input(user_input: str):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


class Command:
    def __init__(self, commands):
        self.commands = commands
    def print_commands(self):
        print("-" * 45)
        print("{:<25} | {:<20}".format("Command", "Description"))
        print("-" * 45)
        for command, description in self.commands.items():
            print("{:<25} | {:<20}".format(command, description))
        print("-" * 45)



def main():
    # book = AddressBook()
    book = load_data()
    basic_commands = {
        "contacts": "Displays contact commands",
        "birthdays": "Displays birthday command"
    }
    contact_commands = {
        "add": "Add a new contact",
        "change": "Change contact information",
        "delete": "Delete a contact",
        "phone": "Show phone number of a contact",
        "all": "Show all contacts",

    }
    birthday_commands = {
        "add-birthday": "Add birthday to a contact",
        "show-birthday": "Show birthday of a contact",
        "upcoming-birthdays": "Show who has birthdays this week",
        "exit or close": "Exit the program"
    }
    basic_command = Command(basic_commands)
    contact_command = Command(contact_commands)
    birthday_command = Command(birthday_commands)

    print("Welcome to the assistant bot!")
    basic_command.print_commands()
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)
        if command in basic_commands:
            if command == "contacts":
                contact_command.print_commands()
            elif command == "birthdays":
                birthday_command.print_commands()
        elif command in contact_commands:
            if command == "add":
                birthday = None
                if len(args) == 3:
                    name, phone, birthday = args
                elif len(args) == 2:
                    name, phone = args
                else:
                    print("You should add name and phone (birthday is optional)")
                    continue
                book.add_contact(name, phone, birthday)

            elif command == "change":
                name, phone = args
                print(book.chane_phone(name, phone))

            elif command == "delete":
                name = args[0]
                print(book.delete_contact(name))

            elif command == "phone":
                name = args[0]
                print(book.show_phone(name))

            elif command == "all":
                for name, values in book.data.items():
                    print(f"Contact:{name} \n{values}")
                    print("∞" * 45)

        elif command in birthday_commands:
            if command == "add-birthday":
                name, birthday = args
                book.add_birthday(name, birthday)

            elif command == "show-birthday":
                name = args[0]
                print(book.show_birthday(name))

            elif command == "upcoming-birthdays":
                print(book.get_upcoming_birthdays())

        elif command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
