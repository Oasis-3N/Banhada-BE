import uuid
from connector import MySQL
from passlib.hash import bcrypt_sha256
from constants.account import *


def get_uuid(id):
    sql = MySQL()
    result = sql.query('SELECT uuid FROM account WHERE id=%s', (id, ))
    if len(result) == 1:
        return uuid.UUID(bytes=result[0][0])

    return None


def register(email, id, username, password, address, nickname):
    sql = MySQL()
    user_uuid = uuid.uuid4()
    while True:
        if sql.query('SELECT COUNT(*) FROM account WHERE uuid=%s', (user_uuid.bytes, ))[0][0] == 0:
            break
        else:
            user_uuid = uuid.uuid4()

    if sql.query('SELECT COUNT(*) FROM account WHERE email LIKE %s', (email,))[0][0] != 0:
        return False, 'email_exists'
    elif len(email) > 255:
        return False, 'email_too_long'

    if sql.query('SELECT COUNT(*) FROM account WHERE nickname LIKE %s', (nickname,))[0][0] != 0:
        return False, 'nickname_exists'
    elif len(nickname) > 100:
        return False, 'nickname_too_long'

    if len(username) > 100:
        return False, 'name_too_long'

    password = bcrypt_sha256.encrypt(password, rounds=bcrypt_hash_rounds)

    sql.transaction.start()

    try:
        sql.query('INSERT INTO account (uuid, id, email, username, password, address, nickname) '
                  'VALUE (%s, %s, %s, %s, %s, %s, %s)',
                  (user_uuid.bytes, id, email, username, password, address, nickname))

    except Exception as e:
        print(e)
        sql.transaction.rollback()
        return False, 'exception_occurred'

    else:
        sql.transaction.commit()
        return True, None


def login(id, password):
    sql = MySQL()

    pw_hash = sql.query('SELECT password FROM account WHERE id=%s', (id, ))
    if len(pw_hash) != 1:
        return False

    return bcrypt_sha256.verify(password, pw_hash[0][0])


def get_user_data(user_uuid: uuid.UUID):
    sql = MySQL(dict_cursor=True)

    data = sql.query('SELECT uuid, id, email, username, address, nickname, rate, image FROM account WHERE uuid=%s',
                     (user_uuid.bytes, ))

    if len(data) != 1:
        return None
    else:
        data = data[0]
        data['uuid'] = str(uuid.UUID(bytes=data['uuid']))

        return data
