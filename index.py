import datetime
import secrets
import hashlib
from flask import json, Flask, request, abort, url_for


def rand():
    return secrets.token_hex(32)


def sha256(data):
    h = hashlib.sha256()
    if type(data) == str:
        h.update(data.encode('utf-8'))
    else:
        h.update(data)
    return h.hexdigest()


def fag(author):
    result = sha256(author or rand())
    app.logger.info('encoding author %s to %s', author, result)
    return result


def invalid(post):
    if post is None:
        app.logger.info('invalid json')
        return True

    if post.get('content') is None:
        app.logger.info('missing "content"')
        return True

    if type(post.get('content')) != str:
        app.logger.info('"content" has wrong type')
        return True

    if type(post.get('author')) not in [str, type(None)]:
        app.logger.info('"author" has wrong type')
        return True

    return False


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        return super().default(obj)


app = Flask(__name__)
app.json_encoder = JSONEncoder


posts = {}


@app.route('/api/posts/')
def get_posts():
    return json.jsonify(posts)


@app.route('/api/posts/', methods=['POST'])
def new_post():
    post_id = rand()
    data = request.get_json()
    if invalid(data):
        abort(400)

    posts[post_id] = {
        'content': data['content'],
        'date': datetime.datetime.now(),
        'author': fag(data.get('author')),
        'replies': [],
    }
    return json.jsonify(
        post_id=post_id,
        href=url_for('get_post', post_id=post_id))


@app.route('/api/posts/<post_id>')
def get_post(post_id):
    return json.jsonify(posts[post_id])


@app.route('/api/posts/<post_id>', methods=['POST'])
def post_reply(post_id):
    data = request.get_json()
    if invalid(data):
        abort(400)

    reply = {
        'content': data['content'],
        'author': fag(data.get('author')),
        'date': datetime.datetime.now()
    }
    posts[post_id]['replies'].append(reply)
    index = posts[post_id]['replies'].index(reply)
    return json.jsonify(
        post_id=post_id,
        href=url_for('get_post', post_id=post_id) + f"#{index}")
