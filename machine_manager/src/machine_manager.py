from flask import Flask, jsonify
from docker_wrapper import DockerWrapper, Image

app = Flask(__name__)
docker = DockerWrapper()

containers = []

# FIXME: These are only temporary versions 
versions = {
    'python': '1.0',
    'java': '2.0',
}

@app.route('/create/<lang>')
def create(lang):
    image = Image('linter', versions[lang], env={'LANGUAGE': lang})
    container = docker.create(image)
    containers.append(container)

    response = {
        'status': 'ok',
        'id': f'127.0.0.1:{container.host_port}',
    }

    return jsonify(response)


@app.route('/delete/<ip_port>')
def delete(ip_port):
    _, port = ip_port.split(':')
    port = int(port)

    for container in containers:
        if container.host_port == port:
            docker.remove(container)
            containers.remove(container)
            break

    response = {
        'status': 'ok',
    }

    return jsonify(response)


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
    return f'/status'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)