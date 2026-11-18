"""Console application for assigning exam tickets."""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
import random
import sys
import unicodedata
from zipfile import BadZipFile

from openpyxl import Workbook, load_workbook
from openpyxl.utils.exceptions import InvalidFileException


JOURNAL = Path(__file__).with_name("journal.xlsx")
HEADERS = ("Last name", "First name", "Номер билета", "Дата и время")
ESC = "\x1b"
NAME_MAX_LENGTH = 100
NAME_SEPARATORS = (" ", "-", "'")


def validate_name(value: str) -> str | None:
    value = value.strip()
    if not value:
        return "Name cannot be empty."
    if len(value) > NAME_MAX_LENGTH:
        return f"Name must contain no more than {NAME_MAX_LENGTH} characters."
    if not any(unicodedata.category(character).startswith("L") for character in value):
        return "Name must contain letters."
    if any(
        unicodedata.category(character).startswith("N")
        or unicodedata.category(character).startswith("P")
        and character not in NAME_SEPARATORS
        or unicodedata.category(character).startswith("S")
        or unicodedata.category(character).startswith("C")
        for character in value
    ):
        return "Name may contain only letters, spaces, hyphens, and apostrophes."
    if value[0] in NAME_SEPARATORS or value[-1] in NAME_SEPARATORS:
        return "Name must start and end with a letter."
    if any(value[index] in NAME_SEPARATORS and value[index + 1] in NAME_SEPARATORS
           for index in range(len(value) - 1)):
        return "Use only one separator between letters."
    return None


class TicketGenerator(ABC):
    @abstractmethod
    def generate(self) -> int:
        raise NotImplementedError


class RandomTicketGenerator(TicketGenerator):
    def generate(self) -> int:
        return random.randint(1, 20)


class JournalRepository(ABC):
    @abstractmethod
    def append(self, last_name: str, first_name: str, ticket: int,
               created_at: datetime) -> None:
        raise NotImplementedError


class ExcelJournalRepository(JournalRepository):
    def __init__(self, path: Path):
        self.path = path

    def append(self, last_name: str, first_name: str, ticket: int,
               created_at: datetime) -> None:
        lock_file = self.path.with_name("~$" + self.path.name)
        if lock_file.exists():
            raise PermissionError(
                f"{self.path.name} открыт в Excel. Закройте файл и повторите попытку."
            )

        workbook = None
        try:
            if self.path.exists():
                workbook = load_workbook(self.path)
                sheet = workbook.active
            else:
                workbook = Workbook()
                sheet = workbook.active
                sheet.append(HEADERS)

            if sheet.max_row == 1 and all(
                sheet.cell(1, column).value is None
                for column in range(1, len(HEADERS) + 1)
            ):
                for column, header in enumerate(HEADERS, start=1):
                    sheet.cell(1, column).value = header

            sheet.append((last_name, first_name, ticket, created_at))
            sheet.cell(sheet.max_row, 4).number_format = "yyyy-mm-dd hh:mm:ss"
            workbook.save(self.path)
        except (PermissionError, OSError, InvalidFileException, BadZipFile) as error:
            raise PermissionError(
                f"Не удалось записать в {self.path.name}: {error}"
            ) from error
        finally:
            if workbook is not None:
                workbook.close()


class LineInput(ABC):
    @abstractmethod
    def prompt(self, label: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def read_key(self) -> str:
        raise NotImplementedError


class ConsoleLineInput(LineInput):
    def read_key(self) -> str:
        if sys.platform == "win32":
            import msvcrt
            return msvcrt.getwch()

        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def prompt(self, label: str) -> str | None:
        while True:
            print(label, end="", flush=True)
            value = ""
            while True:
                key = self.read_key()
                if key == ESC:
                    print()
                    return None
                if key in ("\r", "\n"):
                    print()
                    break
                if key in ("\b", "\x7f"):
                    if value:
                        value = value[:-1]
                        print("\b \b", end="", flush=True)
                    continue
                if key.isprintable():
                    value += key
                    print(key, end="", flush=True)

            value = value.strip()
            if value:
                error = validate_name(value)
                if error is None:
                    return value
                print(error)
                continue
            print("Field cannot be empty. Please try again.")


class TicketApplication:
    def __init__(self, input_service: LineInput,
                 journal: JournalRepository,
                 ticket_generator: TicketGenerator):
        self.input = input_service
        self.journal = journal
        self.ticket_generator = ticket_generator

    def run(self) -> None:
        print("Для выхода нажмите ESC.")
        print(f"Журнал: {JOURNAL.resolve()}")

        while True:
            last_name = self.input.prompt("Last name: ")
            if last_name is None:
                return

            first_name = self.input.prompt("First name: ")
            if first_name is None:
                return

            ticket = self.ticket_generator.generate()
            created_at = datetime.now()

            while True:
                try:
                    self.journal.append(last_name, first_name, ticket, created_at)
                    break
                except PermissionError as error:
                    print(error)
                    print("Закройте journal.xlsx в Excel, нажмите Enter для повтора или ESC для выхода.")
                    key = self.input.read_key()
                    if key == ESC:
                        print("\nЗапись не сохранена. Завершение работы.")
                        return
                    if key not in ("\r", "\n"):
                        continue

            print(f"Билет № {ticket}")


def main() -> None:
    application = TicketApplication(
        ConsoleLineInput(),
        ExcelJournalRepository(JOURNAL),
        RandomTicketGenerator(),
    )
    application.run()


if __name__ == "__main__":
    main()
