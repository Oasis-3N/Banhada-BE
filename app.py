from flask import Flask
import endpoints
from config import FLASK_SECRET

app = Flask(__name__)
app.register_blueprint(endpoints.article_blueprint, url_prefix='/article')
app.register_blueprint(endpoints.account_blueprint, url_prefix='/account')
app.register_blueprint(endpoints.message_blueprint, url_prefix='/message')
app.register_blueprint(endpoints.fork_blueprint, url_prefix='/fork')

app.secret_key = FLASK_SECRET

if __name__ == '__main__':
    app.run('0.0.0.0', port=2500)
