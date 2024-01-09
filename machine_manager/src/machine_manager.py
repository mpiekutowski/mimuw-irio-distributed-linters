from flask import Flask, jsonify, Response
from docker_wrapper import DockerWrapper, Image
import json
import argparse

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

    try:
        container = docker.create(image)
    except DockerError:
        return jsonify({"status": "error"}), 500

    containers.append(container)

    response = {
        'status': 'ok',
        'id': f'127.0.0.1:{container.host_port}',
    }

    return jsonify(response), 200


@app.route('/delete/<ip_port>')
def delete(ip_port):
    _, port = ip_port.split(':')
    port = int(port)

    success = False
    error_message = None

    for container in containers:
        if container.host_port == port:
            try:
                docker.remove(container, timeout=app.config['STOP_TIMEOUT'])
                success = True
            except DockerError:
                pass
            finally:
                containers.remove(container)
                break

    # FIXME: Not sure if just the error code would be enough
    if success:
        return jsonify({"status": "ok"}), 200

    return jsonify({"status": "error"}), 500


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
    parser = argparse.ArgumentParser()
    parser.add_argument('config_path', type=str, help='Path to config file')
    args = parser.parse_args()

    if args.config_path:
        app.config.from_file(args.config_path, load=json.load)
    else:
        print('No config file provided, exiting')
        exit(1)

    app.run(host='0.0.0.0', port=5000)