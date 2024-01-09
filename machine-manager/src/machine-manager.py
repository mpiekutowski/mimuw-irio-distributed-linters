from flask import Flask

app = Flask(__name__)

@app.route('/create/<lang>')
def create(lang):
    return f'/create/{lang}'


@app.route('/delete/<ip_port>')
def delete(ip_port):
    return f'/delete/{ip_port}'


@app.route('/init-update')
def init_update():
    return '/init-update'


@app.route('/update/<lang>')
def update(lang):
    return f'/update/{lang}'


@app.route('/rollback/<lang>')
def rollback(lang):
    return f'/rollback/{lang}'


@app.route('/status')
def status():
    return '/status'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)