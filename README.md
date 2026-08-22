# Ether Core

> An intelligent multi-agent orchestration workbench and desktop assistant developed by **Dox Interactive**.

Ether Core orchestrates a specialized crew of autonomous AI agents powered by unique cloud models via OpenRouter. Built with a Python-powered multi-agent backend and a responsive React frontend, it streamlines software engineering, system architecture design, deep technical research, and automated documentation.

---

## Key Features

* **Manual Mode Selection (The Gatekeeper):**
  * **Answer Mode:** Rapid, 2–3 line conversational answers to factual or direct queries without waking the development crew.
  * **Code Mode:** Full orchestration loop involving frontend, backend, and database engineers to design and implement complete software modules.
  * **Research Mode:** Deep context gathering and structured technical documentation generation.
* **Bilingual Voice Engine:** Integrated support for English and Hindi voice input and natural text-to-speech output.
* **Dedicated Specialists:** Highly capable OpenRouter free-tier models assigned to distinct architectural roles.
* **Concurrent Execution:** Unified single-command startup linking the Python server backend with the React interface.

---

## Agent Roster & Architecture

| Agent Role | Model Provider (OpenRouter) | Primary Focus |
| :--- | :--- | :--- |
| **Executive Boss / Router** | `nvidia/nemotron-3-ultra-550b-a55b:free` | Task triage, intent routing, and crew orchestration |
| **Frontend UI/UX Specialist** | `cohere/north-mini-code:free` | Layouts, component architecture, and styling |
| **Backend API Architect** | `nvidia/nemotron-3-super-120b-a12b:free` | Endpoints, routing, middleware, and server logic |
| **Database & Systems Engineer** | `nvidia/nemotron-3-super-120b-a12b:free` | Schema design, hardware states, and data models |
| **Technical Researcher** | `google/gemma-4-31b-it:free` | Intel gathering, dependency audits, and documentation checks |
| **Documentation Specialist** | `openai/gpt-oss-20b:free` | Markdown synthesis, setup guides, and technical breakdowns |

---

## Tech Stack

* **Frontend:** React, HTML5, CSS3, JavaScript
* **Backend & Orchestration:** Python, CrewAI, LiteLLM, Express/Flask server scripts
* **Audio & Voice:** `speech_recognition`, `gTTS`, `pygame`, `PyAudio`
* **Process Management:** `concurrently`

---

## Getting Started

### Prerequisites

Ensure you have the following installed on your machine:
* **Node.js** (v18.x or higher)
* **Python** (v3.10 to v3.13)
* **Git**

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Zoco03/Ether-Core.git](https://github.com/Zoco03/Ether-Core.git)
   cd Ether-Core
