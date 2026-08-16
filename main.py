import asyncio
import random
import os
import time
import speech_recognition as sr
from gtts import gTTS
import pygame
from agency import run_agency

# Initialize the audio mixer for voice output
pygame.mixer.init()

async def speak_to_user(text: str):
    """Converts text to speech supporting both English and Hindi."""
    try:
        # Generate the audio file using Google TTS (lang='hi' handles both English and Hindi)
        tts = gTTS(text=text, lang='hi')
        filename = "response.mp3"
        tts.save(filename)
        
        # Load and play the audio file
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        
        # Keep the script running while the audio plays
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        # Unload the file so it can be safely deleted
        pygame.mixer.music.unload()
        os.remove(filename)
        
    except Exception as e:
        print(f"\n[TTS Error]: {e}")

def listen_to_user():
    """Activates the microphone and transcribes Hinglish (Hindi + English)."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n[Microphone Active] Listening... (Speak in English or Hindi)")
        # Calibrate for background noise
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)

    try:
        # Setting language to 'hi-IN' allows the Google API to recognize both seamlessly
        print("[System] Processing audio...")
        transcription = recognizer.recognize_google(audio, language="hi-IN")
        print(f"You (Voice): {transcription}")
        return transcription
    
    except sr.UnknownValueError:
        print("\n[Error] Could not understand audio. Please try again.")
        return None
    except sr.RequestError as e:
        print(f"\n[Error] Speech Recognition service unavailable: {e}")
        return None

async def main():
    while True:
        try:
            print("\n" + "="*50)
            print(" DOX INTERACTIVE WORKBENCH (v2026) ")
            print("="*50)
            print("1. Answer Mode (Quick 2-3 lines)")
            print("2. Code Mode (Multi-Agent Dev Crew)")
            print("3. Research Mode (Deep Dive & Docs)")
            print("="*50)
            
            mode_choice = input("\nSelect a mode (1/2/3) or type 'exit': ").strip().lower()
            
            if mode_choice == 'exit':
                print("\nShutting down systems. Goodbye.")
                break
                
            if mode_choice not in ['1', '2', '3']:
                print("\n[Error] Invalid choice. Please type 1, 2, or 3.")
                continue

            input_method = input("\nPress 'ENTER' to speak, or type your prompt directly: ").strip()
            
            if input_method == "":
                # If they just press ENTER, activate the microphone
                user_prompt = listen_to_user()
                if not user_prompt:
                    continue # Skip this loop if the microphone didn't catch anything
            else:
                # If they typed something, use that as the prompt
                user_prompt = input_method
                
            if user_prompt.lower() == 'exit':
                print("\nShutting down systems. Goodbye.")
                break

            print("\n[System] Agents are processing your request...")
            
            # Pass BOTH the prompt and the mode_choice to the agency routing system
            response = await run_agency(user_prompt, mode_choice)

            # Print the final output to the terminal silently
            print("\n" + "="*60)
            print(" FINAL OUTPUT ")
            print("="*60)
            print(response)
            print("="*60 + "\n")

            # Smart TTS Logic: Decide what to speak out loud
            if "```" in response or len(response) > 400:
                completion_lines = [
                    "The job is finished. Your code is printed in the terminal.",
                    "Task executed successfully. I am ready for your next command.",
                    "The Dox Interactive team has completed the build. Check your logs.",
                    "All agents have reported back. Your files are ready."
                ]
                phrase_to_speak = random.choice(completion_lines)
            else:
                # If it is a short conversational answer, read the actual text out loud!
                phrase_to_speak = response
            
            await speak_to_user(phrase_to_speak)

        except KeyboardInterrupt:
            print("\nStopping workbench...")
            break
        except Exception as e:
            print(f"\n[Error Encountered]: {e}")

if __name__ == "__main__":
    asyncio.run(main())