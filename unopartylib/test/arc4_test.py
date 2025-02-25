import pprint
import tempfile
import pytest
from unopartylib.test import conftest  # this is require near the top to do setup of the test suite
from unopartylib.test import util_test
from unopartylib.test.util_test import CURR_DIR
from unopartylib.test.fixtures.params import DP, ADDR

from unopartylib.lib import util
from unopartylib.lib import arc4
from unopartylib.lib.messages import send
from unopartylib.lib import transaction

FIXTURE_SQL_FILE = CURR_DIR + '/fixtures/scenarios/unittest_fixture.sql'
FIXTURE_DB = tempfile.gettempdir() + '/fixtures.unittest_fixture.db'


def test_arc4_mocked():
    """
    by default init_arc4 should be mocked in the test suite to always use `'00' * 32` as seed.
     so when we use `'01' * 32` as seed it should still return the same result as `'00' * 32` or as ``
    """
    text = bytes("testing", 'utf-8')

    # '00' * 32 encrypt
    k = arc4.init_arc4('00' * 32)
    assert k.encrypt(text) == b'\xaa}\xfa5\xcaY:'

    # '00' * 32 decrypt
    k = arc4.init_arc4('00' * 32)
    assert k.decrypt(b'\xaa}\xfa5\xcaY:') == text

    # b'\x00' * 32 encrypt
    k = arc4.init_arc4(b'\x00' * 32)
    assert k.encrypt(text) == b'\xaa}\xfa5\xcaY:'

    # b'\x00' * 32 decrypt
    k = arc4.init_arc4(b'\x00' * 32)
    assert k.decrypt(b'\xaa}\xfa5\xcaY:') == text

    # '' * 32 encrypt
    k = arc4.init_arc4('' * 32)
    assert k.encrypt(text) == b'\xaa}\xfa5\xcaY:'

    # '' * 32 decrypt
    k = arc4.init_arc4('' * 32)
    assert k.decrypt(b'\xaa}\xfa5\xcaY:') == text

    # b'' * 32 encrypt
    k = arc4.init_arc4(b'' * 32)
    assert k.encrypt(text) == b'\xaa}\xfa5\xcaY:'

    # b'' * 32 decrypt
    k = arc4.init_arc4(b'' * 32)
    assert k.decrypt(b'\xaa}\xfa5\xcaY:') == text

    # '01' * 32 encrypt
    k = arc4.init_arc4('01' * 32)
    assert k.encrypt(text) == b'\xaa}\xfa5\xcaY:'

    # '01' * 32 decrypt
    k = arc4.init_arc4('01' * 32)
    assert k.decrypt(b'\xaa}\xfa5\xcaY:') == text

    # b'\x01' * 32 encrypt
    k = arc4.init_arc4(b'\x01' * 32)
    assert k.encrypt(text) == b'\xaa}\xfa5\xcaY:'

    # b'\x01' * 32 decrypt
    k = arc4.init_arc4(b'\x01' * 32)
    assert k.decrypt(b'\xaa}\xfa5\xcaY:') == text


def test_arc4_unmocked():
    """
        by default init_arc4 should be mocked in the test suite to always use `'00' * 32` as seed
         but with DISABLE_ARC4_MOCKING=True it should be disabled and actually produce different results
        """
    with util_test.ConfigContext(DISABLE_ARC4_MOCKING=True):
        text = bytes('testing', 'utf-8')
        k = arc4.init_arc4('00' * 32)
        assert k.encrypt(text) == b'\xaa}\xfa5\xcaY:'

        # '00' * 32 decrypt
        k = arc4.init_arc4('00' * 32)
        assert k.decrypt(b'\xaa}\xfa5\xcaY:') == text

        # b'\x00' * 32 encrypt
        k = arc4.init_arc4(b'\x00' * 32)
        assert k.encrypt(text) == b'\xaa}\xfa5\xcaY:'

        # b'\x00' * 32 decrypt
        k = arc4.init_arc4(b'\x00' * 32)
        assert k.decrypt(b'\xaa}\xfa5\xcaY:') == text

        # '' * 32 encrypt, not allowed
        with pytest.raises(ValueError):
            k = arc4.init_arc4('' * 32)
            assert k.encrypt(text) == b'\xaa}\xfa5\xcaY:'

        # '01' * 32 encrypt
        k = arc4.init_arc4('01' * 32)
        assert k.encrypt(text) == b'rm}zqNN'

        # '01' * 32 decrypt
        k = arc4.init_arc4('01' * 32)
        assert k.decrypt(b'rm}zqNN') == text

        # b'\x01' * 32 encrypt
        k = arc4.init_arc4(b'\x01' * 32)
        assert k.encrypt(text) == b'rm}zqNN'

        # b'\x01' * 32 decrypt
        k = arc4.init_arc4(b'\x01' * 32)
        assert k.decrypt(b'rm}zqNN') == text


@pytest.mark.usefixtures('server_db')
def test_transaction_arc4_mocked(server_db):
    """
    by default init_arc4 should be mocked in the test suite to always use `'00' * 32` as seed.
    """
    v = int(100 * 1e8)
    tx_info = send.compose(server_db, ADDR[0], ADDR[1], 'XUP', v)
    send1hex = transaction.construct(server_db, tx_info)

    assert send1hex == '0100000001c1d8c075936c3495f6d653c50f73d987f75448d97a750249b1eb83bee71b24ae000000001976a914fa070c5a305ef456144e8fdfbb7622efe29cc10288acffffffff0336150000000000001976a91497dfcc531ea6ecca1e53a46492a67bb33dabf80688ac00000000000000001e6a1c8a5dda15fb6f05628a061e67576e926dc71a7fa2f0cceb951120a9322f30ea0b000000001976a914fa070c5a305ef456144e8fdfbb7622efe29cc10288ac00000000'


@pytest.mark.usefixtures('server_db')
def test_transaction_arc4_unmocked(server_db):
    """
    by default init_arc4 should be mocked in the test suite to always use `'00' * 32` as seed
     but with DISABLE_ARC4_MOCKING=True it should be disabled and actually produce different results
    """

    with util_test.ConfigContext(DISABLE_ARC4_MOCKING=True):
        v = int(100 * 1e8)
        tx_info = send.compose(server_db, ADDR[0], ADDR[1], 'XUP', v)
        send1hex = transaction.construct(server_db, tx_info)

        assert send1hex == '0100000001c1d8c075936c3495f6d653c50f73d987f75448d97a750249b1eb83bee71b24ae000000001976a914fa070c5a305ef456144e8fdfbb7622efe29cc10288acffffffff0336150000000000001976a91497dfcc531ea6ecca1e53a46492a67bb33dabf80688ac00000000000000001e6a1c2a504df746f83442653dd7ada4dc727a030865749e9fba58ba71d71a2f30ea0b000000001976a914fa070c5a305ef456144e8fdfbb7622efe29cc10288ac00000000'
