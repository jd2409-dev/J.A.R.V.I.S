import os
import base64
from io import BytesIO
from PIL import Image
import mss
import pyautogui
import ollama
import json

class ScreenshotManager:
    def __init__(self):
        self.sct = mss.mss()

    def capture(self):
        try:
            # mss is cross-platform and handles multiple monitors
            monitor = self.sct.monitors[1] # Primary monitor
            sct_img = self.sct.grab(monitor)
            return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        except Exception as e:
            print(f"Screenshot capture failed: {e}")
            return None

    def capture_base64(self):
        img = self.capture()
        if img:
            buffered = BytesIO()
            img.save(buffered, format="JPEG", quality=70)
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
        return None

class InputManager:
    def __init__(self):
        # PyAutoGUI handles its own display connection
        pass

    def move_mouse(self, x, y):
        pyautogui.moveTo(x, y)

    def click(self, x=None, y=None, button='left'):
        if x is not None and y is not None:
            pyautogui.click(x, y, button=button)
        else:
            pyautogui.click(button=button)

    def type_text(self, text):
        pyautogui.write(text)

    def press_key(self, key):
        pyautogui.press(key)

class AICommandProcessor:
    def __init__(self, model='phi3', mock=False):
        self.model = model
        self.mock = mock
        if not mock:
            self.client = ollama.Client()
        else:
            self.client = None

    def process_command(self, command, screenshot_base64=None):
        if self.mock:
            # Simple heuristic for mock mode
            command = command.lower()
            if "click" in command:
                return json.dumps({"actions": [{"type": "click", "x": 500, "y": 500}]})
            elif "type" in command:
                return json.dumps({"actions": [{"type": "type", "text": "Hello from J.A.R.V.I.S."}]})
            else:
                return json.dumps({"actions": [], "message": f"I heard: {command}. How can I help?"})

        system_prompt = """You are J.A.R.V.I.S., a highly advanced AI assistant.
        You control a computer via mouse and keyboard.
        Given a user command, you should output ONLY the necessary actions in JSON format.
        Actions can be: 'click', 'move', 'type', 'press'.
        Example output: {"actions": [{"type": "click", "x": 100, "y": 200}, {"type": "type", "text": "hello"}]}
        """

        try:
            response = self.client.generate(model=self.model, prompt=f"{system_prompt}\nUser command: {command}")
            return response['response']
        except Exception as e:
            return json.dumps({"error": str(e), "actions": []})

if __name__ == "__main__":
    sm = ScreenshotManager()
    img = sm.capture()
    if img:
        img.save("jarvis_test_capture.png")
        print("Capture successful")
    else:
        print("Capture failed")
