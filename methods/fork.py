from uuid import UUID

from connector import MySQL
from constants import messages


def make_fork(user_uuid: UUID, article_id: int):
    sql = MySQL()

    if user_uuid is None or article_id is None:
        return False, messages.no_required_args, 400

    sql.transaction.start()
    try:
        sql.query('INSERT INTO fork (uuid, article_id) VALUE (%s, %s)', (user_uuid.bytes, article_id, ))
    except Exception as e:
        sql.transaction.rollback()
        print(e)
    else:
        sql.transaction.commit()
        return True, {"message": "inserted"}, 200


def delete_fork(user_uuid: UUID, article_id: int):
    sql = MySQL()

    if sql.query('SELECT COUNT(*) FROM fork WHERE uuid=%s AND article_id=%s', (user_uuid.bytes, article_id, ))[0][0] != 1:
        return False, messages.no_exists.format('fork'), 404

    sql.transaction.start()
    try:
        sql.query('DELETE FROM fork WHERE uuid=%s AND article_id=%s', (user_uuid.bytes, article_id, ))
    except Exception as e:
        sql.transaction.rollback()
        print(e)
    else:
        sql.transaction.commit()
        return True, {"message": "delete_complete"}, 200


def get_fork_list(user_uuid: UUID):
    sql = MySQL(dict_cursor=True)

    result = list(sql.query('SELECT article_id FROM fork WHERE uuid=%s', (user_uuid.bytes, )))

    response_list = list()
    for article in result:
        res = sql.query('SELECT id, title, submitter, cost, views, remain_time, image '
                        'FROM article WHERE id=%s', (article['article_id'], ))[0]
        res['submitter'] = sql.query('SELECT nickname FROM account WHERE uuid=%s', (UUID(bytes=res['submitter']).bytes, ))[0]['nickname']
        res['fork_num'] = len(list(sql.query('SELECT uuid FROM fork WHERE article_id=%s', (res['id'], ))))

        response_list.append(res)

    return True, response_list, 200
