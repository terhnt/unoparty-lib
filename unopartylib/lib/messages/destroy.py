#! /usr/bin/python3

"""Destroy a quantity of an asset."""

import struct
import json
import logging
logger = logging.getLogger(__name__)

from unopartylib.lib import util
from unopartylib.lib import config
from unopartylib.lib import script
from unopartylib.lib import message_type
from unopartylib.lib.script import AddressError
from unopartylib.lib.exceptions import *

FORMAT = '>QQ'
LENGTH = 8 + 8
MAX_TAG_LENGTH = 34
ID = 110


def initialise(db):
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS destructions(
                      tx_index INTEGER PRIMARY KEY,
                      tx_hash TEXT UNIQUE,
                      block_index INTEGER,
                      source TEXT,
                      asset INTEGER,
                      quantity INTEGER,
                      tag TEXT,
                      status TEXT,
                      FOREIGN KEY (tx_index, tx_hash, block_index) REFERENCES transactions(tx_index, tx_hash, block_index))
                   ''')
    cursor.execute('''CREATE INDEX IF NOT EXISTS
                      status_idx ON destructions (status)
                   ''')
    cursor.execute('''CREATE INDEX IF NOT EXISTS
                      address_idx ON destructions (source)
                   ''')


def pack(db, asset, quantity, tag):
    data = message_type.pack(ID)
    if isinstance(tag, str):
        tag = bytes(tag.encode('utf8'))[0:MAX_TAG_LENGTH]
    elif isinstance(tag, bytes):
        tag = tag[0:MAX_TAG_LENGTH]
    else:
        tag = b''

    data += struct.pack(FORMAT, util.get_asset_id(db, asset, util.CURRENT_BLOCK_INDEX), quantity)
    data += tag
    return data


def unpack(db, message):
    try:
        asset_id, quantity = struct.unpack(FORMAT, message[0:16])
        tag = message[16:]
        asset = util.get_asset_name(db, asset_id, util.CURRENT_BLOCK_INDEX)

    except struct.error:
        raise UnpackError('could not unpack')

    except AssetIDError:
        raise UnpackError('asset id invalid')

    return asset, quantity, tag


def validate (db, source, destination, asset, quantity):

    try:
        util.get_asset_id(db, asset, util.CURRENT_BLOCK_INDEX)
    except AssetError:
        raise ValidateError('asset invalid')

    try:
        script.validate(source)
    except AddressError:
        raise ValidateError('source address invalid')

    if destination:
        raise ValidateError('destination exists')

    if asset == config.BTC:
        raise ValidateError('cannot destroy {}'.format(config.BTC))

    if type(quantity) != int:
        raise ValidateError('quantity not integer')

    if quantity > config.MAX_INT:
        raise ValidateError('integer overflow, quantity too large')

    if quantity < 0:
        raise ValidateError('quantity negative')

    if util.get_balance(db, source, asset) < quantity:
        raise BalanceError('balance insufficient')


def compose (db, source, asset, quantity, tag):
    # resolve subassets
    asset = util.resolve_subasset_longname(db, asset)

    validate(db, source, None, asset, quantity)
    data = pack(db, asset, quantity, tag)

    return (source, [], data)


def parse (db, tx, message):
    status = 'valid'

    asset, quantity, tag = None, None, None

    try:
        asset, quantity, tag = unpack(db, message)
        validate(db, tx['source'], tx['destination'], asset, quantity)
        util.debit(db, tx['source'], asset, quantity, 'destroy', tx['tx_hash'])

    except UnpackError as e:
        status = 'invalid: ' + ''.join(e.args)

    except (ValidateError, BalanceError) as e:
        status = 'invalid: ' + ''.join(e.args)

    bindings = {
                'tx_index': tx['tx_index'],
                'tx_hash': tx['tx_hash'],
                'block_index': tx['block_index'],
                'source': tx['source'],
                'asset': asset,
                'quantity': quantity,
                'tag': tag,
                'status': status,
               }
    if "integer overflow" not in status:
        sql = 'insert into destructions values(:tx_index, :tx_hash, :block_index, :source, :asset, :quantity, :tag, :status)'
        cursor = db.cursor()
        cursor.execute(sql, bindings)
    else:
        logger.warn("Not storing [destroy] tx [%s]: %s" % (tx['tx_hash'], status))
        logger.debug("Bindings: %s" % (json.dumps(bindings), ))


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
