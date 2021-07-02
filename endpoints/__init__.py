from functools import wraps
from flask import request, jsonify, Response


def is_api(required_keys=None, acceptable_keys=None, input_type: str = 'query_string'):
    if required_keys is None:
        required_keys = []
    if acceptable_keys is None:
        acceptable_keys = []

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if input_type == 'query_string':
                data = request.args
            elif input_type == 'json':
                request.on_json_loading_failed = lambda: jsonify({'error': 'JSON_parsing_failed'}), 400
                data = request.get_json()
                if not isinstance(data, dict):
                    print("dictionary_required")
                    return jsonify({'error': 'dictionary_required'}), 400
            else:
                print('server_side_error_contact_administrator')
                return jsonify({'error': 'server_side_error_contact_administrator'}), 400

            data = {str(k).lower(): v for k, v in data.items() if k in required_keys or k in acceptable_keys}
            if not set(required_keys).issubset(set(data.keys())):
                print('no_required_args')
                return jsonify({'error': 'no_required_args'}), 400
            else:
                return return_api(func, data, *args, **kwargs)

        return wrapper

    return decorator


def return_as_api(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        return return_api(function, *args, **kwargs)

    return decorator


def return_api(func, *args, **kwargs):
    ret_data: Response = func(*args, **kwargs)
    if isinstance(ret_data, tuple):
        return jsonify(ret_data[0]), ret_data[1]
    else:
        return jsonify(ret_data)


from .account import account_blueprint
from .article import article_blueprint
from .message import message_blueprint
from .fork import fork_blueprint

__all__ = ['is_api', 'return_as_api']
