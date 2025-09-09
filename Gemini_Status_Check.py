# Check Gemini Code Assist status
import os

def check_gemini_status():
    print("Checking Gemini extension...")
    installed = os.system("code --list-extensions | findstr google.gemini")
    if installed != 0:
        print("Gemini not found. Please install via VS Code Marketplace.")
        return
    print("Gemini extension found.")
    print("To verify it's signed in, run: Ctrl + Shift + P → Gemini: Sign In")

check_gemini_status()