import pytest
from app.validators import (
    validate_spanish_tax_id,
    _validate_dni,
    _validate_nie,
    _validate_cif,
    get_tax_id_type
)


class TestValidateSpanishTaxId:
    """Tests for the main Spanish tax ID validation function."""

    # Valid DNI examples (calculated with correct control letters)
    @pytest.mark.parametrize("dni", [
        "12345678Z",
        "87654321X",
        "11111111H",
        "99999999R",
        "52892374X",  # Correct control letter for 52892374
    ])
    def test_valid_dni(self, dni):
        """Test valid DNI numbers pass validation."""
        is_valid, normalized = validate_spanish_tax_id(dni)
        assert is_valid is True
        assert normalized == dni.upper()

    # Valid NIE examples (X=0, Y=1, Z=2 prefix, calculated with correct control letters)
    @pytest.mark.parametrize("nie", [
        "X1234567L",
        "Y8765432P",  # Correct control for 18765432
        "Z9999999H",  # Correct control for 29999999
        "X0000001R",  # Correct control for 00000001
    ])
    def test_valid_nie(self, nie):
        """Test valid NIE numbers pass validation."""
        is_valid, normalized = validate_spanish_tax_id(nie)
        assert is_valid is True
        assert normalized == nie.upper()

    # Valid CIF examples (calculated with correct AEAT algorithm)
    @pytest.mark.parametrize("cif", [
        "B87654327",
        "A12345679",
        "G55555551",
        "Q12345678",
        "P11111110",
        "P1111111J",  # Letter control J=0
    ])
    def test_valid_cif(self, cif):
        """Test valid CIF numbers pass validation."""
        is_valid, normalized = validate_spanish_tax_id(cif)
        assert is_valid is True
        assert normalized == cif.upper()

    # Invalid formats
    @pytest.mark.parametrize("invalid_id", [
        "",              # Empty
        "123",           # Too short
        "123456789012",  # Too long
        "12345678",      # Missing control char
        "ABCDEFGHI",     # All letters
        "123456789",     # All digits (9 digits)
        "1234567A",      # 7 digits + letter
        "X123456",       # NIE too short
        "B1234567",      # CIF missing control
        "I12345678",     # Invalid first letter for CIF
        "Ñ12345678",     # Invalid character
        "12345678@",     # Invalid character
        "  ",            # Whitespace only
    ])
    def test_invalid_formats_rejected(self, invalid_id):
        """Test various invalid formats are rejected."""
        is_valid, normalized = validate_spanish_tax_id(invalid_id)
        assert is_valid is False

    def test_lowercase_input_normalized(self):
        """Lowercase input should be normalized to uppercase."""
        is_valid, normalized = validate_spanish_tax_id("b87654327")
        assert is_valid is True
        assert normalized == "B87654327"

    def test_whitespace_handled(self):
        """Whitespace should be stripped."""
        is_valid, normalized = validate_spanish_tax_id(" B87654327 ")
        assert is_valid is True
        assert normalized == "B87654327"

    def test_internal_spaces_removed(self):
        """Internal spaces should be removed."""
        is_valid, normalized = validate_spanish_tax_id("B8 765 4327")
        assert is_valid is True
        assert normalized == "B87654327"


class TestValidateDni:
    """Tests for DNI-specific validation."""

    @pytest.mark.parametrize("dni,expected", [
        ("12345678Z", True),
        ("12345678A", False),  # Wrong control letter
        ("00000000T", True),
        ("99999999R", True),
        ("52892374X", True),   # Correct control letter
        ("52892374D", False),  # Wrong control letter
    ])
    def test_dni_control_letter(self, dni, expected):
        """Test DNI control letter validation."""
        assert _validate_dni(dni) == expected


class TestValidateNie:
    """Tests for NIE-specific validation."""

    @pytest.mark.parametrize("nie,expected", [
        ("X1234567L", True),
        ("Y8765432P", True),   # Correct control letter
        ("Z9999999H", True),   # Correct control letter
        ("X0000001R", True),   # Correct control letter
        ("X1234567A", False),  # Wrong control letter
        ("W1234567L", False),  # Invalid first letter
    ])
    def test_nie_validation(self, nie, expected):
        """Test NIE validation with X/Y/Z prefixes."""
        assert _validate_nie(nie) == expected


class TestValidateCif:
    """Tests for CIF-specific validation."""

    @pytest.mark.parametrize("cif,expected", [
        ("B87654327", True),   # Correct control digit
        ("A12345679", True),   # Correct control digit
        ("G55555551", True),   # Correct control digit
        ("Q12345678", True),   # Correct control digit
        ("P11111110", True),   # Correct control digit 0
        ("P1111111J", True),   # Letter control J=0
        ("B87654322", False),  # Wrong control digit
        ("I12345678", False),  # Invalid first letter (I not in valid set)
        ("Ñ12345678", False),  # Invalid first letter
        ("B1234567", False),   # Too short
        ("B123456789", False), # Too long
    ])
    def test_cif_validation(self, cif, expected):
        """Test CIF validation algorithm."""
        assert _validate_cif(cif) == expected

    def test_cif_letter_control(self):
        """Test CIF with letter control character (A-J)."""
        # CIF_CONTROL_LETTERS = 'JABCDEFGHI' means J=0, A=1, B=2, ..., I=9
        # CIF P1111111J should have control J=0
        assert _validate_cif("P1111111J") is True
        assert _validate_cif("P1111111K") is False


class TestGetTaxIdType:
    """Tests for tax ID type detection."""

    @pytest.mark.parametrize("tax_id,expected_type", [
        ("12345678Z", "DNI"),
        ("87654321X", "DNI"),
        ("X1234567L", "NIE"),
        ("Y8765432P", "NIE"),
        ("Z9999999H", "NIE"),
        ("B87654327", "CIF"),
        ("A12345679", "CIF"),
        ("G55555551", "CIF"),
        ("123", "UNKNOWN"),
        ("", "UNKNOWN"),
        ("ABCDEFGHI", "UNKNOWN"),
    ])
    def test_type_detection(self, tax_id, expected_type):
        """Test tax ID type classification."""
        assert get_tax_id_type(tax_id) == expected_type