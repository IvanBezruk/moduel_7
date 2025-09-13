from datetime import datetime, timedelta
from collections import UserDict

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, *kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Contact not found"
        except IndexError:
            return "Invalid command format. Please check the arguments."
        except Exception as e:
            return f"An error occurred: {str(e)}"
    return inner

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("Phone number must be 10 digits")
        super().__init__(value)
    
    def validate_phone(self, phone):
        return phone.isdigit() and len(phone) == 10

class Birthday(Field):
    def __init__(self, value):
        try:
            # Додайте перевірку коректності даних
            # та перетворіть рядок на об'єкт datetime
            datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone_to_remove = self.find_phone(phone)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)

    def edit_phone(self, old_phone, new_phone):
        phone_to_edit = self.find_phone(old_phone)
        if phone_to_edit:
            if not Phone(new_phone).validate_phone(new_phone):
                raise ValueError("New phone number must be 10 digits")
            phone_to_edit.value = new_phone
        else:
            raise ValueError("Phone number not found")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        #Add the birthday to the contact
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        """
        Determie contacts that have birthdays within next 7 days
        """
        upcoming_birthdays = []
        today = datetime.today().date()
        
        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday_date.replace(year=today.year)
                
                # Check whether the birthday happened this year or check the next one
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                
                # Check whether the birthday is within the next 7 dayes
                days_until_birthday = (birthday_this_year - today).days
                if 0 <= days_until_birthday <= 7:
                    #check if it is weekend
                    congratulation_date = birthday_this_year
                    if birthday_this_year.weekday() == 5:  # Saturday
                        congratulation_date = birthday_this_year + timedelta(days=2)
                    elif birthday_this_year.weekday() == 6:  # Sunday
                        congratulation_date = birthday_this_year + timedelta(days=1)
                    
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "birthday": congratulation_date.strftime("%d.%m.%Y")
                    })
        
        return upcoming_birthdays

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        raise IndexError("Please provide name and phone number")
    
    name = args[0]
    phone = args[1]

    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    if len(args) < 3:
        raise IndexError("Please provide name, old phone, and new phone")
    
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError("Contact not found")
    
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."

@input_error
def show_phone(args, book: AddressBook):
    if len(args) < 1:
        raise IndexError("Please provide contact name")
    
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError("Contact not found")
    
    if record.phones:
        phones = ', '.join(phone.value for phone in record.phones)
        return f"{name}: {phones}"
    else:
        return f"{name} has no phone numbers"

@input_error
def show_all(args, book: AddressBook):
    if not book.data:
        return "No contacts found."
    
    result = []
    for record in book.data.values():
        result.append(str(record))
    return '\n'.join(result)

@input_error
def add_birthday(args, book: AddressBook):
    
    if len(args) < 2:
        raise IndexError("Please provide name and birthday (DD.MM.YYYY)")
    
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError("Contact not found")
    
    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def show_birthday(args, book: AddressBook):
    
    if len(args) < 1:
        raise IndexError("Please provide contact name")
    
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError("Contact not found")
    
    if record.birthday:
        return f"{name}'s birthday: {record.birthday.value}"
    else:
        return f"{name} has no birthday set"

@input_error
def birthdays(args, book: AddressBook):
    
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays in the next 7 days."
    
    result = ["Upcoming birthdays:"]
    for birthday_info in upcoming:
        result.append(f"{birthday_info['name']}: {birthday_info['birthday']}")
    
    return '\n'.join(result)

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)   # <-- FIXED here

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
            print(show_all(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()

    