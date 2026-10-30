from abc import ABC, abstractmethod
from datetime import date

class LibraryError(Exception):
    pass


class ItemNotFoundError(LibraryError):
    pass


class ItemNotAvailableError(LibraryError):
    pass


class LimitExceededError(LibraryError):
    pass


class MemberNotFoundError(LibraryError):
    pass


class LibraryItem(ABC):
    total_created = 0

    def __init__(self, item_id, title, year, is_available=True):
        self._item_id = item_id
        self.title = title
        self.year = year
        self._is_available = is_available
        LibraryItem.total_created += 1

    @staticmethod
    def normalize_text(text):
        return " ".join(text.split())

    @property
    def item_id(self):
        return self._item_id

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if not isinstance(value, str):
            raise TypeError(f'Title must be str, got {type(value).__name__}')

        normalized_title = self.normalize_text(value)

        if normalized_title == "":
            raise ValueError("Title can't be empty")
        self._title = normalized_title

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int):
            raise TypeError(f'Year must be int, got {type(value).__name__}')
        if  date.today().year < value or value < 1450:
            raise ValueError(f'Invalid year: {value}')
        self._year = value

    @property
    def is_available(self):
        return self._is_available

    def check_out(self):
        if not self.is_available:
            raise ItemNotAvailableError(f"Item '{self.item_id}' is not available")
        self._is_available = False

    def check_in(self):
        if self.is_available:
            raise LibraryError(f"Item '{self.item_id}' is not lent out")
        self._is_available = True

    @abstractmethod
    def loan_days(self):
        pass

    def __repr__(self):
        return f"{type(self).__name__}(item_id={self.item_id!r}, title={self.title!r})"

    def __eq__(self, other):
        if not isinstance(other, LibraryItem):
            return NotImplemented
        return self.item_id == other.item_id

    def __hash__(self):
        return hash(self.item_id)

    def __lt__(self, other):
        if not isinstance(other, LibraryItem):
            return NotImplemented
        return (self.year, self.title) < (other.year, other.title)


class Book(LibraryItem):

    def __init__(self, isbn, title, author, year, is_available=True):
        super().__init__(isbn, title, year, is_available)
        self.isbn = isbn
        self.author = author

    def loan_days(self):
        return 14

    def __str__(self):
        return f"{self.title} - {self.author} ({self.year})"

    @classmethod
    def from_string(cls, line):
        parts = line.split(";")
        if len(parts) != 4:
            raise ValueError(f"Expected 4 fields, got {len(parts)} : {line!r}")
        isbn, title, author, year = parts
        return cls(int(isbn), title, author.strip(), int(year))


class Magazine(LibraryItem):

    def __init__(self, item_id, title, year, issue, is_available=True):
        super().__init__(item_id, title, year, is_available)
        self.issue = issue

    def loan_days(self):
        return 7

    def __str__(self):
        return f"{self.title} #{self.issue} ({self.year})"


class DVD(LibraryItem):

    def __init__(self, item_id, title, year, duration_min, is_available=True):
        super().__init__(item_id, title, year, is_available)
        self.duration_min = duration_min

    def loan_days(self):
        return 3

    def __str__(self):
        return f"{self.title} [DVD, {self.duration_min} min] ({self.year})"


class Member:
    MAX_ITEMS = 3

    def __init__(self, member_id, name):
        self._member_id = member_id
        self.name = name
        self._borrowed_items = []

    @property
    def member_id(self):
        return self._member_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError(f'Member name must be str, got {type(value).__name__}')

        normalized_name = LibraryItem.normalize_text(value)

        if normalized_name == "":
            raise ValueError("Name can't be empty")
        self._name = normalized_name

    @property
    def borrowed_items(self):
        return tuple(self._borrowed_items)

    def add_item(self, item):
        if not self.can_borrow:
            raise LimitExceededError(f"Member '{self.name}' has reached the limit of {self.MAX_ITEMS}")
        self._borrowed_items.append(item)

    def remove_item(self, item):
        if item not in self._borrowed_items:
            raise LibraryError(f"{self.name} hasn't borrowed {item}")
        self._borrowed_items.remove(item)

    @property
    def items_left(self):
        return self.MAX_ITEMS - len(self._borrowed_items)

    @property
    def can_borrow(self):
        return self.items_left > 0

    def __str__(self):
        return f"{self.name} (items: {len(self.borrowed_items)}/{self.MAX_ITEMS})"


