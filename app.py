import tkinter as tk
import speech_recognition as sr
import threading
import pyautogui
import time

class SpeechToTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech to Text (Romanian)")
        self.root.minsize(250, 100)

        self.label = tk.Label(root, text="Click 'Start Speaking' to begin recording.")
        self.label.pack(pady=10)

        self.start_button = tk.Button(root, text="Start Speaking", command=self.start_listening)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="Stop Speaking", command=self.stop_listening, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.auto_enter_var = tk.IntVar()  # Variable for checkbox state
        self.auto_enter_checkbox = tk.Checkbutton(root, text="Auto Press Enter", variable=self.auto_enter_var)
        self.auto_enter_checkbox.pack(pady=5)

        self.error_var = tk.StringVar()  # Variable to hold error message
        self.error_label = tk.Label(root, textvariable=self.error_var, fg="red")
        self.error_label.pack(pady=5)

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.audio_queue = []
        self.recognition_thread = None
        self.last_speech_time = time.time()

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_listening(self):
        self.is_listening = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.label.config(text="Listening...")
        self.error_var.set("")  # Clear any previous error message

        def listen():
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                while self.is_listening:
                    try:
                        audio = self.recognizer.listen(source, phrase_time_limit=3)
                        self.audio_queue.append(audio)
                        self.last_speech_time = time.time()
                    except Exception as e:
                        print(f"Listening error: {e}")

        def recognize_audio():
            while self.is_listening or self.audio_queue:
                if self.audio_queue:
                    audio = self.audio_queue.pop(0)
                    try:
                        text = self.recognizer.recognize_google(audio, language="ro-RO")
                        pyautogui.typewrite(text + ' ', interval=0.05)
                        self.last_speech_time = time.time()
                    except sr.UnknownValueError:
                        pass  # Ignore unrecognized audio
                    except sr.RequestError as e:
                        print(f"Could not request results from Google Speech Recognition service; {e}")
                else:
                    # Check for a long period of silence
                    if self.auto_enter_var.get() and time.time() - self.last_speech_time > 5:
                        pyautogui.press('enter')
                        self.last_speech_time = time.time()
                time.sleep(0.1)  # Small sleep to prevent busy waiting

        self.recognition_thread = threading.Thread(target=recognize_audio)
        self.recognition_thread.start()

        self.listening_thread = threading.Thread(target=listen)
        self.listening_thread.start()

    def stop_listening(self):
        self.is_listening = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.label.config(text="Click 'Start Speaking' to begin recording.")
        self.error_var.set("")  # Clear any error message when stopping

        # Wait for threads to finish processing
        while self.recognition_thread.is_alive() or self.listening_thread.is_alive():
            time.sleep(0.1)

    def on_closing(self):
        self.is_listening = False  # Stop listening
        # Wait for threads to finish processing
        if self.recognition_thread is not None:
            self.recognition_thread.join(timeout=1)
        if self.listening_thread is not None:
            self.listening_thread.join(timeout=1)
        self.root.destroy()  # Close the Tkinter window

def main():
    root = tk.Tk()
    app = SpeechToTextApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
