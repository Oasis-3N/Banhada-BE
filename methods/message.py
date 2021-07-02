from uuid import UUID

from connector import MySQL
from constants import messages


def get_messages(group_id: int):
    sql = MySQL(dict_cursor=True)

    result = list(sql.query('SELECT submitter, message, image, reg_date FROM messages '
                            'WHERE group_id=%s ORDER BY reg_date asc', (group_id,)))

    for i in range(len(result)):
        if result[i]['message'] is None:
            result[i]['message'] = ""
        submitter_info = sql.query('SELECT nickname, image FROM account WHERE uuid=%s',
                                   (UUID(bytes=result[i]['submitter']).bytes, ))[0]
        result[i]['submitter'] = submitter_info['nickname']
        result[i]['profile_image'] = submitter_info['image']

    return True, result, 200


def get_message_groups(user_uuid: UUID):
    sql = MySQL(dict_cursor=True)

    group_list = list(sql.query('SELECT id , article_id, seller_uuid, buyer_uuid FROM message_group '
                                'WHERE seller_uuid=%s OR buyer_uuid=%s', (user_uuid.bytes, user_uuid.bytes, )))

    if len(group_list) == 0:
        return True, list()

    new_group_dict_list = list()

    for group in group_list:
        new_group_list = dict()
        new_group_list['group_id'] = group['id']

        message_recent = list(sql.query('SELECT message FROM messages '
                                        'WHERE group_id=%s ORDER BY reg_date asc', (group['id'], )))
        if len(message_recent) == 0:
            message_recent = " "
        else:
            message_recent = message_recent[-1]['message']
        if message_recent is None or message_recent == "":
            new_group_list['preview'] = "no image"
        else:
            new_group_list['preview'] = message_recent

        new_group_list['article_id'] = group['article_id']

        if str(group['seller_uuid']) == str(user_uuid.bytes):
            new_group_list['counter_nickname'] = sql.query('SELECT nickname FROM account WHERE uuid=%s',
                                                           (group['buyer_uuid'], ))[0]['nickname']
        else:
            new_group_list['counter_nickname'] = sql.query('SELECT nickname FROM account WHERE uuid=%s',
                                                           (UUID(bytes=group['seller_uuid']).bytes,))[0]['nickname']

        new_group_list['image'] = sql.query('SELECT image FROM article WHERE id=%s',
                                            (group['article_id'], ))[0]['image']
        if new_group_list['image'] is None or new_group_list['image'] == "":
            new_group_list['image'] = "no image"

        new_group_dict_list.append(new_group_list)

    return True, new_group_dict_list, 200


def send_message(user_uuid: UUID, group_id: int, image: str, content: str):
    sql = MySQL()

    if user_uuid is None or group_id is None:
        return False, messages.no_required_args, 400

    sql.transaction.start()
    try:
        sql.query('INSERT INTO messages '
                  '(group_id, submitter, message, image) '
                  'VALUE (%s, %s, %s, %s)', (group_id, user_uuid.bytes, content, image, ))
    except Exception as e:
        print(e)
        sql.transaction.rollback()
        return False, messages.exception_occurred, 500
    else:
        inserted = sql.query('SELECT LAST_INSERT_ID()')[0][0]
        sql.transaction.commit()
        return True, inserted, 200


def make_group(article_id: int, buyer_uuid: UUID):
    sql = MySQL()

    seller_uuid = UUID(bytes=sql.query('SELECT submitter FROM article WHERE id=%s', (article_id, ))[0][0])

    sql.transaction.start()
    try:
        sql.query('INSERT INTO message_group (article_id, seller_uuid, buyer_uuid) '
                  'VALUE (%s, %s, %s)', (article_id, seller_uuid.bytes, buyer_uuid.bytes))
    except Exception as e:
        print(e)
        sql.transaction.rollback()
        return False, messages.exception_occurred, 500
    else:
        sql.transaction.commit()
        last_inserted = sql.query('SELECT LAST_INSERT_ID()')[0][0]
        return True, last_inserted, 200


def if_group_exist(group_id: int):
    sql = MySQL()
    if sql.query('SELECT COUNT(*) FROM message_group WHERE id=%s', (group_id, ))[0][0] == 1:
        return True
    else:
        return False


def if_user_in_group(user_uuid: UUID, group_id: int):
    sql = MySQL()
    if sql.query('SELECT COUNT(*) FROM message_group '
                 'WHERE (seller_uuid=%s OR buyer_uuid=%s) AND id=%s',
                 (user_uuid.bytes, user_uuid.bytes, group_id))[0][0] == 1:
        return True
    else:
        return False


def if_group_made(article_id: int, buyer_uuid: UUID):
    sql = MySQL()
    if sql.query('SELECT COUNT(*) FROM message_group '
                 'WHERE article_id=%s AND buyer_uuid=%s', (article_id, buyer_uuid.bytes, ))[0][0] == 1:
        return True
    else:
        return False


def if_buyer_post_article(article_id: int, buyer_uuid: UUID):
    sql = MySQL(dict_cursor=True)
    article_submitter = sql.query('SELECT submitter FROM article WHERE id=%s', (article_id, ))[0]['submitter']
    if str(article_submitter) == str(buyer_uuid.bytes):
        return True
    else:
        return False
