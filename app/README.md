# PrepPilot Streamlit Chatting Interface

This is a clean, modern Streamlit-based chatting interface for PrepPilot, allowing users to select a subject and converse with the PrepPilot AI regarding that subject.

## Features

- **Subject Selection**: Lands on a welcome/selection page to retrieve and select subjects from the PrepPilot backend API.
- **Session Continuity**: Retains conversation memory using the backend's session management, showing tokens used/available.
- **Real-Time Streaming**: Implements real-time Server-Sent Events (SSE) streaming for a smooth typing effect.
- **Modern UI**: Dark/Light tailored color palette, premium layout, custom styling.

## Running Locally

1. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environmental variables (optional):
   - `BACKEND_URL`: Set the URL of your PrepPilot FastAPI backend (defaults to `http://localhost:8000`).
     - E.g., on Windows PowerShell: `$env:BACKEND_URL="http://localhost:8000"`

4. Run the application:
   ```bash
   streamlit run app.py
   ```
