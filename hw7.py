from datetime import datetime, timedelta
from collections import UserDict
import re

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty.")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not self._validate(value):
            raise ValueError("Phone number must be exactly 10 digits.")
        super().__init__(value)

    @staticmethod
    def _validate(value):
        return bool(re.fullmatch(r"\d{10}", value))

class Birthday(Field):
    def __init__(self, value):
        if not self.validate_birthday(value):
            raise ValueError("Дата повинна бути у форматі DD.MM.YYYY.")
        self.value = datetime.strptime(value, '%d.%m.%Y')

    @staticmethod
    def validate_birthday(value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
            return True
        except ValueError:
            return False

class Record:
    def __init__(self, name: Name, phone: Phone = None, birthday: Birthday = None):
        self.name = Name(name)
        self.phones = []
        if phone:
            self.phones.append(phone)
        self.birthday = birthday
    
    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]
    
    def edit_phone(self, old_phone, new_phone):
        for idx, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[idx]=Phone(new_phone)
                break 
        else:
            raise ValueError(f"Phone number {old_phone} not found.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
    
    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.now()
        birthday_date = datetime.strptime(self.birthday.value, "%d.%m.%Y").replace(year=today.year)
        if birthday_date < today:
            birthday_date = birthday_date.replace(year=today.year + 1)
        return (birthday_date - today).days


class AddressBook(UserDict):
    def add_record(self, record):  
        self.data[record.name.value]=record

    def find(self, name):
        return self.data.get(name) 

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError(f"Contact {name} not found.")
  
    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())

    def upcoming_birthdays(self, days=7):
        today = datetime.now()
        upcoming = []
        for record in self.data.values():
            if record.birthday:
                bday = datetime.strptime(record.birthday.value, "%d.%m.%Y").replace(year=today.year)
                if bday < today:
                    bday = bday.replace(year=today.year + 1)
                if 0 <= (bday - today).days < days:
                    upcoming.append(record)
        return upcoming


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"Error: {str(e)}"
    return wrapper


@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        return "Error: Provide both name and phone number."
    name, phone = args[0], args[1]
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    if len(args) < 3:
        return "Error: Provide name, old phone, and new phone."
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.change_phone(old_phone, new_phone)
        return f"Phone for '{name}' updated."
    return f"Contact '{name}' not found."


@input_error
def show_phone(args, book: AddressBook):
    if len(args) < 1:
        return "Error: Provide a contact name."
    name = args[0]
    record = book.find(name)
    if record:
        phones = ", ".join(phone.value for phone in record.phones)
        return f"{name}: {phones}"
    return f"Contact '{name}' not found."


def show_all(book: AddressBook):
    if not book.data:
        return "No contacts found."
    result = []
    for record in book.data.values():
        phones = ", ".join(phone.value for phone in record.phones)
        birthday = record.birthday.value if record.birthday else "N/A"
        result.append(f"Contact name: {record.name.value}, phones: {phones}, birthday: {birthday}")
    return "\n".join(result)


@input_error
def add_birthday(args, book: AddressBook):
    if len(args) < 2:
        return "Error: Provide a name and birthday in DD.MM.YYYY format."
    name, birthday = args[0], args[1]
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday for '{name}' added."
    return f"Contact '{name}' not found."

@input_error
def show_birthday(args, book: AddressBook):
    if len(args) < 1:
        return "Error: Provide a contact name."
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        print(f"Birthday object: {record.birthday.value}")
        birthday_date = record.birthday.value.strftime("%d.%m.%Y")
        return f"{name}'s birthday is on {birthday_date}."
    return f"Birthday for '{name}' not found."


def show_birthdays(book: AddressBook):
    birthdays = book.get_upcoming_birthdays()
    if not birthdays:
        return "No upcoming birthdays."
    result = []
    for b in birthdays:
        result.append(f"{b['name']}: {b['birthday']}")
    return "\n".join(result)

def parse_input(user_input):
    parts = user_input.strip().split(" ", 1)
    cmd = parts[0].lower()
    args = parts[1].split() if len(parts) > 1 else []
    return cmd, args


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(show_birthdays(book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
