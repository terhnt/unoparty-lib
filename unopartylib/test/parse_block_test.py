#! /usr/bin/python3
import pprint
import tempfile
from unopartylib.test import conftest  # this is require near the top to do setup of the test suite
from unopartylib.test.fixtures.params import DEFAULT_PARAMS as DP
from unopartylib.test.util_test import CURR_DIR

from unopartylib.lib import (blocks)


FIXTURE_SQL_FILE = CURR_DIR + '/fixtures/scenarios/parseblock_unittest_fixture.sql'
FIXTURE_DB = tempfile.gettempdir() + '/fixtures.parseblock_unittest_fixture.db'


def test_parse_block(server_db):
    test_outputs = blocks.parse_block(server_db, DP['default_block_index'], 1420914478)
    outputs = ('44cf374045f44caf86c7b7de61de3e712f4ba3c39523ab95bc68149ef8aede18',
               'b4d68165bdbd4e14cf5f426bd32d9ebf831688f97b4d2a99340afc7db5817ba0',
               'fafa399384e61785222b285cf1cde836cd8b64edbb8c1087bf4a28c9ace84f95',
               None)
    try:
        assert outputs == test_outputs
    except AssertionError:
        msg = "expected outputs don't match test_outputs:\noutputs=\n" + pprint.pformat(outputs) + "\ntest_outputs=\n" + pprint.pformat(test_outputs)
        raise AssertionError(msg)
