# PPT Generator - Project Documentation

This document contains a comprehensive overview of the **PPT Generator**, an AI-Powered Presentation Builder. It outlines the dependencies, the underlying workflow, and the key architectural decisions made. This guide is designed to help anyone replicate the project's functionality from scratch.

---

## 1. Project Overview

The PPT Generator is a multi-agent AI system designed to transform user prompts into beautiful presentations. It uses **CrewAI** to orchestrate specialized AI agents and the **Google Gemini API** to generate the content. The frontend provides a modern React-based user interface with real-time progress tracking, communicating with the backend via REST APIs and WebSockets.

---

## 2. Dependencies

The project is split into a Python backend and a Node/React frontend.

### Backend Dependencies (Python 3.13)
The backend uses a virtual environment (`venv`) and requires the following key libraries (listed in `backend/requirements.txt`):

*   **Core Frameworks**: `flask==3.1.0`
*   **AI & Agents**: `crewai>=0.11.0`, `google-generativeai==0.8.3`
*   **Real-time Communication**: `python-socketio==5.11.4`, `flask-socketio==5.4.1`
*   **Web Setup**: `flask-cors==5.0.0`, `python-dotenv==1.0.1`, `requests==2.32.3`
*   **PDF/Presentation Generation**: 
    *   `weasyprint==60.2` (Converts HTML slides to PDF)
    *   `pydyf==0.8.0` (Pinned for WeasyPrint compatibility)
    *   `Pillow==10.4.0`
    *   `beautifulsoup4==4.12.3`
    *   `python-pptx>=1.0.2`

### Frontend Dependencies (Node 20+)
The frontend is a Vite + React application. Key packages (from `frontend/ppt-generator/package.json`):

*   **Framework**: `react^19.1.1`, `react-dom^19.1.1`
*   **Build Tool**: `vite^7.1.2`
*   **Styling**: Tailwind CSS via `@tailwindcss/postcss^4.1.12`, `tailwind-merge^3.3.1`, `clsx^2.1.1`
*   **UI Components**: `@headlessui/react^2.2.7`, `lucide-react^0.542.0`
*   **Networking**: `axios^1.11.0`

---

## 3. Workflow Architecture

The application workflow follows a clear path from user input to the final presentation file.

1.  **User Input (Frontend)**: The user opens the React frontend (`http://localhost:5173`), enters a presentation topic (e.g., "Impact of AI in Business"), selects a theme, and specifies the number of slides.
2.  **API Request**: The frontend makes a POST request to `/api/presentations` on the Flask backend (`http://localhost:5000`).
3.  **WebSocket Connection**: The frontend joins a WebSocket room specific to the `project_id` to receive real-time updates as the agents work.
4.  **Agent Orchestration (Backend)**: 
    *   The `PPTProjectManager` initializes a new project state.
    *   It triggers `PPTCrew.create_presentation()`.
    *   **Planner Agent**: Analyzes the request and creates a presentation blueprint.
    *   **Content Creator Agent**: Expands the blueprint into detailed content, slide by slide.
    *   **Designer Agent**: Provides visual context and instructions.
5.  **Data Processing**: The final output from the CrewAI agents is expected to be HTML code blocks or JSON. The `_extract_crew_result` and `_clean_json_content` methods parse this output.
6.  **HTML Generation**: The content is mapped to a selected `ThemeConfig` (e.g., 'corporate_blue'). Each slide is wrapped in a styled HTML `div` representing a 1920x1080px page.
7.  **PDF Conversion**: `Weasyprint` takes the combined HTML document and converts it into a formatted `.pdf` file. *(Note: While the README claims `.pptx` generation, the core logic actually relies on Weasyprint PDF generation for the final output).*
8.  **Completion**: A WebSocket event (`project_completed`) is fired, and the frontend allows the user to download the final generated PDF file.

---

## 4. Key Architectural Decisions

1.  **CrewAI for Multi-Agent System**: Instead of relying on a single LLM prompt, the workload is distributed across specialized agents. This separation of concerns yields higher quality content—the planner focuses on structure, the content creator on depth, and the designer on aesthetics.
2.  **WebSockets for Real-Time Feedback**: Presentation generation takes time. `flask-socketio` is used to push live status updates to the user interface, improving user experience by showing exactly what step the AI is currently working on.
3.  **HTML-to-PDF Pipeline**: Instead of using native PowerPoint SDKs (like python-pptx alone) to build complex visual slides from scratch, the system generates HTML using CSS for styling, and converts it to PDF via `weasyprint`. This allows for highly customizable, web-native designs (gradients, drop shadows) that are hard to programmatically construct in native PowerPoint files.
4.  **WeasyPrint Compatibility Pinning**: WeasyPrint `60.2` has strict compatibility limits with `pydyf`. It was intentionally decided to pin `pydyf==0.8.0` in the requirements to prevent `TypeError: PDF.__init__() takes 1 positional argument but 3 were given` errors during PDF construction.
5.  **Eventlet / Threading**: The Flask-SocketIO implementation utilizes standard threading (`async_mode='threading'`) for simplicity and compatibility across different local environments, rather than requiring complex async loops.
6.  **File System State Management**: Project metadata and intermediate generated files are saved directly to the file system (in `temp/` and `generated_ppts/`) rather than an external database. This keeps the application lightweight, easily deployable, and simple to debug.

---

## 5. Replication Steps (From Scratch)

To replicate this environment:

1.  **Backend setup**:
    ```bash
    mkdir backend && cd backend
    python3 -m venv venv
    source venv/bin/activate
    # Install dependencies listed above
    pip install crewai==0.11.0 flask==3.1.0 python-dotenv==1.0.1 python-socketio==5.11.4 flask-socketio==5.4.1 google-generativeai==0.8.3 flask-cors==5.0.0 Pillow==10.4.0 requests==2.32.3 dataclasses-json==0.6.4 weasyprint==60.2 beautifulsoup4==4.12.3 python-pptx>=1.0.2 pydyf==0.8.0
    # Set environment variables
    echo "GEMINI_API_KEY=your_key" > .env
    ```
2.  **Frontend setup**:
    ```bash
    mkdir frontend && cd frontend
    npm create vite@latest ppt-generator -- --template react
    cd ppt-generator
    npm install @headlessui/react axios clsx lucide-react tailwind-merge
    npm install -D tailwindcss @tailwindcss/postcss autoprefixer postcss
    ```
3.  **Execution**: 
    *   Backend: `python3 start_server.py`
    *   Frontend: `npm run dev --host`
