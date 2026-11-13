import os
import time
import pyautogui
from pydantic import BaseModel
from google import genai

# Safety: Slam your mouse cursor into any corner of the screen to stop the script
pyautogui.FAILSAFE = True

# Initialize the Gemini client (reads GEMINI_API_KEY from your environment)
client = genai.Client()

# Define the exact structure the AI must reply with
class NextAction(BaseModel):
    thought: str
    action: str          # "click", "type", "press", "wait", or "done"
    x: int = 0           # Screen X coordinate for clicking
    y: int = 0           # Screen Y coordinate for clicking
    text: str = ""       # Text to type or key name to press (e.g., "enter", "win")

GOAL = "Open Notepad and write a short paragraph about automation."
screen_width, screen_height = pyautogui.size()

print(f"Starting autonomous agent. Screen size: {screen_width}x{screen_height}")
print("Move mouse to any screen corner to abort immediately.\n")

while True:
    # 1. Capture current screen state
    screenshot = pyautogui.screenshot()
    
    # 2. Ask the AI to decide the next human-like step
    prompt = f"""
    You are controlling a Windows PC. Screen resolution is {screen_width}x{screen_height}.
    Your overall goal is: "{GOAL}".
    Look at the current screenshot and decide the single next action to take.
    - Use 'click' with x and y coordinates to click icons, search bars, or buttons.
    - Use 'type' with text to type characters.
    - Use 'press' with text (like 'enter', 'win', 'tab') for single keys.
    - Use 'wait' if something is still loading.
    - Use 'done' once the goal is completely finished.
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[screenshot, prompt],
        config={
            "response_mime_type": "application/json",
            "response_schema": NextAction,
        },
    )
    
    
    step = NextAction.model_validate_json(response.text)
    print(f"AI Thought: {step.thought}")
    print(f"Executing: {step.action} ({step.x}, {step.y}) '{step.text}'\n")
    
    # 3. Perform the action like a human user
    if step.action == "click":
        pyautogui.moveTo(step.x, step.y, duration=0.4)
        pyautogui.click()
    elif step.action == "type":
        pyautogui.write(step.text, interval=0.05)
    elif step.action == "press":
        pyautogui.press(step.text)
    elif step.action == "wait":
        time.sleep(2)
    elif step.action == "done":
        print("Goal completed!")
        break
        
    # Pause briefly so Windows can react before the next screenshot
    time.sleep(1.5)
