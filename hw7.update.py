from collections import UserDict
import re
from datetime import datetime, timedelta

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
        super().__init__(value)

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


if __name__ == "__main__":
    book = AddressBook()

    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")
    book.add_record(john_record)

    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    book.add_record(jane_record)

    ann_record = Record ("Ann")
    ann_record.add_phone("9876543217")
    ann_record.add_birthday("07.12.2001")
    book.add_record(ann_record)

    vova_record = Record ("Vova")
    vova_record.add_phone("1234567899")
    vova_record.add_birthday("15.12.2000")
    book.add_record(vova_record)

    print(book)

    john = book.find("John")
    john.edit_phone("1234567890", "1112223333")

    print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

    found_phone = john.find_phone("5555555555")
    print(f"{john.name}: {found_phone}")  # Виведення: John: 5555555555

    book.delete("Jane")
    print("\nПісля видалення Jane:")
    print(book)

# Додавання записів
book.add_record(Record(Name("Vova"), Phone("1234567899"), Birthday("15.12.2000")))
book.add_record(Record(Name("Anna"), Phone("9876543217"), Birthday("07.12.2001")))

# Отримання іменинників
upcoming = book.upcoming_birthdays()
for rec in upcoming:
    print(f"Іменниники у найближчі сім днів: {rec.name.value}: {rec.birthday.value}")
