import jinja2.ext
import threading
import socket
import os
from flask import Flask, render_template, jsonify, request
from modules import screenbloom_functions as sb

# app = Flask(__name__)  # Development
app = Flask(__name__, static_url_path='', static_folder='', template_folder='')  # Production
app.secret_key = os.urandom(24)


@app.route('/')
def index():
    global startup_thread
    if startup_thread.is_alive():
        startup_thread.join()

    data = sb.get_index_data()
    return render_template('/home.html',
                           update=data['update'],
                           min_bri=data['min_bri'],
                           default=data['default'],
                           default_color=data['default_color'],
                           lights=data['lights'],
                           lights_number=data['lights_number'],
                           icon_size=data['icon_size'],
                           username=data['username'],
                           party_mode=data['party_mode'],
                           title='Home')


@app.route('/start')
def start():
    data = sb.start_screenbloom()
    return jsonify(data)


@app.route('/stop')
def stop():
    data = sb.stop_screenbloom()
    return jsonify(data)


@app.route('/new-user')
def new_user():
    return render_template('/new_user.html',
                           title='New User')


@app.route('/manual')
def manual():
    return render_template('/new_user_manual.html',
                           title='Manual IP')


@app.route('/register', methods=['GET', 'POST'])
def register():
    username = request.args.get('username', 0, type=str)
    hue_ip = request.args.get('hue_ip', 0, type=str)
    data = sb.register_logic(username, hue_ip, local_host)
    return jsonify(data)


@app.route('/update-min-bri', methods=['POST'])
def update_min_bri():
    if request.method == 'POST':
        min_bri = request.json

        sb.write_config('Light Settings', 'min_bri', min_bri)
        sb.restart_check()

        data = {
            'message': 'Minimum Brightness Updated!',
            'value': min_bri
        }
        return jsonify(data)


@app.route('/update-update-speed', methods=['POST'])
def update_update_speed():
    if request.method == 'POST':
        update_speed = float(request.json)

        sb.write_config('Light Settings', 'update', update_speed)
        sb.restart_check()

        data = {
            'message': 'Update Speed Updated!',
            'value': update_speed
        }
        return jsonify(data)


@app.route('/update-default-color', methods=['POST'])
def update_default_color():
    if request.method == 'POST':
        color = request.json

        helper = sb.rgb_cie.ColorHelper()
        default = helper.hexToRGB(color)
        default = '%d,%d,%d' % (default[0], default[1], default[2])

        sb.write_config('Light Settings', 'default', default)
        sb.restart_check()

        data = {
            'message': 'Default Color Updated!',
            'value': default
        }
        return jsonify(data)


@app.route('/update-party-mode', methods=['POST'])
def update_party_mode():
    if request.method == 'POST':
        print 'Update Party Mode Route Hit'
        party_mode_state = request.json
        wording = 'enabled' if int(party_mode_state) else 'disabled'

        sb.write_config('Party Mode', 'running', party_mode_state)
        sb.restart_check()

        data = {
            'message': 'Party mode %s!' % wording
        }
        return jsonify(data)


@app.route('/update-bulbs', methods=['POST'])
def update_bulbs():
    if request.method == 'POST':
        bulbs = request.json

        sb.write_config('Light Settings', 'active', bulbs)
        sb.restart_check()

        data = {
            'message': 'Bulbs updated!',
        }
        return jsonify(data)


@app.route('/on-off')
def on_off():
    state = request.args.get('state', 0, type=str)
    sb.lights_on_off(state)
    data = {
        'message': 'Turned lights %s' % state
    }
    return jsonify(data)

if __name__ == '__main__':
    local_host = socket.gethostbyname(socket.gethostname())
    startup_thread = sb.StartupThread(local_host)
    startup_thread.start()
    app.run(debug=True, host=local_host, use_reloader=False)
