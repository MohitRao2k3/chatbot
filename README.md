LangGraph Memory Chatbot
A conversational chatbot built with LangGraph, Google Gemini,
Streamlit, and PostgreSQL. It is designed to keep conversations
organized by thread and store user-specific memories across
conversations.
> **Current status:** RAG has **not** been integrated yet. This version
> uses stored user memories and conversation checkpoints; it does not
> retrieve relevant chunks from a document knowledge base.
Features
Chat interface built with Streamlit.
Google Gemini model for responses.
LangGraph workflow for handling messages and memory updates.
PostgreSQL-backed long-term user memory using `PostgresStore`.
PostgreSQL-backed conversation state/checkpoints using
`PostgresSaver`.
Environment-variable configuration for API keys and database
connection.
Project files
``` text
your-project/
├── chatbot_frontend.py   # Streamlit user interface
├── memory_graph.py       # LangGraph workflow and memory logic
├── requirements.txt      # Python dependencies
├── .env                  # Local secrets; do not commit this file
└── .gitignore
```
Adjust the filenames in these instructions if your repository uses a
different structure.
Requirements
Python 3.10 or a compatible version supported by your installed
dependencies
Docker Desktop (for running PostgreSQL locally), or a reachable
PostgreSQL database
A Google AI API key
Git (optional, for version control and deployment)
Installation and local setup
1. Clone the repository
``` bash
git clone https://github.com/MohitRao2k3/chatbot.git
cd chatbot
```
If the repository contains additional folders, move into the folder that
contains `chatbot_frontend.py`.
2. Create and activate a virtual environment
Windows PowerShell:
``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
If PowerShell blocks activation, you can run the environment's Python
directly or use Command Prompt activation:
``` bat
.venv\Scripts\activate.bat
```
3. Install dependencies
Create a `requirements.txt` file with the packages used by the project,
or use the repository's existing file:
``` text
streamlit
langgraph
langchain-core
langchain-google-genai
langgraph-checkpoint-postgres
langchain-postgres
psycopg[binary,pool]
python-dotenv
```
Install them:
``` powershell
pip install -r requirements.txt
```
For reproducible deployments, pin tested package versions once the
application is working reliably.
4. Start PostgreSQL locally with Docker
If you already have a PostgreSQL container named `memory-postgres-1`,
start it:
``` powershell
docker start memory-postgres-1
```
To create a new container instead, run this only if you do not already
have a suitable container:
``` powershell
docker run --name memory-postgres-1 `
  -e POSTGRES_USER=postgres `
  -e POSTGRES_PASSWORD=postgres `
  -e POSTGRES_DB=postgres `
  -p 5442:5432 `
  -v memory_pgdata:/var/lib/postgresql/data `
  -d postgres:16
```
Check that it is running:
``` powershell
docker ps
```
Test the database:
``` powershell
docker exec -it memory-postgres-1 psql -U postgres -d postgres -c "SELECT 1;"
```
5. Configure environment variables
Create a `.env` file in the project root:
``` dotenv
DB_URI=postgresql://postgres:postgres@127.0.0.1:5442/postgres?sslmode=disable
GOOGLE_API_KEY=replace_with_your_google_ai_api_key
GEMINI_MODEL=gemini-3.6-flash
```
Use the model name supported by your Google AI account and the model
configured in your code. The example database URL assumes the local
Docker container uses the username `postgres`, password `postgres`,
database `postgres`, and host port `5442`. Change it if your settings
differ.
Security: Never commit `.env` or publish API keys, database
passwords, or production connection strings. Keep `.env` in
`.gitignore`.
6. Run the application
From the directory containing `chatbot_frontend.py`, run:
``` powershell
streamlit run chatbot_frontend.py
```
Streamlit will print a local URL, usually `http://localhost:8501`.
How the workflow works
At a high level:
The user submits a message in the Streamlit interface.
LangGraph runs the workflow.
The memory step reads existing user memories and may save new memory
items to PostgreSQL.
The chat step sends the conversation context and available memories
to Gemini.
PostgreSQL checkpointing stores conversation state for the
configured thread.
The precise behavior depends on the implementation in `memory_graph.py`
and `chatbot_frontend.py`.
Current limitation: RAG is not integrated
Retrieval-Augmented Generation (RAG) is not currently part of this
project.
The existing long-term memory feature is not the same as document RAG:
Long-term memory stores selected user facts or preferences for
future conversations.
RAG typically loads documents, splits them into chunks, creates
embeddings, retrieves relevant chunks for a question, and provides
those chunks to the language model as context.
To add RAG later, you would generally add a document ingestion/indexing
process, an embedding model, a vector store or retriever, and a
retrieval step in the LangGraph workflow. The retriever would fetch
relevant document passages before the chat model generates an answer.
The exact design depends on the document types and database/vector-store
choice.
Until those pieces are implemented and connected to the graph, do not
describe this version as a RAG chatbot.
Deployment notes
The app can be deployed to a Python hosting platform such as Railway or
Render. A Streamlit hosting service is another option for the frontend.
For a cloud deployment:
Push the application code and `requirements.txt` to GitHub.
Provision a persistent, reachable PostgreSQL database.
Configure `DB_URI` using the database provider's connection string
or internal service reference.
Add `GOOGLE_API_KEY` and `GEMINI_MODEL` as hosting-platform
environment variables.
Configure the start command:
    ``` bash
    streamlit run chatbot_frontend.py --server.address 0.0.0.0 --server.port $PORT
    ```
Deploy and check the application logs if startup fails.
Do not use the local `localhost:5442` database URL in the cloud. In a
hosted service, `localhost` refers to that service's own environment,
not your computer. Use the cloud database connection URL instead.
Multi-user note
If the application is publicly accessible, make sure each authenticated
user receives a distinct, trustworthy `user_id`. A fixed ID such as `u1`
can cause users to share memory. Add authentication and enforce
user-level data isolation before offering the chatbot to multiple
people.
Troubleshooting
PostgreSQL connection timeout
Confirm the database container/service is running.
For local Docker, check `docker ps` and
`docker port memory-postgres-1`.
Confirm the host port in `DB_URI` matches the published port (for
example, `5442`).
Verify the database username, password, and database name.
For cloud deployment, use the provider's database URL rather than
`localhost`.
Missing API key
Confirm `GOOGLE_API_KEY` exists in `.env` locally or in the hosting
platform's environment-variable settings.
Restart the application after changing environment variables.
Never paste secret values into public logs, issues, or repositories.
Conversation or memory does not persist
Confirm both the store and checkpointer are connected to the
intended database.
Confirm database setup/initialization is run as required by the
code.
Check that the same intended `thread_id` is reused to resume a
conversation and the correct `user_id` is used for memory.
Inspect application logs for database or graph errors.
Roadmap
[ ] Add document ingestion and chunking for RAG.
[ ] Add embeddings and a retriever/vector store.
[ ] Add a LangGraph retrieval step that supplies relevant document
context to the model.
[ ] Add authentication and per-user memory isolation before public
multi-user use.
[ ] Pin tested dependency versions and add automated tests.
License
Add the license appropriate for your project before distributing it.
