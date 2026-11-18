import unittest

from main import RandomTicketGenerator, validate_name


class NameValidationTests(unittest.TestCase):
    def test_rejects_digits(self):
        self.assertIsNotNone(validate_name("123"))
        self.assertIsNotNone(validate_name("Ivan123"))

    def test_rejects_symbols(self):
        self.assertIsNotNone(validate_name("@Student"))
        self.assertIsNotNone(validate_name("O,Connor"))

    def test_accepts_supported_names(self):
        self.assertIsNone(validate_name("Smith"))
        self.assertIsNone(validate_name("O'Connor"))
        self.assertIsNone(validate_name("Иванов"))
        self.assertIsNone(validate_name("Jean-Luc"))


class TicketValidationTests(unittest.TestCase):
    def test_ticket_is_in_supported_range(self):
        generator = RandomTicketGenerator()
        for _ in range(100):
            ticket = generator.generate()
            self.assertGreaterEqual(ticket, 1)
            self.assertLessEqual(ticket, 20)


if __name__ == "__main__":
    unittest.main()
