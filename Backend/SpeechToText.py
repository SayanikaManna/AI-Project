from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
import time

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en-US")  # Default to English if not provided

# Modified HTML code for speech recognition
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
    <meta charset="UTF-8">
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="stop" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition = null;
        let silenceTimer = null;
        
        function startRecognition() {
            try {
                if (!window.SpeechRecognition && !window.webkitSpeechRecognition) {
                    output.textContent = "ERROR: Speech recognition not supported";
                    return;
                }
                
                recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                recognition.lang = '';  // Will be replaced by Python
                recognition.continuous = true;
                recognition.interimResults = true;
                
                recognition.onresult = function(event) {
                    // Reset silence timer when we get speech
                    clearTimeout(silenceTimer);
                    
                    const transcript = event.results[event.results.length - 1][0].transcript;
                    output.textContent = transcript;
                    
                    // Set a timer to detect silence (2 seconds)
                    silenceTimer = setTimeout(() => {
                        if (recognition) {
                            recognition.stop();
                        }
                    }, 2000);
                };

                recognition.onend = function() {
                    console.log("Recognition ended");
                };
                
                recognition.onerror = function(event) {
                    console.error("Speech recognition error:", event.error);
                };
                
                recognition.start();
            } catch (e) {
                output.textContent = "ERROR: " + e.message;
            }
        }

        function stopRecognition() {
            clearTimeout(silenceTimer);
            if (recognition) {
                try {
                    recognition.stop();
                } catch (e) {
                    console.error("Error stopping recognition:", e);
                }
                recognition = null;
            }
        }
        
        // Auto-start when page loads
        window.addEventListener('load', function() {
            setTimeout(startRecognition, 500);
        });
    </script>
</body>
</html>'''

# Replace language placeholder in HTML
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Ensure Data directory exists
os.makedirs("Data", exist_ok=True)

with open(r"Data/Voice.html", "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Get file path
current_dir = os.getcwd()
Link = f"file:///{current_dir}/Data/Voice.html".replace("\\", "/")

# Set up Chrome options
def get_chrome_options():
    Chrome_options = Options()
    
    # Required for headless operation
    Chrome_options.add_argument("--headless=new")  # Modern headless mode
    Chrome_options.add_argument("--disable-gpu")
    Chrome_options.add_argument("--no-sandbox")
    Chrome_options.add_argument("--disable-dev-shm-usage")
    Chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Auto-accept microphone permission
    
    # Needed for better stability
    Chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    Chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # Set up user-agent
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.118 Safari/537.36"
    Chrome_options.add_argument(f"user-agent={user_agent}")
    
    return Chrome_options

# Ensure TempDirPath exists
TempDirPath = rf"{current_dir}/Frontend/Files"
os.makedirs(TempDirPath, exist_ok=True)

def SetAssistantStatus(Status):
    with open(rf"{TempDirPath}/Status.data", "w", encoding="utf-8") as file:
        file.write(Status)

def QueryModifier(Query):
    if not Query or Query.strip() == "":
        return "I didn't hear anything. Could you please try again?"
    
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
    try:
        english_translation = mt.translate(Text, "en", "auto")
        return english_translation.capitalize()
    except Exception as e:
        print(f"Translation error: {e}")
        return Text.capitalize()  # Return original text if translation fails

# This is the function name that main.py is looking for
def SpeechRecognition():
    try:
        # Set up WebDriver with correct ChromeDriver version
        options = get_chrome_options()
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"Error initializing Chrome driver: {e}")
            # Fallback to local chromedriver
            driver_path = os.path.join(current_dir, "chromedriver")
            if os.path.exists(driver_path):
                service = Service(driver_path)
                driver = webdriver.Chrome(service=service, options=options)
            else:
                raise Exception("ChromeDriver not found and could not be installed automatically")
        
        # Load the HTML file
        driver.get(Link)
        
        # Wait for page to fully load (no need to click start since it auto-starts)
        time.sleep(1)
        
        SetAssistantStatus("Listening...")
        
        # Add a timeout mechanism
        max_wait_time = 15  # seconds
        start_time = time.time()
        last_text = ""
        no_change_start = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                current_text = driver.find_element(By.ID, "output").text.strip()
                
                # If we have text and it hasn't changed for 3 seconds, consider it complete
                if current_text:
                    if current_text != last_text:
                        last_text = current_text
                        no_change_start = time.time()
                    elif time.time() - no_change_start >= 3:
                        # Text has been stable for 3 seconds, process it
                        driver.quit()
                        
                        if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                            return QueryModifier(current_text)
                        else:
                            SetAssistantStatus("Translating...")
                            return QueryModifier(UniversalTranslator(current_text))
            except Exception as e:
                print(f"Error in recognition loop: {e}")
            
            time.sleep(0.3)  # Small delay to prevent CPU usage
        
        # After timeout, check if we have any text
        try:
            final_text = driver.find_element(By.ID, "output").text.strip()
            driver.quit()
            
            if final_text:
                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(final_text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(final_text))
            else:
                return "I didn't hear anything. Could you please try again?"
        except:
            driver.quit()
            return "I didn't hear anything. Could you please try again?"
            
    except Exception as e:
        print(f"Speech recognition error: {e}")
        SetAssistantStatus("Speech recognition error")
        try:
            driver.quit()
        except:
            pass
        return "Sorry, there was an error with speech recognition. Please try again."

# Add the continuous recognition function for direct use
def ContinuousSpeechRecognition():
    print("Continuous speech recognition started. Press Ctrl+C to stop.")
    try:
        while True:
            result = SpeechRecognition()
            print(f"Recognized: {result}")
    except KeyboardInterrupt:
        print("\nStopping continuous speech recognition...")

# When run directly, just perform one recognition
if __name__ == "__main__":
    print(f"Speech recognition started with language: {InputLanguage}")
    if input("Do you want continuous recognition? (y/n): ").lower() == 'y':
        ContinuousSpeechRecognition()
    else:
        Text = SpeechRecognition()
        print(f"Recognized: {Text}")