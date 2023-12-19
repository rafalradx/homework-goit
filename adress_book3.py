from dataclasses import dataclass, field
from collections import UserDict
from datetime import date
from icecream import ic
import pickle


@dataclass(order=True)
class Field:
    _value: str = field(init=False, repr=False)
    value: str

    @property
    def value(self) -> str:
        return self._value

    # general setter
    @value.setter
    def value(self, new_value: str) -> None:
        self._value = new_value


@dataclass(order=True, unsafe_hash=True)
class Phone(Field):
    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, new_value: str) -> None:
        if self.is_phone_valid(new_value):
            self._value = new_value

    @staticmethod
    def is_phone_valid(phone_number: str) -> bool:
        if phone_number.isdigit() and len(phone_number) == 9:
            return True
        else:
            raise ValueError(
                f"Phone number '{phone_number}' is not valid. Please specify a 9-digit string"
            )


@dataclass(order=True)
class Name(Field):
    pass


@dataclass(order=True)
class Birthday(Field):
    @property
    def value(self) -> date:
        return self._value

    @value.setter
    def value(self, new_date: str) -> None:
        if new_date is None:
            self._value = None
            return
        try:
            dateobj = date.fromisoformat(new_date)
            self._value = dateobj
        except ValueError:
            print(f"Date of birth '{new_date}' is not valid")
            print(f"Supported date format: YYYY-MM-DD")
            self._value = None

    def __str__(self):
        if self.value is None:
            return "None"
        else:
            return self.value.isoformat()


class Record:
    def __init__(self, contact_name: str, *phone_numbs: str, birthday=None) -> None:
        self.name = Name(contact_name)
        # cast data to set to remove duplicates
        phone_numbs = set(phone_numbs)
        phone_numbs = [Phone(phone_numb) for phone_numb in phone_numbs]
        phone_numbs.sort()
        self.phones = phone_numbs
        self.birthday = Birthday(birthday)

    def add_phone(self, *phone_numbs: str):
        # cast data to set to remove duplicates
        phone_numbs = set(phone_numbs)
        new_phones = [Phone(phone_numb) for phone_numb in phone_numbs]
        self.phones.extend(new_phones)
        all_phones = self.phones
        # cast data to set to remove duplicates
        all_phones = list(set(all_phones))
        all_phones.sort()
        self.phones = all_phones

    def remove_phone(self, *phone_numbs: str):
        for phone in phone_numbs:
            self.phones.remove(Phone(phone))

    def change_phone(self, old_phone: str, new_phone: str):
        ind = self.phones.index(Phone(old_phone))
        self.phones.pop(ind)
        self.phones.insert(ind, Phone(new_phone))
        self.phones.sort()

    def days_to_birthday(self):
        today_date = date.today()
        if self.birthday.value is not None:
            birthdate = self.birthday.value
            birthday_this_year = date(
                year=today_date.year, month=birthdate.month, day=birthdate.day
            )
            delta_this_year = birthday_this_year - today_date
            if delta_this_year.days >= 0:
                return delta_this_year.days
            else:
                birthday_nex_year = date(
                    year=today_date.year + 1, month=birthdate.month, day=birthdate.day
                )
                delta_next_year = birthday_nex_year - today_date
                return delta_next_year.days

    def __str__(self) -> str:
        return f"name: {self.name.value}, phones: {[ph_num.value for ph_num in self.phones]}, birthday: {self.birthday}"

    def __repr__(self) -> str:
        return self.__str__()

    def get_search_string(self) -> str:
        phones_string = " ".join([ph_num.value for ph_num in self.phones])
        return f"{self.name} {phones_string} {self.birthday}"

    def get_name(self) -> str:
        return self.name.value

    def get_phones(self) -> list[str]:
        return [phone.value for phone in self.phones]


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def store_book_in_file(self, filename: str):
        with open(filename, "wb") as file:
            pickle.dump(self, file)

    @staticmethod
    def import_book_from_file(filename: str):
        with open(filename, "rb") as file:
            return pickle.load(file)

    def search_for(self, query: str) -> list[Record]:
        hits_dict = {
            key: value
            for key, value in self.data.items()
            if query in value.get_search_string()
        }
        return hits_dict

    def iterator(self, N):
        rec_keys = list(self.data.keys())
        rec_keys.sort()

        count = 0
        while count < len(rec_keys):
            output_page = ""
            recs_to_print = rec_keys[count : count + N]
            for rec in recs_to_print:
                rec_string = f"{rec:8} {self.data[rec]} \n"
                output_page += rec_string

            yield output_page.removesuffix("\n")
            count += N


