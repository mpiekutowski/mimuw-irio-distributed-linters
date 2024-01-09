from flask import Flask, jsonify, Response
from docker_wrapper import DockerWrapper, Image, DockerError
import json
import argparse
import requests

app = Flask(__name__)
docker = DockerWrapper()

containersInfo = [] # dict(container, is_ready, request_count, is_healthy)
# TODO: update is_ready checking if created linter is up

# FIXME: These are only temporary versions 
versions = {
    'python': '1.0',
    'java': '2.0',
}

# FIXME: These endpoints should probably be POST
@app.route('/create/<lang>')
def create(lang):
    image = Image('linter', versions[lang], env={'LANGUAGE': lang})

    try:
        container = docker.create(image)
    except DockerError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    containersInfo.append(dict(container=container, is_ready=False, request_count=0, is_healthy=True))

    response = {
        'status': 'ok',
        'id': f'127.0.0.1:{container.host_port}',
    }

    return jsonify(response), 200


@app.route('/delete/<ip_port>')
def delete(ip_port):
    _, port = ip_port.split(':')
    port = int(port)

    found = False
    error_message = None

    # FIXME: What should happen if docker fails? Remove from containers list?
    for containerInfo in containersInfo:
        if containerInfo["container"].host_port == port:
            found = True
            try:
                docker.remove(containerInfo["container"], timeout=app.config['STOP_TIMEOUT'])
            except DockerError as e:
                error_message = str(e)
            finally:
                containersInfo.remove(containerInfo)
                break

    if not found:
        return jsonify({"status": "error", "message": "Container not found"}), 500

    if error_message is not None:
        return jsonify({"status": "error", "message": error_message}), 500

    return jsonify({"status": "ok"}), 200


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
    lintersArray = []
    for containerInfo in containersInfo:
        linterDict = {}
        linterDict[containerInfo["container"].id] = dict(
            version=containerInfo["container"].version,
            lang=containerInfo["container"].lang,
            request_count=containerInfo["request_count"],
            is_healthy=containerInfo["is_healthy"]
        )
        lintersArray.append(linterDict)

    return jsonify(linters=lintersArray), 200

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