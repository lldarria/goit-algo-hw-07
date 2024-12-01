from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must consist of 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def change_phone(self, old_phone, new_phone):
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError(f"Phone {old_phone} not found.")

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)


class AddressBook:
    def __init__(self):
        self.records = {}

    def add_record(self, record):
        self.records[record.name.value] = record

    def find(self, name):
        return self.records.get(name)

    def get_all_contacts(self):
        return self.records.values()

    def get_upcoming_birthdays(self):
        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        result = []

        for record in self.records.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if today <= birthday_this_year <= next_week:
                    result.append({
                        "name": record.name.value,
                        "birthday": birthday_this_year.strftime("%d.%m.%Y"),
                    })
        return result


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
    contacts = book.get_all_contacts()
    if not contacts:
        return "No contacts found."
    result = []
    for record in contacts:
        phones = ", ".join(phone.value for phone in record.phones)
        birthday = record.birthday.value.strftime("%d.%m.%Y") if record.birthday else "N/A"
        result.append(f"{record.name.value}: {phones} | Birthday: {birthday}")
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
        return f"{name}'s birthday is on {record.birthday.value.strftime('%d.%m.%Y')}."
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
