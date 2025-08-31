import re

serial_number_regex = r"^[0-9]{6}"


def is_valid_serial_number(serial_number: str) -> bool:
    return re.fullmatch(pattern=serial_number_regex, string=serial_number) is not None


def is_valid_card_number(card_number: str) -> bool:
    return is_valid_serial_number(
        card_number
    )  # assuming books and cards serials validation logic are same
