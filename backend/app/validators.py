import re
from typing import Tuple

# CIF first letter to value mapping (per official AEAT algorithm)
CIF_LETTER_VALUES = {
    'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15, 'G': 16, 'H': 17,
    'J': 18, 'N': 19, 'P': 20, 'Q': 21, 'R': 22, 'S': 23, 'U': 24, 'V': 25, 'W': 26
}

# Control letter mapping for CIF (1=A, 2=B, ..., 9=I, 0=J)
CIF_CONTROL_LETTERS = "JABCDEFGHI"

# DNI control letters
DNI_CONTROL_LETTERS = "TRWAGMYFPDXBNJZSQVHLCKE"

# Valid first letters for CIF
VALID_CIF_FIRST_LETTERS = "ABCDEFGHJNPQRSUVW"


def validate_spanish_tax_id(tax_id: str) -> Tuple[bool, str]:
    """
    Validates a Spanish NIF/NIE/CIF (Tax ID) according to official algorithms.

    Returns:
        Tuple[bool, str]: (is_valid, normalized_tax_id)
    """
    if not tax_id:
        return False, ""

    # Normalize: uppercase, remove spaces
    normalized = tax_id.upper().strip().replace(" ", "")

    # DNI Pattern: 8 digits + 1 letter
    dni_pattern = re.compile(r'^\d{8}[A-Z]$')
    # NIE Pattern: X/Y/Z + 7 digits + 1 letter
    nie_pattern = re.compile(r'^[XYZ]\d{7}[A-Z]$')
    # CIF Pattern: Letter + 7 digits + 1 control (digit or letter A-J)
    cif_pattern = re.compile(r'^[ABCDEFGHJNPQRSUVW]\d{7}[\dA-J]$')

    if dni_pattern.match(normalized):
        return _validate_dni(normalized), normalized
    if nie_pattern.match(normalized):
        return _validate_nie(normalized), normalized
    if cif_pattern.match(normalized):
        return _validate_cif(normalized), normalized

    return False, normalized


def _validate_dni(dni: str) -> bool:
    """Validate DNI (8 digits + control letter)"""
    if not re.match(r'^\d{8}[A-Z]$', dni):
        return False
    try:
        number = int(dni[:8])
        return dni[8] == DNI_CONTROL_LETTERS[number % 23]
    except (ValueError, IndexError):
        return False


def _validate_nie(nie: str) -> bool:
    """Validate NIE (X/Y/Z + 7 digits + control letter)"""
    if not re.match(r'^[XYZ]\d{7}[A-Z]$', nie):
        return False
    # Replace first letter: X=0, Y=1, Z=2
    replacement = {'X': '0', 'Y': '1', 'Z': '2'}
    dni_like = replacement[nie[0]] + nie[1:]
    return _validate_dni(dni_like)


def _validate_cif(cif: str) -> bool:
    """Validate CIF (Letter + 7 digits + control character) - Official AEAT algorithm"""
    if not re.match(r'^[ABCDEFGHJNPQRSUVW]\d{7}[\dA-J]$', cif):
        return False

    first_char = cif[0]
    body_digits = cif[1:8]
    control_char = cif[8]

    try:
        letter_value = CIF_LETTER_VALUES[first_char]
    except KeyError:
        return False

    # Official AEAT algorithm for CIF:
    # - Digits in odd positions (1st, 3rd, 5th, 7th) are multiplied by 2
    # - Digits in even positions (2nd, 4th, 6th) are added as-is
    # - Sum all, control digit = (10 - (sum % 10)) % 10
    total = 0
    digits = [int(d) for d in body_digits]
    for i, d in enumerate(digits):
        if i % 2 == 0:  # odd position (1st, 3rd, 5th, 7th)
            product = d * 2
            total += product if product < 10 else product - 9
        else:  # even position (2nd, 4th, 6th)
            total += d

    control_digit = (10 - (total % 10)) % 10

    if control_char.isdigit():
        return int(control_char) == control_digit
    else:
        return control_char == CIF_CONTROL_LETTERS[control_digit]


def get_tax_id_type(tax_id: str) -> str:
    """Returns the type of tax ID: 'DNI', 'NIE', 'CIF', or 'UNKNOWN'"""
    normalized = tax_id.upper().strip().replace(" ", "")
    if re.match(r'^\d{8}[A-Z]$', normalized):
        return "DNI"
    if re.match(r'^[XYZ]\d{7}[A-Z]$', normalized):
        return "NIE"
    if re.match(r'^[ABCDEFGHJNPQRSUVW]\d{7}[\dA-J]$', normalized):
        return "CIF"
    return "UNKNOWN"