from flask import Blueprint
from . import is_api
from methods import article
from constants import messages
from methods.account import get_uuid

article_blueprint = Blueprint('Article', __name__)


@article_blueprint.route('/get_articles', methods=['GET'])
@is_api(required_keys=['address', 'id'],
        acceptable_keys=['article_type', 'article_category', 'start_idx', 'end_idx'])
def get_articles(data):
    if 'article_type' not in data:
        data['article_type'] = 'None'
    if 'article_category' not in data:
        data['article_category'] = 'None'
    if 'start_idx' not in data:
        data['start_idx'] = 0
    if 'end_idx' not in data:
        data['end_idx'] = 20

    data['user_uuid'] = get_uuid(data['id'])
    del data['id']

    status, article_list = article.get_articles(**data)

    if not status:
        return {'error': messages.no_exists.format('article')}
    else:
        return article_list


@article_blueprint.route('/get_article/<int:article_id>', methods=['GET'])
@is_api(acceptable_keys=[])
def get_article(data, article_id: int):
    status, article_dict = article.get_article(article_id)

    if not status:
        return {'error': messages.no_exists.format('article')}, 404
    else:
        return article_dict


'''
아래 api들은 제대로 구현하지 않았으며 버그가 있을 가능성이 높음

@article_blueprint.route('/search', methods=['GET'])
@is_api(required_keys=['type', 'keyword'], acceptable_keys=['start_idx', 'end_idx'])
def get_articles_by_search(data):
    if 'start_idx' not in data:
        data['start_idx'] = 0
    if 'end_idx' not in data:
        data['end_idx'] = 20

    if not isinstance(data['start_idx'], int) or not isinstance(data['end_idx'], int):
        return {'error': 'idx_must_be_integer'}, 400

    return article.get_articles_with_search(**data)


@article_blueprint.route('/delete_article/<int:article_id>', methods=['DELETE'])
@is_api(acceptable_keys=[])
def delete_article(data, article_id: int):
    status, message, status_code = article.delete_article(article_id)

    if not status:
        return {'error': message}, status_code

    else:
        return {'deleted': article_id}
    
'''


@article_blueprint.route('/create_article', methods=['POST'])
@is_api(required_keys=['title', 'submitter', 'address', 'cost', 'remain_time',
                       'max_num', 'article_type', 'article_category'],
        acceptable_keys=['image', 'content'], input_type='json')
def create_article(data):
    data['submitter'] = get_uuid(data['submitter'])
    status, message, status_code = article.create_article(**data)

    if not status:
        return {'message': message}, status_code

    else:
        return {'message': message}
