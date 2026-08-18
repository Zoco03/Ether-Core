import sys
import io
import os
import re

# Safe UTF-8 reconfiguration for Windows console output
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from agency import run_agency, AGENTS_REGISTRY

app = FastAPI(title="Ether Core API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str
    mode: str
    async_execution: Optional[bool] = False

def auto_save_files(agency_output: str, output_dir: str = "project_output") -> List[str]:
    os.makedirs(output_dir, exist_ok=True)
    saved_files = []

    # Split output by [FILE: relative/path/to/file.ext] tags
    file_blocks = re.split(r'\[FILE:\s*([^\]]+)\]', agency_output)

    if len(file_blocks) > 1:
        # Odd indices are filenames, even indices (starting at 2) are contents
        for i in range(1, len(file_blocks), 2):
            rel_path = file_blocks[i].strip().strip('`"* ')
            raw_content = file_blocks[i + 1]

            # Stop content extraction if another file tag or section header starts lower down
            content = raw_content.split('[FILE:')[0].strip()

            # Clean markdown code blocks if present
            content = re.sub(r'^```[a-zA-Z]*\n', '', content)
            content = re.sub(r'\n```$', '', content)
            content = content.strip('` \n')

            if rel_path and content:
                full_path = os.path.join(output_dir, rel_path)
                
                # Automatically create nested subdirectories (e.g. project_output/frontend/)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content + "\n")

                saved_files.append(rel_path)

        if saved_files:
            return saved_files

    # Fallback parser for standard markdown code blocks without [FILE:] tags
    fallback_matches = re.findall(r"```[^\n]*\n([\s\S]*?)```", agency_output)
    if fallback_matches:
        for i, code in enumerate(fallback_matches):
            if code.strip():
                clean_name = f"auto_generated_{i+1}.txt"
                full_path = os.path.join(output_dir, clean_name)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(code.strip() + "\n")
                saved_files.append(clean_name)

    return saved_files

# NEW: Dynamic Agent Endpoint
@app.get("/api/agents")
async def get_agents():
    """Returns the exact living agent list from agency.py"""
    return [
        {"tag": a["tag"], "name": a["name"], "icon": a["icon"]}
        for a in AGENTS_REGISTRY
    ]

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        response = await run_agency(request.prompt, request.mode, request.async_execution)
        
        saved_files = []
        if request.mode in ["2", "3"] and response:
            saved_files = auto_save_files(str(response))
            
        return {
            "status": "success",
            "response": str(response),
            "saved_files": saved_files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
