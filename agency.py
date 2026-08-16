import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# 1. Cloud Model Connectors via OpenRouter (Verified Free Slugs)
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
    model="openrouter/meta-llama/llama-3-8b-instruct:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

backend_db_llm = LLM(
    model="openrouter/qwen/qwen-2-7b-instruct:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

research_llm = LLM(
    model="openrouter/nvidia/nemotron-3-super-120b-a12b:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

doc_llm = LLM(
    model="openrouter/microsoft/phi-3-mini-128k-instruct:free",
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

# 3. Agency Execution Loop
async def run_agency(user_prompt: str, mode_choice: str) -> str:
    """Manually routes the task based on the user's terminal selection."""
    
    if mode_choice == '1':
        # -----------------------------------------
        # MODE 1: ANSWER (Quick, snappy, 2-3 lines)
        # -----------------------------------------
        answer_agent = Agent(
            role="Executive Assistant",
            goal="Answer general questions instantly and concisely.",
            backstory="You are a sharp, efficient assistant. You do not write code. You answer questions directly.",
            llm=boss_llm,
            verbose=False
        )

        answer_task = Task(
            description=f"Answer this prompt directly: '{user_prompt}'. Your response MUST be a maximum of 2 to 3 short, snappy lines.",
            expected_output="A conversational answer, strictly 2-3 lines maximum.",
            agent=answer_agent
        )

        answer_crew = Crew(agents=[answer_agent], tasks=[answer_task], verbose=False)
        result = await answer_crew.kickoff_async()
        return str(result.raw)

    elif mode_choice == '2':
        # -----------------------------------------
        # MODE 2: CODE (The full heavy-lifting crew)
        # -----------------------------------------
        print("\n[System] Code Mode engaged. Delegating to the development crew...")
        
        project_task = Task(
            description=f"Analyze and implement the following code request: {user_prompt}",
            expected_output="Code implementation with necessary technical breakdowns.",
            agent=frontend_agent
        )

        dev_crew = Crew(
            agents=[frontend_agent, backend_api_agent, backend_db_agent],
            tasks=[project_task],
            process=Process.hierarchical,
            manager_llm=boss_llm,
            verbose=True
        )

        result = await dev_crew.kickoff_async() 
        return str(result.raw)

    elif mode_choice == '3':
        # -----------------------------------------
        # MODE 3: RESEARCH (Information gathering)
        # -----------------------------------------
        print("\n[System] Research Mode engaged. Gathering intel...")
        
        research_task = Task(
            description=f"Perform a deep-dive analysis and research report on: {user_prompt}",
            expected_output="A detailed, well-structured research report summarizing the key findings.",
            agent=research_agent 
        )

        research_crew = Crew(
            agents=[research_agent, doc_agent],
            tasks=[research_task],
            verbose=True
        )

        result = await research_crew.kickoff_async()
        return str(result.raw)