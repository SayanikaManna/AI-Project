# Import required Libraries
from AppOpener import close, open as appopen  # type: ignore # Import functions to open and close
from webbrowser import open as webopen  # Import web browser functionality.
from pywhatkit import search, playonyt  # type: ignore # Import functions for Google search and YouTube playback.
from dotenv import dotenv_values  # Import dotenv to manage environment variables.
from bs4 import BeautifulSoup  # type: ignore # Import BeautifulSoup for parsing HTML content.
from rich import print  # rich for styled console output.
import webbrowser  # Import webbrowser for opening URLs.
from groq import Groq  # Import Groq for AI chat functionalities.
import requests
import subprocess  # Import subprocess for interacting with the system.
import keyboard  # type: ignore # Import keyboard for keyboard related actions.
import asyncio  # Import asyncio for asynchronous programming.
import os  # Import os for operating system functionalities.

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Set environment variables
GroqAPIKey = env_vars.get("GroqAPIKey")
if not GroqAPIKey:
    raise ValueError("GroqAPIKey not found in .env file")

os.environ["GROQ_API_KEY"] = GroqAPIKey

# Get the Username from environment variables or set a default
Username = env_vars.get("Username", "Assistant")
os.environ["Username"] = Username

# Initialize the Groq client with the API key
client = Groq(api_key=GroqAPIKey)

# Define CSS classes for parsing specific elements in HTML content.
classes = [
    "zCubwf", "hgKEle", "LTKDO SY7ric", "ZOLcM", "gert vk bk FzvwSb YuPhnf", "pclqee",
    "tw-Data-text tw text-small tw-ta",
    "IZ6rdc", "05uR6d LTK00", "vlzY6d", "webanswers-webanswers table_webanswers-table",
    "dDoNo Ikb48b gart", "sXLabe",
    "Lwkfke", "VQF4g", "qw3pe", "kno-rdesc", "SPZz6b"
]

# Define a user agent for making web requests.
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Predefined professional responses for user interactions.
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask.",
]

# List to store chatbot messages.
messages = []

