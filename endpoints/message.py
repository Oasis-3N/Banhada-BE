from flask import Blueprint
from methods import message
from constants import messages
from methods.account import get_uuid
from methods.article import if_article_exist
from . import is_api

message_blueprint = Blueprint('Message', __name__)


@message_blueprint.route('/get_messages', methods=['GET'])
@is_api(required_keys=['group_id'])
def get_messages(data):
    if not message.if_group_exist(data['group_id']):
        return {"error": messages.no_exists.format('group')}, 404

    status, info, status_code = message.get_messages(**data)

    if not status:
        return {'error': info}, status_code

    else:
        return info


@message_blueprint.route('/get_message_groups', methods=['GET'])
@is_api(required_keys=['id'])
def get_message_groups(data):
    data['user_uuid'] = get_uuid(data['id'])
    del data['id']
    status, info, status_code = message.get_message_groups(**data)

    if not status:
        return {'error': info}, status_code

    else:
        return info


@message_blueprint.route('/send_message', methods=['POST'])
@is_api(required_keys=['id', 'group_id'], acceptable_keys=['image', 'content'], input_type='json')
def send_message(data):
    data['user_uuid'] = get_uuid(data['id'])
    del data['id']

    if not message.if_group_exist(data['group_id']):
        return {"error": messages.no_exists.format('group')}, 404
    if not message.if_user_in_group(data['user_uuid'], data['group_id']):
        return {"error": "no authority"}, 403

    if 'image' not in data:
        data['image'] = ''
    if 'content' not in data:
        data['content'] = ''

    status, info, status_code = message.send_message(**data)

    if not status:
        return {'error': info}, status_code
    else:
        return {'message': info}


@message_blueprint.route('/make_group', methods=['POST'])
@is_api(required_keys=['article_id', 'buyer_id'], input_type='json')
def make_group(data):
    if not if_article_exist(data['article_id']):
        return {'message': messages.no_exists.format('article')}, 404

    buyer_uuid = get_uuid(data['buyer_id'])

    if message.if_group_made(data['article_id'], buyer_uuid):
        return {'message': "group_already_made"}, 201
    if message.if_buyer_post_article(data['article_id'], buyer_uuid):
        return {'message': "own_article"}, 201

    status, info, status_code = message.make_group(data['article_id'], buyer_uuid)

    if not status:
        return {'error': info}, status_code
    else:
        return {'message': info}
