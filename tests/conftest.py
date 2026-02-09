import pytest


@pytest.fixture
def transmitter_packet():
    return "5555553475c58c0000800d000027b10000008e01000e240"


@pytest.fixture
def search_mode_packet():
    return "5555553475c58cffff100d000000000000000000006fd80"


@pytest.fixture
def corrupted_syncword_packet():
    return "5555559999c58c0000800d000027b10000008e01000e240"


@pytest.fixture
def corrupted_crc_packet():
    return "5555553475c58c0000800d000027b10000008e0100123450"


@pytest.fixture
def corrupted_data_packet():
    return "5555553475c58c0000800d000027b10000009e01000e240"


@pytest.fixture
def missing_preamble_packet():
    return "3475c58c0000800d000027b10000008e01000e240"


@pytest.fixture
def too_short_packet():
    return "5555553475c58c0000800d"


@pytest.fixture
def empty_packet():
    return ""


@pytest.fixture
def uppercase_packet():
    return "5555553475C58C0000800D000027B10000008E01000E240"


@pytest.fixture
def lowercase_packet():
    return "5555553475c58c0000800d000027b10000008e01000e240"


@pytest.fixture
def max_total_ah_packet():
    return "5555553475c58c0000800d00ffffff00000000010003af20"


@pytest.fixture
def max_current_a_packet():
    return "5555553475c58c0000800d000000000000ffff0100f8a30"


@pytest.fixture
def zero_values_packet():
    return "5555553475c58c0000800d000000000000000000006fd80"
