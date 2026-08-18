import asyncio
import random
import os
import re
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

def process_and_save_files(agency_output: str, output_dir: str = "project_output"):
    """Extracts code blocks and saves them, with a fallback for missing file tags."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Attempt 1: Look for the strict [FILE: name] tag
    pattern = r"\[FILE:\s*(.*?)\][\s\S]*?```[^\n]*\n(.*?)```"
    matches = re.findall(pattern, agency_output, flags=re.DOTALL)
    
    if matches:
        print(f"\n[System] 📁 Found {len(matches)} perfectly formatted files:")
        for filename, code in matches:
            filename = filename.strip().split('/')[-1].split('\\')[-1] 
            full_path = os.path.join(output_dir, filename)
            
            permission = input(f"  ⚠️ Update/Create '{full_path}'? (y/n): ")
            if permission.lower() == 'y':
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as file:
                    file.write(code.strip() + "\n")
                print(f"  ✅ Saved successfully to: {full_path}")
            else:
                print(f"  ❌ Skipped: {full_path}")
        return # If it worked perfectly, stop here.

    # Attempt 2 (FALLBACK): The AI forgot the tag, but still wrote a markdown code block
    fallback_pattern = r"```[^\n]*\n(.*?)```"
    fallback_matches = re.findall(fallback_pattern, agency_output, flags=re.DOTALL)
    
    if fallback_matches:
        print(f"\n[System] ⚠️ The AI generated code, but forgot to name the files.")
        for i, code in enumerate(fallback_matches):
            
            # Show a tiny preview of what the code is so the user knows what to name it
            preview = code.strip()[:80].replace('\n', ' ')
            print(f"\n--- Code Block {i+1} Preview ---")
            print(f"{preview}...")
            print("-----------------------------")
            
            filename = input(f"  Enter filename to save as (e.g. 'index.html') or press ENTER to skip: ").strip()
            
            if filename:
                # Clean up the filename
                filename = filename.strip().split('/')[-1].split('\\')[-1] 
                full_path = os.path.join(output_dir, filename)
                
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as file:
                    file.write(code.strip() + "\n")
                print(f"  ✅ Saved successfully to: {full_path}")
            else:
                print(f"  ❌ Skipped block {i+1}")
    else:
        print("\n[System] ⚠️ No code blocks were detected in the AI's response at all.")

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

            # === MULTI-FILE ATTACHMENT LOGIC (Max 5) ===
            attached_context = ""
            print("\n[Optional] You can attach up to 5 existing files for context.")
            print("Type the filename (e.g., 'index.html') or press ENTER to skip/finish.")
            
            attached_count = 0
            while attached_count < 5:
                attach_file = input(f"  📎 Attach file {attached_count + 1}/5: ").strip()
                
                if not attach_file:
                    break # User pressed ENTER on an empty line, stop asking
                
                # Check inside project_output first, then fallback to current directory
                file_path = os.path.join("project_output", attach_file)
                if not os.path.exists(file_path):
                    file_path = attach_file
                    
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            file_content = f.read()
                        
                        attached_context += f"\n\n--- CURRENT CONTENTS OF {attach_file} ---\n```\n{file_content}\n```\n--- END OF CURRENT FILE ---\n"
                        attached_count += 1
                        print(f"  ✅ Added {attach_file}")
                    except Exception as e:
                        print(f"  ❌ Could not read '{file_path}': {e}")
                else:
                    print(f"  ❌ Could not find '{attach_file}'. Make sure the name is correct.")
            
            # Combine the user prompt with all attached files
            final_prompt = user_prompt
            if attached_context:
                final_prompt += f"\n{attached_context}\nPlease consider the attached files above when processing this request."
            # ============================================

            print("\n[System] Agents are processing your request...")
            
            # Pass the COMBINED prompt to the agency
            response = await run_agency(final_prompt, mode_choice)

            # === ROBUST SAFETY CHECKS ===
            if response is None:
                print("\n[System Error] The AI failed to respond (Likely an API timeout). Let's try again.")
                await speak_to_user("The connection timed out. Please try your request again.")
                continue

            if response == "None":
                print("\n[System Error] The AI returned 'None' as a string. Retrying...")
                await speak_to_user("The connection timed out. Please try your request again.")
                continue

            # Ensure we have a string to safely use 'in' and 'len'
            response = str(response)
            # =============================

            # Print the final output to the terminal silently
            print("\n" + "="*60)
            print(" FINAL OUTPUT ")
            print("="*60)
            print(response)
            print("="*60 + "\n")
            
            # === File Saving Logic ===
            if mode_choice in ['2', '3']:
                process_and_save_files(response)
            # ==============================

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
                phrase_to_speak = response
            
            await speak_to_user(phrase_to_speak)

        except KeyboardInterrupt:
            print("\nStopping workbench...")
            break
        except Exception as e:
            print(f"\n[Error Encountered]: {e}")

if __name__ == "__main__":
    asyncio.run(main())