# System message to provide context to the chatbot.
SystemChatBot = [{"role": "system",
                  "content": f"Hello, I am {os.environ['Username']}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]

# Function to perform a Google search.
def GoogleSearch(Topic):
    try:
        search(Topic)  # Use pywhatkit's search function to perform a Google search.
        return True  # Indicate success.
    except Exception as e:
        print(f"Error in GoogleSearch: {e}")
        return False

# Function to generate content using AI and save it to a file.
def Content(Topic):
    # Nested function to open a file in Notepad.
    def OpenNotepad(File):
        try:
            default_text_editor = 'notepad.exe'  # Default text editor.
            subprocess.Popen([default_text_editor, File])  # Open the file in Notepad.
            return True
        except Exception as e:
            print(f"Error opening notepad: {e}")
            return False

    # Nested function to generate content using the AI chatbot.
    def ContentWriterAI(prompt):
        try:
            messages.append({"role": "user", "content": f"{prompt}"})  # Add the user's prompt to messages.
            completion = client.chat.completions.create(
                model="llama3-8b-8192",  # Example of a currently available model
                messages=SystemChatBot + messages,  # Include system instructions and chat history.
                max_tokens=2048,  # Limit the maximum tokens in the response.
                temperature=0.7,  # Adjust response randomness.
                top_p=1,  # Use nucleus sampling for response diversity.
                stream=True,  # Enable streaming response.
                stop=None  # Allow the model to determine stopping conditions.
            )

            Answer = ""  # Initialize an empty string for the response.
            # Process streamed response chunks
            for chunk in completion:
                if chunk.choices[0].delta.content:  # Check for content in the current chunk.
                    Answer += chunk.choices[0].delta.content  # Append the content to the answer.
            Answer = Answer.replace("</s>", "")  # Remove unwanted tokens from the response.
            messages.append({"role": "assistant", "content": Answer})  # Add the AI response to messages.
            return Answer
        except Exception as e:
            print(f"Error generating content: {e}")
            return f"Sorry, I encountered an error: {e}"

    try:
        Topic = str(Topic).replace("content", "").strip()  # Remove "Content" from the topic and trim whitespace
        if not Topic:
            print("Error: Empty topic after removing 'content'")
            return False
            
        ContentByAI = ContentWriterAI(Topic)  # Generate content using AI.

        # Create Data directory if it doesn't exist
        data_dir = "Data"
        os.makedirs(data_dir, exist_ok=True)
        
        # Create a safe filename
        safe_filename = Topic.lower().replace(' ', '')
        file_path = os.path.join(data_dir, f"{safe_filename}.txt")
        
        # Save the generated content to a text file.
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(ContentByAI)  # Write the content to the file.
        
        return OpenNotepad(file_path)  # Open the file in Notepad
    except Exception as e:
        print(f"Error in Content function: {e}")
        return False

# Function to search for a topic on YouTube.
def YouTubeSearch(Topic):
    try:
        Url4Search = f"http://www.youtube.com/results?search_query={Topic}"  # Construct the YouTube search URL.
        webbrowser.open(Url4Search)  # Open the search URL in a web browser.
        return True  # Indicate success.
    except Exception as e:
        print(f"Error in YouTubeSearch: {e}")
        return False

# Function to play a video on YouTube.
def PlayYoutube(query):
    try:
        playonyt(query)  # Use pywhatkit's playonyt function to play the video.
        return True  # Indicate success.
    except Exception as e:
        print(f"Error in PlayYoutube: {e}")
        return False

# Function to open an application or a relevant webpage.
def OpenApp(app, sess=requests.session()):
    app = app.strip()  # Remove leading/trailing whitespace
    if not app:
        print("Error: Empty app name")
        return False
        
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)  # Attempt to open the app.
        return True  # Indicate success.
    except Exception as app_error:
        print(f"Could not open app directly: {app_error}")
        try:
            # Nested function to extract links from HTML content.
            def extract_links(html):
                if html is None:
                    return []
                soup = BeautifulSoup(html, 'html.parser')  # Parse the HTML content.
                links = soup.find_all('a', {'jsname': 'UWckNb'})  # Find relevant links.
                return [link.get('href') for link in links if link.get('href')]  # Return the links.

            # Nested function to perform a Google search and retrieve HTML.
            def search_google(query):
                url = f"https://www.google.com/search?q={query}"  # Construct the Google search URL.
                headers = {"User-Agent": useragent}  # Use the predefined user-agent.
                response = sess.get(url, headers=headers)  # Perform the GET request.
                if response.status_code == 200:
                    return response.text  # Return the HTML content.
                else:
                    print(f"Failed to retrieve search results: {response.status_code}")  # Print an error message.
                    return None

            html = search_google(app)  # Perform the Google search.
            if html:
                links = extract_links(html)
                if links:
                    webopen(links[0])  # Open the first link in a web browser.
                    return True  # Indicate success.
                else:
                    print(f"No links found for '{app}'")
                    return False
            else:
                print(f"Failed to get search results for '{app}'")
                return False
        except Exception as web_error:
            print(f"Error in web search for app: {web_error}")
            return False

# Function to close an application.
def CloseApp(app):
    app = app.strip()  # Remove leading/trailing whitespace
    if not app:
        print("Error: Empty app name")
        return False
        
    if "chrome" in app.lower():
        print("Skipping Chrome close request")
        return False  # Skip if the app is Chrome.
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)  # Attempt to close the app.
            return True  # Indicate success.
        except Exception as e:
            print(f"Error closing app '{app}': {e}")
            return False  # Indicate failure.

