import re
from typing import Tuple

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

    # Regex patterns for different types
    # DNI: 8 digits + 1 letter (e.g., 12345678Z)
    # NIE: X/Y/Z + 7 digits + 1 letter (e.g., X1234567L)
    # CIF: Letter + 8 digits (last char can be digit or letter)

    # DNI Pattern
    dni_pattern = re.compile(r'^\d{8}[A-Z]$')
    # NIE Pattern
    nie_pattern = re.compile(r'^[XYZ]\d{7}[A-Z]$')
    # CIF Pattern (includes old CIF and new NIF for entities)
    cif_pattern = re.compile(r'^[ABCDEFGHJNPQRSUVW]\d{7}[\dA-J]$')

    # DNI Validation
    if dni_pattern.match(normalized):
        return _validate_dni(normalized), normalized

    # NIE Validation (convert X/Y/Z to 0/1/2 and validate as DNI)
    if nie_pattern.match(normalized):
        return _validate_nie(normalized), normalized

    # CIF Validation
    if cif_pattern.match(normalized):
        return _validate_cif(normalized), normalized

    return False, normalized


def _validate_dni(nif: str) -> bool:
    """Validate DNI (8 digits + control letter)"""
    control_letters = "TRWAGMYFPDXBNJZSQVHLCKE"
    number = int(nif[:8])
    expected_letter = control_letters[number % 23]
    return nif[8] == expected_letter


def _validate_nie(nie: str) -> bool:
    """Validate NIE (X/Y/Z + 7 digits + control letter)"""
    # Replace first letter: X=0, Y=1, Z=2
    replacement = {'X': '0', 'Y': '1', 'Z': '2'}
    dni_like = replacement[nie[0]] + nie[1:]
    return _validate_dni(dni_like)


def _validate_cif(cif: str) -> bool:
    """Validate CIF (Letter + 7 digits + control character)"""
    # Weights for the algorithm
    weights = [2, 4, 8, 5, 10, 9, 7, 3, 6]  # Not all used, standard is 2,1,2,1,2,1,2,1

    # Actually, CIF uses a specific algorithm:
    # Even positions (2,4,6,8): sum of digits
    # Odd positions (1,3,5,7): multiply by 2, sum digits of result
    # Total sum, control = (10 - (sum % 10)) % 10
    # Control can be digit (0-9) or letter (A-J for 0-9)

    if len(cif) != 9:
        return False

    first_char = cif[0]
    numbers = cif[1:8]
    control_char = cif[8]

    # Only certain first letters are valid for CIF
    valid_first_letters = "ABCDEFGHJNPQRSUVW"
    if first_char not in valid_first_letters:
        return False

    # Calculate checksum
    total = 0

    # Positions 1,3,5,7 (0-indexed: 0,2,4,6 in the 7-digit number)
    for i in [0, 2, 4, 6]:
        doubled = int(numbers[i]) * 2
        total += doubled if doubled < 10 else doubled - 9

    # Positions 2,4,6,8 (0-indexed: 1,3,5 in the 7-digit number)
    for i in [1, 3, 5]:
        total += int(numbers[i])

    # Position 8 (index 7) - for some CIF types this is also included
    # Actually standard CIF: positions 1,3,5,7 of the 8-char body (indices 0,2,4,6)
    # and positions 2,4,6,8 (indices 1,3,5,7)
    total += int(numbers[7])

    control_digit = (10 - (total % 10)) % 10

    # Control can be digit or letter A-J (where A=0, B=1, ..., J=9)
    if control_char.isdigit():
        return int(control_char) == control_digit
    else:
        # Letter control: A=0, B=1, ..., J=9
        letter_value = ord(control_char) - ord('A')
        return 0 <= letter_value <= 9 and letter_value == control_digit


def get_tax_id_type(tax_id: str) -> str:
    """Returns the type of tax ID: 'DNI', 'NIE', 'CIF', or 'UNKNOWN'"""
    normalized = tax_id.upper().strip().replace(" ", "")

    dni_pattern = re.compile(r'^\d{8}[A-Z]$')
    nie_pattern = re.compile(r'^[XYZ]\d{7}[A-Z]$')
    cif_pattern = re.compile(r'^[ABCDEFGHJNPQRSUVW]\d{7}[\dA-J]$')

    if dni_pattern.match(normalized):
        return "DNI"
    elif nie_pattern.match(normalized):
        return "NIE"
    elif cif_pattern.match(normalized):
        return "CIF"
    return "UNKNOWN"