from flask import Blueprint
from methods import fork
from methods.account import get_uuid
from . import is_api

fork_blueprint = Blueprint('Fork', __name__)


@fork_blueprint.route('/make_fork', methods=['POST'])
@is_api(required_keys=['id', 'article_id'], input_type='json')
def make_fork(data):
    data['user_uuid'] = get_uuid(data['id'])
    del data['id']

    status, info, status_code = fork.make_fork(**data)

    if not status:
        return {'error': info}, status_code

    else:
        return info, status_code


@fork_blueprint.route('/delete_fork', methods=['DELETE'])
@is_api(required_keys=['id', 'article_id'], input_type='json')
def delete_fork(data):
    data['user_uuid'] = get_uuid(data['id'])
    del data['id']

    status, info, status_code = fork.delete_fork(**data)

    if not status:
        return {'error': info}, status_code

    else:
        return info, status_code


@fork_blueprint.route('/get_fork_list', methods=['GET'])
@is_api(required_keys=['id'])
def get_fork_list(data):
    data['user_uuid'] = get_uuid(data['id'])
    del data['id']

    status, info, status_code = fork.get_fork_list(**data)

    if not status:
        return {'error': info}, status_code
    else:
        return info, status_code