# Function to execute system-level commands.
def System(command):
    command = command.strip().lower()  # Normalize the command
    if not command:
        print("Error: Empty system command")
        return False
        
    try:
        # Nested function to mute the system volume.
        def mute():
            keyboard.press_and_release("volume mute")  # Simulate the mute key press.
            return True

        # Nested function to unmute the system volume.
        def unmute():
            keyboard.press_and_release("volume mute")  # Simulate the unmute key press.
            return True

        # Nested function to increase the system volume.
        def volume_up():
            keyboard.press_and_release("volume up")  # Simulate the volume up key press.
            return True

        # Nested function to decrease the system volume.
        def volume_down():
            keyboard.press_and_release("volume down")  # Simulate the volume down key press.
            return True

        # Execute the appropriate command.
        if command == "mute":
            return mute()
        elif command == "unmute":
            return unmute()
        elif command == "volume up":
            return volume_up()
        elif command == "volume down":
            return volume_down()
        else:
            print(f"Unknown system command: {command}")
            return False
    except Exception as e:
        print(f"Error executing system command '{command}': {e}")
        return False

# Asynchronous function to translate and execute user commands.
async def TranslateAndExecute(commands: list[str]):
    if not commands:
        print("No commands to execute")
        return
        
    funcs = []  # List to store asynchronous tasks.

    for command in commands:
        command = command.strip()
        if not command:
            continue
            
        if command.startswith("open"):  # Handle "open" commands.
            if "open it" in command or "open file" in command:  # Ignore specific commands.
                print(f"Skipping command: {command}")
                continue
            else:
                app_name = command.removeprefix("open").strip()
                fun = asyncio.to_thread(OpenApp, app_name)  # Schedule app opening.
                funcs.append(fun)
        elif command.startswith("general"):  # Placeholder for general commands.
            print(f"General command not implemented: {command}")
            continue
        elif command.startswith("realtime "):  # Placeholder for real-time commands.
            print(f"Realtime command not implemented: {command}")
            continue
        elif command.startswith("close"):  # Handle "close" commands.
            app_name = command.removeprefix("close").strip()
            fun = asyncio.to_thread(CloseApp, app_name)  # Schedule app closing.
            funcs.append(fun)
        elif command.startswith("play"):  # Handle "play" commands.
            query = command.removeprefix("play").strip()
            fun = asyncio.to_thread(PlayYoutube, query)  # Schedule YouTube playback.
            funcs.append(fun)
        elif command.startswith("content"):  # Handle "content" commands.
            topic = command.removeprefix("content").strip()
            fun = asyncio.to_thread(Content, topic)  # Schedule content creation
            funcs.append(fun)
        elif command.startswith("google search"):  # Handle Google search commands
            query = command.removeprefix("google search").strip()
            fun = asyncio.to_thread(GoogleSearch, query)  # Schedule Google search.
            funcs.append(fun)
        elif command.startswith("youtube search"):  # Handle YouTube search commands.
            query = command.removeprefix("youtube search").strip()
            fun = asyncio.to_thread(YouTubeSearch, query)  # Schedule YouTube search.
            funcs.append(fun)
        elif command.startswith("system"):  # Handle system commands.
            sys_command = command.removeprefix("system").strip()
            fun = asyncio.to_thread(System, sys_command)  # Schedule system command.
            funcs.append(fun)
        else:
            print(f"No Function Found. For {command}")  # Print an error for unrecognized commands.

    if funcs:
        results = await asyncio.gather(*funcs)  # Execute all tasks concurrently.
        
        for i, result in enumerate(results):  # Process the results.
            print(f"Command {i+1} result: {result}")
            yield result
    else:
        print("No functions to execute")
        yield False

# Asynchronous function to automate command execution.
async def Automation(commands: list[str]):
    try:
        results = []
        async for result in TranslateAndExecute(commands):  # Translate and execute commands.
            results.append(result)
        return all(results) if results else False  # Indicate success only if all commands succeeded
    except Exception as e:
        print(f"Error in automation: {e}")
        return False

# Example usage - this is how you would call the function
if __name__ == "__main__":
    # asyncio.run(Automation(["content write a letter about climate change"]))
    pass