class Library:
    def __init__(self, name):
        self.name = name
        self._items = {}
        self._members = {}
        self._history = []

    def add_item(self, item):
        if not isinstance(item, LibraryItem):
            raise TypeError(f"Expected LibraryItem, got {type(item).__name__}")
        if item.item_id in self._items:
            raise LibraryError(f"Item '{item.item_id}' already exists")
        self._items[item.item_id] = item

    def add_member(self, member):
        if member.member_id in self._members:
            raise LibraryError(f"Member '{member.member_id}' already exists")
        self._members[member.member_id] = member

    def lend_item(self, item_id, member_id):
        member = self.get_member(member_id)
        item = self.get_item(item_id)

        if not item.is_available:
            raise ItemNotAvailableError(f"Item '{item_id}' is not available")

        if not member.can_borrow:
            raise LimitExceededError(f"{member.name} has reached the limit of {Member.MAX_ITEMS}")

        member.add_item(item)
        item.check_out()
        message = f"{member.name} has borrowed {item} for {item.loan_days()} days"
        self._history.append(message)
        return message

    def return_item(self, item_id, member_id):
        member = self.get_member(member_id)
        item = self.get_item(item_id)

        if item not in member.borrowed_items:
            raise LibraryError(f"Member {member.name} hasn't borrowed {item}")

        member.remove_item(item)
        item.check_in()
        message = f"{member.name} has returned {item}"
        self._history.append(message)
        return message

    def available_items(self):
        return sorted(item for item in self._items.values() if item.is_available)

    def find_by_author(self, author):
        query = LibraryItem.normalize_text(author).lower()
        return [item for item in self._items.values() if isinstance(item, Book) and LibraryItem.normalize_text(item.author).lower() == query]

    def get_history(self):
        return "History:\n" + "\n".join(self._history)

    @property
    def items(self):
        return tuple(self._items.values())

    @property
    def members(self):
        return tuple(self._members.values())

    @property
    def history(self):
        return tuple(self._history)


    def get_member(self, member_id):
        if member_id not in self._members:
            raise MemberNotFoundError(f"Member '{member_id}' not found")
        return self._members[member_id]

    def get_item(self, item_id):
        if item_id not in self._items:
            raise ItemNotFoundError(f"Item '{item_id}' not found")
        return self._items[item_id]

    def __str__(self):
        return f'Library "{self.name}": {len(self._items)} items, {len(self._members)} members'

    def __len__(self):
        return len(self._items)

    def __contains__(self, item_id):
        return item_id in self._items


def section(title):
    print(f"\n=== {title} ===")


if __name__ == "__main__":
    section("Setup")
    lib = Library("Central Library")
    BOOK_LINES = ["100; Kobzar ; Taras Shevchenko; 1840",
                     "101;Zakhar Berkut;Ivan Franko;1883",
                     "102;Lisova pisnia;Lesya Ukrainka;1911",
                     "103;Tyhrolovy;Ivan Bahrianyi;1944",
                     "105;Eneida;Ivan Kotliarevsky;1798"]
    for line in BOOK_LINES:
        lib.add_item(Book.from_string(line))

    lib.add_item(Magazine("M1", "Ukrainskyi Tyzhden", 2024, 42))
    lib.add_item(DVD("D1", "Tini zabutykh predkiv", 1965, 97))

    lib.add_member(Member(200, "Ihor"))
    lib.add_member(Member(201, "Arthur"))

    print(lib)
    print(f"len: {len(lib)} | 100 in library: {100 in lib} | 999 in library: {999 in lib}")
    print(f"Total items created: {LibraryItem.total_created}")

    section("Lending (polymorphism: loan_days)")
    print(lib.lend_item(100, 200))
    print(lib.lend_item("M1", 200))
    print(lib.lend_item("D1", 201))

    section("Errors")
    try:
        lib.lend_item("D1", 200)
    except ItemNotAvailableError as e:
        print(f"Error: {e}")

    try:
        lib.lend_item(106, 200)
    except ItemNotFoundError as e:
        print(f"Error: {e}")

    try:
        lib.lend_item(101, 999)
    except MemberNotFoundError as e:
        print(f"Error: {e}")

    print(lib.lend_item(101, 200))
    try:
        lib.lend_item(102, 200)
    except LimitExceededError as e:
        print(f"Error: {e}")

    try:
        lib.return_item(105, 201)
    except LibraryError as e:
        print(f"Error: {e}")

    try:
        lib.add_item(Book(100, "Kobzar", "Taras Shevchenko", 1840))
    except LibraryError as e:
        print(f"Error: {e}")

    try:
        lib.add_item("Kobzar")
    except TypeError as e:
        print(f"TypeError: {e}")

    section("Returning")
    print(lib.return_item(100, 200))

    section("Members")
    for member in lib.members:  # було: lib.members.values()
        print(member)

    section("Available (sorted by year, then title)")
    print("\n".join(str(item) for item in lib.available_items()))

    section("Search by author")
    books = lib.find_by_author(" ivan franko ")
    print(f"Books by Ivan Franko: {len(books)}")
    for book in books:
        print(book)
    print(f"Books by Ihor Kaptol: {len(lib.find_by_author('Ihor Kaptol'))}")

    section("Magic methods")
    copy = Book(100, "Kobzar (copy)", "Taras Shevchenko", 1840)
    print("Same item:", copy == lib.get_item(100))  # було: lib.items[100]
    print("In a set:", len({copy, lib.get_item(100)}))
    print(repr(lib.get_item("M1")))  # було: lib.items["M1"]

    section("History")
    print(lib.get_history())
