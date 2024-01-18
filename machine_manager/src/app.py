from flask import Flask, jsonify, request
from docker_wrapper import DockerError
import json
import argparse
import sys
import signal
from typing import Optional
from image_store import ImageStore

from machine_manager import MachineManager, Config
from health_check import HealthCheck, finish_health_check

app = Flask(__name__)

machine_manager: Optional[MachineManager] = None

@app.route('/create', methods=['POST'])
def create():
    request_data = request.get_json()
    lang = request_data.get('lang')

    if not lang:
        return jsonify({"status": "error", "message": "Missing 'lang' parameter"}), 400

    try:
        linter = machine_manager.create_linter(lang)
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    response = {
        'status': 'ok',
        'ip': linter.container.address,
    }

    return jsonify(response), 200


@app.route('/delete', methods=['POST'])
def delete():
    request_data = request.get_json()
    address = request_data.get('ip')

    if not address:
        return jsonify({"status": "error", "message": "Missing 'ip' parameter"}), 400

    try:
        machine_manager.delete_linter(address)
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"status": "error", "message": str(e)}), 500


    return jsonify({"status": "ok"}), 200


@app.route('/init-update', methods=['POST'])
def init_update():
    request_data = request.get_json()
    lang = request_data.get('lang')

    if not lang:
        return jsonify({"status": "error", "message": "Missing 'lang' parameter"}), 400
    
    version = request_data.get('version')

    if not version:
        return jsonify({"status": "error", "message": "Missing 'version' parameter"}), 400
    
    try:
        machine_manager.init_update(lang, version)
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    return '/init-update'


@app.route('/update', methods=['POST'])
def update():
    request_data = request.get_json()
    lang = request_data.get('lang')

    if not lang:
        return jsonify({"status": "error", "message": "Missing 'lang' parameter"}), 400

    try:
        machine_manager.update(lang)
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "ok"}), 200


@app.route('/rollback', methods=['POST'])
def rollback():
    request_data = request.get_json()
    lang = request_data.get('lang')

    if not lang:
        return jsonify({"status": "error", "message": "Missing 'lang' parameter"}), 400

    try:
        machine_manager.rollback(lang)
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
    return jsonify({"status": "ok"}), 200


@app.route('/status')
def status():
    return jsonify(linters=machine_manager.status()), 200


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

    machine_manager = MachineManager(
        image_store=ImageStore.from_json_file(args.linters_path), 
        update_steps=app.config['UPDATE_STEPS'],
        config=Config(timeout=app.config['STOP_TIMEOUT']) # Yes, this is ugly, will fix later
        )
    
    health_check_thread = HealthCheck(args=(machine_manager.health_check_info, machine_manager.health_check_mutex))
    health_check_thread.start()

    def handler(signal, frame):
        finish_health_check(health_check_thread)
        sys.exit(0)

    signal.signal(signal.SIGINT, handler)

    app.run(host='0.0.0.0', port=5000)