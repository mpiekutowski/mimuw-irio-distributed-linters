from flask import Flask, jsonify, Response, request
from docker_wrapper import DockerWrapper, Image, DockerError, Container
import json
import argparse
from typing import List
from dataclasses import dataclass
from image_store import ImageStore

app = Flask(__name__)
docker = DockerWrapper()

@dataclass
class Linter:
    lang: str
    version: str
    host_port: int
    container: Container 

linters: List[Linter] = []

# Assign None to make it global
image_store = None

health_check_info = {} # dict(container_id, (request_count, is_healthy))
# FIXME: temporary structure, will be changed to be shared with health check worker
# TODO: update checking if created linter is up

# FIXME: These are only temporary versions 
versions = {
    'python': '1.0',
    'java': '2.0',
}       

@app.route('/create', methods=['POST'])
def create():
    request_data = request.get_json()
    lang = request_data.get('lang')

    if not lang:
        return jsonify({"status": "error", "message": "Missing 'lang' parameter"}), 400

    image = image_store.get_image(lang, versions[lang])

    if image is None:
        return jsonify({"status": "error", "message": "Invalid 'lang' parameter"}), 400

    try:
        container = docker.create(image)
    except DockerError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    linters.append(Linter(lang=lang, version=versions[lang], host_port=container.host_port, container=container))
    health_check_info[container.id] = dict(request_count=0, is_healthy=True)

    response = {
        'status': 'ok',
        'id': f'127.0.0.1:{container.host_port}',
    }

    return jsonify(response), 200


@app.route('/delete', methods=['POST'])
def delete():
    request_data = request.get_json()
    ip_port = request_data.get('ip_port')

    if not ip_port:
        return jsonify({"status": "error", "message": "Missing 'ip_port' parameter"}), 400

    _, port = ip_port.split(':')
    port = int(port)

    found = False
    error_message = None

    # FIXME: What should happen if docker fails? Remove from containers list?
    for linter in linters:
        if linter.host_port == port:
            found = True
            try:
                docker.remove(linter.container, timeout=app.config['STOP_TIMEOUT'])
            except DockerError as e:
                error_message = str(e)
            finally:
                linters.remove(linter)
                break

    if not found:
        return jsonify({"status": "error", "message": "Container not found"}), 500

    if error_message is not None:
        return jsonify({"status": "error", "message": error_message}), 500

    return jsonify({"status": "ok"}), 200


@app.route('/init-update', methods=['POST'])
def init_update():
    return '/init-update'


@app.route('/update', methods=['POST'])
def update():
    request_data = request.get_json()
    lang = request_data.get('lang')

    if not lang:
        return jsonify({"status": "error", "message": "Missing 'lang' parameter"}), 400

    return f'/update/{lang}'


@app.route('/rollback', methods=['POST'])
def rollback():
    request_data = request.get_json()
    lang = request_data.get('lang')

    if not lang:
        return jsonify({"status": "error", "message": "Missing 'lang' parameter"}), 400

    return f'/rollback/{lang}'


@app.route('/status')
def status():
    lintersArray = []
    for linter in linters:
        health_check_result = health_check_info.get(linter.container.id)
        linterDict = {}
        linterDict[linter.container.id] = dict(
            version=linter.version,
            lang=linter.lang,
            request_count=health_check_result["request_count"],
            is_healthy=health_check_result["is_healthy"]
        )
        lintersArray.append(linterDict)

    return jsonify(linters=lintersArray), 200

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config_path', type=str, help='Path to config file')
    parser.add_argument('linters_path', type=str, help='Path to file with linter definitions')
    args = parser.parse_args()

    if args.config_path:
        app.config.from_file(args.config_path, load=json.load)
    else:
        print('No config file provided, exiting')
        exit(1)

    if args.linters_path:
        image_store = ImageStore.from_json_file(args.linters_path)
    else:
        print('No linters file provided, exiting')
        exit(1)

    app.run(host='0.0.0.0', port=5000)