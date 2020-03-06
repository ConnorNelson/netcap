#!/usr/bin/env python3
import pathlib
import ast
import json

from flask import Flask, render_template, request

app = Flask(__name__)
persist_dir = pathlib.Path('/persist')
conversation_dir = (persist_dir / 'conversations').resolve()

@app.route('/')
def index():
    filter_ = request.args.get('filter')
    conversations = list()
    for path in conversation_dir.iterdir():
        if filter_:
            with open(path) as f:
                if not filter_ in f.read():
                    continue
        time, port1, port2 = path.name.split('-')
        conversations.append({'time': time,
                              'port1': port1,
                              'port2': port2})
    return render_template('index.html', conversations=conversations)

@app.route('/conversation/<conversation>')
def conversation(conversation):
    with open(conversation_dir / conversation) as f:
        data = [(a, b, c.decode('latin')) for a, b, c in  ast.literal_eval(f.read())]
    return {'conversation': data}


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4242)
