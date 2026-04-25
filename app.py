from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from jarvis import ScreenshotManager, InputManager, AICommandProcessor
import json
import os
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-jarvis-secret')
app.config['ACCESS_TOKEN'] = os.environ.get('JARVIS_TOKEN', 'admin') # Default token for simplicity
socketio = SocketIO(app, cors_allowed_origins="*")

sm = ScreenshotManager()
im = InputManager()
# Mock mode is enabled if specifically requested
mock_mode = os.environ.get('JARVIS_MOCK', 'true').lower() == 'true'
ollama_host = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
ai = AICommandProcessor(host=ollama_host, mock=mock_mode)

@app.route('/')
def index():
    token = request.args.get('token')
    if token != app.config['ACCESS_TOKEN']:
        return "Unauthorized. Please provide a valid token in the URL.", 401
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit_screenshot()

@socketio.on('command')
def handle_command(data):
    command = data.get('command')
    print(f"Received command: {command}")

    # Capture current screenshot for AI context
    screenshot_b64 = sm.capture_base64()

    # Process with AI
    ai_resp_json = ai.process_command(command, screenshot_base64=screenshot_b64)
    try:
        ai_resp = json.loads(ai_resp_json)
        actions = ai_resp.get('actions', [])

        for action in actions:
            execute_action(action)

        emit('ai_response', {'message': ai_resp.get('message', 'Actions executed.'), 'actions': actions})
    except Exception as e:
        emit('error', {'message': f"Error parsing AI response: {str(e)}"})

    # Send updated screenshot
    emit_screenshot()

@socketio.on('mouse_click')
def handle_mouse_click(data):
    x = data.get('x')
    y = data.get('y')
    button = data.get('button', 'left')
    im.click(x, y, button=button)
    emit_screenshot()

@socketio.on('key_press')
def handle_key_press(data):
    key = data.get('key')
    im.press_key(key)
    emit_screenshot()

def execute_action(action):
    action_type = action.get('type')
    if action_type == 'click':
        im.click(action.get('x'), action.get('y'))
    elif action_type == 'move':
        im.move_mouse(action.get('x'), action.get('y'))
    elif action_type == 'type':
        im.type_text(action.get('text'))
    elif action_type == 'press':
        im.press_key(action.get('key'))
    elif action_type == 'wait':
        time.sleep(float(action.get('seconds', 1)))

def emit_screenshot():
    screenshot = sm.capture_base64()
    if screenshot:
        socketio.emit('screenshot', {'image': screenshot})

def screenshot_loop():
    while True:
        emit_screenshot()
        time.sleep(2) # Refresh every 2 seconds

if __name__ == '__main__':
    # Threading the screenshot loop might be too aggressive for simple remote control,
    # but let's keep it in mind. For now, we refresh on actions.
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
