import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class BookSetPart:
    """A book included within a Teacher Set to be searched for in WorldCat."""

    def __init__(
        self,
        copies: int,
        isbn: str | int,
        format: str | None = None,
        title: str | None = None,
    ) -> None:
        self.copies = copies
        self.isbn = self.norm_isbn(isbn)
        self.format = format
        self.title = title

    @property
    def isbn(self):
        return self._isbn

    @isbn.setter
    def isbn(self, value: str | int) -> str:
        self._isbn = self.norm_isbn(value)

    def norm_isbn(self, isbn: str | int) -> str:
        norm_isbn = self.normalize_isbn(isbn)
        if not self.is_valid_upc(norm_isbn) and not self.is_valid_isbn(norm_isbn):
            raise ValueError(f"ISBN/UPC is invalid: {isbn}.")
        return norm_isbn

    def is_valid_isbn(self, isbn_str: str) -> bool:
        clean_isbn = isbn_str.strip(".").replace("-", "").replace(" ", "")
        if len(clean_isbn) == 10:
            if not clean_isbn[:9].isdigit():
                return False
            total = 0
            for i in range(9):
                total += int(clean_isbn[i]) * (10 - i)
            last_char = clean_isbn[9].upper()
            if last_char == "X":
                total += 10
            elif last_char.isdigit():
                total += int(last_char)
            else:
                return False
            return total % 11 == 0
        elif len(clean_isbn) == 13:
            if not clean_isbn.isdigit():
                return False
            total = 0
            for i in range(13):
                weight = 1 if i % 2 == 0 else 3
                total += int(clean_isbn[i]) * weight
            return total % 10 == 0
        return False

    def is_valid_upc(self, upc_str: str) -> bool:
        clean_upc = upc_str.strip(".").replace("-", "").replace(" ", "")
        if len(clean_upc) != 12 or not clean_upc.isdigit():
            return False

        total = 0
        for index in range(11):
            digit = int(clean_upc[index])
            total += digit * (3 if index % 2 == 0 else 1)

        check_digit = int(clean_upc[-1])
        return (total + check_digit) % 10 == 0

    def normalize_isbn(self, isbn_str: str) -> str:
        clean_isbn = isbn_str.strip(".").replace("-", "").replace(" ", "")
        if len(clean_isbn) == 9:
            clean_isbn = f"0{clean_isbn}"
        return clean_isbn


@dataclass
class DataField:
    tag: str
    indicators: tuple[str, str]
    subfields: list[tuple[str, str]]


@dataclass
class FixedField:
    tag: str
    data: str | None


@dataclass(frozen=True)
class SpecialFormatSetPart:
    """A special format item included within a Teacher Set."""

    copies: int
    title: str
    description: str = ""
    pub_date: str | None = None


@dataclass
class WorldcatSetPart:
    """A book included within a Teacher Set."""

    copies: int
    description: str
    isbn: str
    title: str
    author: str | None = None
    author_dates: str | None = None
    format: str | None = "book"
    pub_date: str | None = None
