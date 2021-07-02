from flask import Blueprint
from . import is_api
from methods import account

account_blueprint = Blueprint('Account', __name__)


@account_blueprint.route('/register', methods=['POST'])
@is_api(required_keys=['email', 'id', 'username', 'password', 'address', 'nickname'], input_type='json')
def register(data):
    state, error_code = account.register(**data)

    if not state:
        return {'error': error_code}, (400 if error_code != 'exception_occurred' else 500)
    else:
        return {'registered': True}, 201


@account_blueprint.route('/login', methods=['POST'])
@is_api(required_keys=['id', 'password'], input_type='json')
def login(data):
    if not account.login(**data):
        return {"registered": "Failed"}, 403
    else:
        return {"registered": "True"}, 200


@account_blueprint.route('/user_data', methods=['GET'])
@is_api(required_keys=['id'])
def get_userdata(data):
    uuid = account.get_uuid(data['id'])
    data = account.get_user_data(uuid)

    if data is None:
        return {'error': 'exception_occurred'}, 500
    else:
        return data
