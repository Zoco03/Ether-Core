import chainlit as cl
import asyncio
import os
import re
from chainlit.input_widget import Select
from agency import run_agency 

# --- Chat Profiles (The Model Dropdown) ---
# This creates a native dropdown above your chat input to select the model/agent.
@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(name="Default Crew (Auto-Routing)", icon="🤖"),
        cl.ChatProfile(name="Frontend UI/UX Specialist", icon="🎨"),
        cl.ChatProfile(name="Backend API Architect", icon="⚙️"),
        cl.ChatProfile(name="Database Engineer", icon="🗄️"),
        cl.ChatProfile(name="Technical Researcher", icon="🔬")
    ]

# --- Chat Settings (The Mode Selectors) ---
@cl.on_chat_start
async def start():
    """Sets up the mode selector settings panel."""
    # This puts your Answer, Code, Research options in a settings panel attached to the input bar
    settings = await cl.ChatSettings(
        [
            Select(
                id="Mode",
                label="Select Mode",
                values=["Answer", "Code", "Research"],
                initial_index=0,
            )
        ]
    ).send()
    
    cl.user_session.set("current_mode", "1") # Default Answer mode

@cl.on_settings_update
async def setup_agent(settings):
    """Updates the mode when you change it in the UI."""
    mode_map = {"Answer": "1", "Code": "2", "Research": "3"}
    selected_mode = mode_map[settings["Mode"]]
    cl.user_session.set("current_mode", selected_mode)
    await cl.Message(content=f"✅ System set to **{settings['Mode']} Mode**.").send()


def auto_save_files(agency_output: str, output_dir: str = "project_output") -> list:
    """Extracts code blocks and auto-saves them to disk."""
    os.makedirs(output_dir, exist_ok=True)
    saved_files = []
    
    pattern = r"\[FILE:\s*(.*?)\][\s\S]*?```[^\n]*\n(.*?)```"
    matches = re.findall(pattern, agency_output, flags=re.DOTALL)
    
    if matches:
        for filename, code in matches:
            filename = filename.strip().split('/')[-1].split('\\')[-1] 
            full_path = os.path.join(output_dir, filename)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as file:
                file.write(code.strip().rstrip("`").strip() + "\n")
            saved_files.append(full_path)
        return saved_files

    fallback_pattern = r"```[^\n]*\n(.*?)```"
    fallback_matches = re.findall(fallback_pattern, agency_output, flags=re.DOTALL)
    
    if fallback_matches:
        for i, code in enumerate(fallback_matches):
            filename = f"auto_generated_code_{i+1}.txt"
            full_path = os.path.join(output_dir, filename)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as file:
                file.write(code.strip().rstrip("`").strip() + "\n")
            saved_files.append(full_path)
            
    return saved_files

@cl.on_message
async def main(message: cl.Message):
    """Handles the user's prompt."""
    current_mode = cl.user_session.get("current_mode")
    prompt = message.content
    
    # Read the model from the Chat Profile dropdown
    selected_profile = cl.user_session.get("chat_profile")
    
    attached_context = ""
    if message.elements:
        for element in message.elements:
            if "text" in element.mime or element.name.endswith(('.html', '.py', '.js', '.css', '.md', '.txt')):
                try:
                    with open(element.path, "r", encoding="utf-8") as f:
                        content = f.read()
                    attached_context += f"\n\n--- CONTENTS OF {element.name} ---\n{content}\n--- END ---\n"
                except Exception as e:
                    await cl.Message(content=f"⚠️ Could not read `{element.name}`: {e}").send()
        
        if attached_context:
            prompt += f"\n{attached_context}\nPlease consider the attached files above."

    # If the user selected a specific agent from the dropdown, append the tag to the prompt
    if selected_profile and selected_profile != "Default Crew (Auto-Routing)":
        prompt = f"@{selected_profile.split(' ')[0].lower()} {prompt}"

    async with cl.Step(name="🏢 Ether Core") as step:
        step.output = "📥 Reading prompt and attached files...\n"
        await asyncio.sleep(0.5)
        
        if selected_profile != "Default Crew (Auto-Routing)":
            step.output += f"🎯 Pinging **{selected_profile}**...\n"
        
        step.output += "⚙️ Processing task...\n🧠 Models are working...\n"
        
        # Run the backend
        final_output = await run_agency(prompt, current_mode)
        
        step.output += "✅ Reviewing final work."
    
    if final_output and final_output != "None":
        final_output = str(final_output)
        await cl.Message(content=final_output).send()
        
        if current_mode in ['2', '3']:
            saved_files = auto_save_files(final_output)
            if saved_files:
                files_list = "\n".join([f"- `{f}`" for f in saved_files])
                await cl.Message(content=f"📁 **Auto-Saved Files:**\n{files_list}").send()
    else:
        await cl.Message(content="❌ The API timed out or returned an empty response. Please try again.").send()
# --- Chat Profiles (The Model Dropdown) ---
@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="Default Crew (Auto-Routing)",
            markdown_description="Automatically routes tasks to the best-suited worker agent.",
            icon="🤖"
        ),
        cl.ChatProfile(
            name="Frontend UI/UX Specialist",
            markdown_description="Specializes in HTML, CSS, JavaScript, and UI frameworks.",
            icon="🎨"
        ),
        cl.ChatProfile(
            name="Backend API Architect",
            markdown_description="Specializes in Python, API endpoints, and server architecture.",
            icon="⚙️"
        ),
        cl.ChatProfile(
            name="Database Engineer",
            markdown_description="Specializes in database schemas, SQL, and system design.",
            icon="🗄️"
        ),
        cl.ChatProfile(
            name="Technical Researcher",
            markdown_description="Performs deep technical research, analysis, and documentation.",
            icon="🔬"
        )
    ]