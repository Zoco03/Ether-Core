import sys
import io
import os

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

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# 1. Cloud Model Connectors via OpenRouter (Active Working Free Models)
boss_llm = LLM(
    model="openrouter/nvidia/nemotron-3-ultra-550b-a55b:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

frontend_llm = LLM(
    model="openrouter/cohere/north-mini-code:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

backend_api_llm = LLM(
    model="openrouter/nvidia/nemotron-3-super-120b-a12b:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

backend_db_llm = LLM(
    model="openrouter/nvidia/nemotron-3-super-120b-a12b:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

research_llm = LLM(
    model="openrouter/google/gemma-4-31b-it:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

doc_llm = LLM(
    model="openrouter/openai/gpt-oss-20b:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

# 2. Worker Agents
frontend_agent = Agent(
    role="Frontend UI/UX Specialist",
    goal="Design clean, modern, and accessible user interfaces and web layouts.",
    backstory="You are an expert in HTML, CSS, JavaScript, and modern component frameworks.",
    llm=frontend_llm,
    verbose=True
)

backend_api_agent = Agent(
    role="Backend API Architect",
    goal="Implement secure, scalable REST/gRPC endpoints and application logic.",
    backstory="You write production-ready backend code in Python, Node.js, and other modern runtimes.",
    llm=backend_api_llm,
    verbose=True
)

backend_db_agent = Agent(
    role="Database & Systems Engineer",
    goal="Design efficient data models, schema structures, and optimized queries.",
    backstory="You specialize in database design, caching layers, and backend state handling.",
    llm=backend_db_llm,
    verbose=True
)

research_agent = Agent(
    role="Technical Researcher",
    goal="Investigate best practices, dependencies, libraries, and relevant documentation.",
    backstory="You find the best technical approaches and solutions before code execution.",
    llm=research_llm,
    verbose=True
)

doc_agent = Agent(
    role="Documentation Specialist",
    goal="Produce structured Markdown documentation and clear setup instructions.",
    backstory="You organize complex multi-agent outputs into concise developer documentation.",
    llm=doc_llm,
    verbose=True
)

# 3. Dynamic Agent Registry for React Frontend
AGENTS_REGISTRY = [
    {"tag": "@frontend", "name": frontend_agent.role, "agent": frontend_agent, "icon": "🎨"},
    {"tag": "@backend_api", "name": backend_api_agent.role, "agent": backend_api_agent, "icon": "⚡"},
    {"tag": "@backend_db", "name": backend_db_agent.role, "agent": backend_db_agent, "icon": "🗄️"},
    {"tag": "@research", "name": research_agent.role, "agent": research_agent, "icon": "🔍"},
    {"tag": "@doc", "name": doc_agent.role, "agent": doc_agent, "icon": "📝"},
]

# 4. Agency Execution Loop
async def run_agency(user_prompt: str, mode_choice: str, async_execution: bool = False) -> str:
    """Manually routes the task based on the user's selection."""
    
    if mode_choice == '1':
        answer_agent = Agent(
            role="Executive Assistant",
            goal="Answer general questions instantly and concisely.",
            backstory="You are a sharp, efficient assistant. You do not write code. You answer questions directly.",
            llm=doc_llm,
            verbose=False
        )

        answer_task = Task(
            description=f"Answer this prompt directly: '{user_prompt}'. Your response MUST be a maximum of 2 to 3 short, snappy lines.",
            expected_output="A conversational answer, strictly 2-3 lines maximum.",
            agent=answer_agent,
            async_execution=async_execution
        )

        answer_crew = Crew(agents=[answer_agent], tasks=[answer_task], verbose=False)
        result = await answer_crew.kickoff_async()
        return str(result.raw)

    elif mode_choice == '2':
        print("\n[System] Code Mode engaged. Orchestrating with Boss Agent...")
        
        # Determine which agents to include based on @ tags
        active_agents = []
        for reg in AGENTS_REGISTRY:
            if reg["tag"] in user_prompt:
                active_agents.append(reg["agent"])
        
        # If no tags are provided, fallback to default dev agents
        if not active_agents:
            active_agents = [frontend_agent, backend_api_agent, backend_db_agent]
            
        project_task = Task(
            description=f"Analyze and implement the following code request: {user_prompt}\n"
                        f"CRITICAL INSTRUCTION: As the manager, break down this request into sub-tasks for your available specialists. "
                        f"Ensure they share context (e.g., database schemas, API endpoints, variable names) so the final code integrates perfectly.\n"
                        f"CRITICAL INSTRUCTION: Every generated code block MUST begin with a filename tag like [FILE: path/filename.ext]. "
                        f"Review the specialists' work to ensure this formatting is strictly followed.",
            expected_output="Final compiled code implementation integrating the work of all specialists, with precise technical breakdowns and strict [FILE: filename] tags for every file.",
            async_execution=async_execution
        )

        dev_crew = Crew(
            agents=active_agents,
            tasks=[project_task],
            process=Process.hierarchical,
            manager_llm=boss_llm,
            verbose=True
        )

        result = await dev_crew.kickoff_async() 
        return str(result.raw)

    elif mode_choice == '3':
        print("\n[System] Research Mode engaged. Gathering intel...")
        
        research_task = Task(
            description=f"Perform a deep-dive analysis and research report on: {user_prompt}",
            expected_output="A detailed, well-structured research report summarizing the key findings.",
            agent=research_agent,
            async_execution=async_execution
        )

        research_crew = Crew(
            agents=[research_agent, doc_agent],
            tasks=[research_task],
            verbose=True
        )

        result = await research_crew.kickoff_async()
        return str(result.raw)