# testing
if __name__ == "__main__":
    # create record with name and three phone numbers, duplicates are ignored
    rec1 = Record("Bilbo", "123123123", "666736473", "232322323", birthday="1988-12-01")
    print(str(rec1))
    ic(rec1.days_to_birthday())
    ic(rec1)
    # create record with name only (phone number and birthday are optional)
    rec2 = Record("Frodo")
    ic(rec2)

    # add another phone numbers to rec1, duplicates are ignored
    rec1.add_phone("334343434", "666666666", "666666666", "334343434", "232322323")
    ic(rec1)
    # not present numbers are ignored, not in list -> ValueError
    rec1.remove_phone("334343434", "666736473")
    ic(rec1)
    # change phone; two arguments; not in list -> ValueError
    rec1.change_phone("666666666", "777777777")
    ic(rec1)

    # get name frome rec1 (rec1.name.value)
    ic(rec1.get_name())

    myAddressBook = AddressBook()
    ic(myAddressBook)
    myAddressBook.add_record(rec1)
    ic(myAddressBook)
    rec1_from_dict = myAddressBook["Bilbo"]
    ic(rec1_from_dict)

    ic(rec1.get_phones())
    myAddressBook.add_record(rec2)

    # wrong phone number
    try:
        rec3 = Record("stefan", "ddfdfa")
    except ValueError as e:
        print(e)

    # wrong birthay date
    rec4 = Record("Stasiek", "123321123", birthday="hhhdj-3--43-")

    # paginator
    myAddressBook.add_record(Record("Balin", birthday="1432-04-12"))
    myAddressBook.add_record(Record("Thorin", birthday="1672-08-12"))
    myAddressBook.add_record(Record("Dwalin", birthday="1868-09-21"))
    myAddressBook.add_record(Record("Oin", birthday="2001-01-23"))
    myAddressBook.add_record(Record("Gloin", birthday="2005-06-07"))
    myAddressBook.add_record(Record("Kili", birthday="1844-08-23"))
    myAddressBook.add_record(Record("Fili", birthday="1844-12-31"))
    myAddressBook.add_record(Record("Bifur", birthday="1872-11-13"))
    myAddressBook.add_record(Record("Bofur", birthday="1111-11-11"))
    myAddressBook.add_record(Record("Bombur", birthday="2002-02-22"))
    myAddressBook.add_record(Record("Dori", birthday="1234-12-21"))
    myAddressBook.add_record(Record("Ori", birthday="1232-02-16"))
    myAddressBook.add_record(Record("Nori", birthday="2023-01-01"))

    # generator N records per page
    N = 6
    paginator = myAddressBook.iterator(N)

    for page in paginator:
        print(page)
        input("Press enter to continue...")

    # pickle
    myAddressBook.store_book_in_file("addbook.bin")

    # unpickle
    ABbackup = AddressBook.import_book_from_file("addbook.bin")

    # before and after
    ic(myAddressBook)
    ic(ABbackup)

    # searching through address book (case sensitive)
    # return dictionary {name: Record} with hits
    ic(myAddressBook.search_for("Bilbo"))
    ic(myAddressBook.search_for("123"))
    ic(myAddressBook.search_for("fur"))
    ic(myAddressBook.search_for("1872-11-13"))
    ic(myAddressBook.search_for("1844"))
