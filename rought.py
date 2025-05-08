from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage")  # Default to English if not provided

HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace language placeholder in HTML
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

with open(r"Data/Voice.html", "w") as f:
    f.write(HtmlCode)

# Get file path
current_dir = os.getcwd()
Link = f"{current_dir}/Data/Voice.html"

# Set up Chrome options
Chrome_options = Options()
Chrome_options.add_argument("--ignore-certificate-errors")
Chrome_options.add_argument("--disable-gpu")
Chrome_options.add_argument("--disable-software-rasterizer")
Chrome_options.add_argument("--no-sandbox")
Chrome_options.add_argument("--disable-dev-shm-usage")
Chrome_options.add_argument("--start-maximized")

# Set up user-agent
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.118 Safari/537.36"
Chrome_options.add_argument(f"user-agent={user_agent}")

# Set up WebDriver with correct ChromeDriver version
service = Service(ChromeDriverManager().install())  # Automatically fetches the compatible version

driver = webdriver.Chrome(service=service, options=Chrome_options)

# Ensure TempDirPath exists
TempDirPath = rf"{current_dir}/Frontend/Files"

def SetAssistantStatus(Status):
    with open(rf"{TempDirPath}/Status.data", "w", encoding="utf-8") as file:
        file.write(Status)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's", "can you"]

    if any(new_query.startswith(word) for word in question_words):
        if new_query[-1] not in ['.', '?', '!']:
            new_query += "?"
    else:
        if new_query[-1] not in ['.', '?', '!']:
            new_query += "."

    return new_query.capitalize()

def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

def SpeechRecognition():
    driver.get(Link)
    driver.find_element(By.ID, "start").click()

    while True:
        try:
            Text = driver.find_element(By.ID, "output").text

            if Text:
                driver.find_element(By.ID, "stop").click()

                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))
        except Exception:
            pass

if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        print(Text)
