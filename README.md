# Campus Buzz

Campus Buzz is a hybrid-cloud mini project that demonstrates the basic integration of:

- Frontend submission
- A workflow orchestration service
- Data persistence
- Serverless-style event processing (simulated)

The goal is to build a simple, reproducible pipeline:

Event submission → workflow persistence → event trigger → processing function → result write-back.

This project intentionally avoids complex authentication/authorization systems and heavy UI work, making it suitable for quickly validating system architecture and service orchestration.

## Project Structure

```
campus-buzz/
├── docker-compose.yml
├── README.md
├── requirements.txt
├── start-services.sh          # Script to quickly start all services for macOS/Linux
├── start-windows.bat          # Script to quickly start all services for Windows
├── venv/                      # Python virtual environment (created automatically after running the script)
├── services/
│   ├── data-service/
│   │   ├── api.py            # Flask API service providing CRUD operations for event records
│   │   ├── database.py       # SQLAlchemy model definitions
│   │   ├── Dockerfile        # Container configuration for the data service
│   │   └── requirements.txt  # Python dependencies
│   ├── workflow/
│   │   ├── main.py           # Flask API service handling event submissions
│   │   ├── Dockerfile        # Container configuration for the workflow service
│   │   └── requirements.txt  # Python dependencies
│   └── presentation/
│       ├── Dockerfile        # Container configuration for the frontend
│       ├── package.json      # Node.js dependencies and scripts
│       ├── public/
│       │   └── index.html    # Entry point for the React application
│       └── src/
│           ├── App.js        # Main React component
│           ├── index.js      # Entry point of the React app
│           ├── index.css     # Stylesheet
│           └── setupProxy.js # Proxy configuration for development environment
└── functions/
    ├── submission-event/
    │   ├── index.js          # Submission event function simulator (HTTP)
    │   └── Dockerfile        # Container configuration for the function
    ├── processor/
    │   ├── logic.py          # Event processing logic (validation and classification rules)
    │   ├── app.py            # Flask app for processing function
    │   └── Dockerfile        # Container configuration for the function
    └── result-update/
        ├── updater.py        # Logic for writing results back to Data Service
        ├── app.py            # Flask app for result update function
        └── Dockerfile        # Container configuration for the function
```

## Key Components

- **Data Service** (`services/data-service`)
  - Flask + SQLAlchemy REST API
  - Full CRUD for event records
  - Persists data in SQLite
  - CORS enabled

- **Workflow Service** (`services/workflow`)
  - Flask orchestration service
  - Receives event submissions from the frontend
  - Creates an initial record in the Data Service with `PENDING` status
  - Triggers the submission-event simulator (serverless-style)

- **Presentation Service** (`services/presentation`)
  - React + Material UI frontend
  - Event submission form
  - Live event list display (polling)
  - Calls backend APIs directly

- **Processing Function** (`functions/processor`)
  - Validates the payload
  - Classifies events by keywords
  - Assigns priority based on category
  - Produces a final status and note

- **Serverless-style Functions (Simulated)**
  - Submission Event: receives a submission trigger and forwards it to the processor
  - Result Update: receives processor output and patches the Data Service record

## Prerequisites

### Required

- **Python 3.11+** (recommended: 3.11 or 3.12)
- **Node.js 18+** (recommended: 18.x LTS)
- **Git**

### Optional

- **Docker & Docker Compose** (for containerized deployment)

### OS Compatibility

- **macOS** (tested)
- **Linux** / **Windows** (should work; scripts may need adjustments)

## Local Setup

### Quick Start (Recommended)

```bash
# 1. Clone the repo
git clone <your-github-repo-url>
cd campus-buzz

# 2. Run the startup script (starts all services)
./start-services.sh
```

The script will:

- Check dependencies (Python and Node.js)
- Create a Python virtual environment
- Install dependencies
- Start services (Data: 5002, Workflow: 5001, Frontend: 3000)
- Open the frontend in your browser

### Manual Start (Alternative)

If the script fails, you can start services manually.

#### 1. Environment Setup

```bash
git clone <your-github-repo-url>
cd campus-buzz

python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

#### 2. Start Data Service

```bash
cd services/data-service
python api.py
```

Service URL: `http://localhost:5002`

#### 3. Start Workflow Service

```bash
cd services/workflow
DATA_SERVICE_URL=http://localhost:5002 python main.py
```

Service URL: `http://localhost:5001`

#### 4. Start Frontend

```bash
cd services/presentation
npm install
npm start
```

Frontend URL: `http://localhost:3000`

### Quick Verification

```bash
# 1. Check if services are running
curl -s http://localhost:5001/ | head -1  # Workflow Service
curl -s http://localhost:5002/ | head -1  # Data Service

# 2. Test the submit endpoint
curl -X POST http://localhost:5001/api/submit \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Event","description":"This is a test submission to validate the pipeline end-to-end.","location":"Test Location","date":"2024-12-31","organiser":"Tester"}'

# 3. Verify records exist
curl http://localhost:5002/records | jq '.[0]'
```

### Service Ports

- **Frontend**: `http://localhost:3000`
- **Workflow Service**: `http://localhost:5001`
- **Data Service**: `http://localhost:5002`

## Service APIs

### Data Service

- `GET /`: service info
- `POST /records`: create a record (required fields: `title`, `description`, `location`, `date`, `organiser`)
- `GET /records`: list all records
- `GET /records/<id>`: get a single record
- `PATCH /records/<id>`: update `status`, `category`, `priority`, `note`

### Workflow Service

- `GET /`: service info
- `POST /api/submit`: receives submissions, creates a `PENDING` record, and triggers the submission-event simulator

## System Workflow

1. The user submits an event in the frontend.
2. Workflow Service stores an initial record in Data Service with status `PENDING`.
3. Workflow triggers the Submission Event simulator.
4. Submission Event forwards the payload to the Processor.
5. Processor evaluates and sends its decision to Result Update.
6. Result Update writes back to Data Service via `PATCH /records/<id>`.
7. The frontend polls Data Service and displays final status, category, priority, and notes.

## Event Processing Rules

- **INCOMPLETE**
  - If any required field (`title`, `description`, `location`, `date`, `organiser`) is missing or empty.
- **NEEDS REVISION**
  - If date format is not `YYYY-MM-DD`, or `description` is fewer than 40 characters.
- **APPROVED**
  - If completeness and format checks pass, the event is classified and assigned a priority.

### Keyword Category Precedence

1. `OPPORTUNITY`: matches `career`, `internship`, `recruitment`
2. `ACADEMIC`: matches `workshop`, `seminar`, `lecture`
3. `SOCIAL`: matches `club`, `society`, `social`
4. `GENERAL`: default when none match

### Priority Mapping

- `OPPORTUNITY` → `HIGH`
- `ACADEMIC` → `MEDIUM`
- `SOCIAL` → `NORMAL`
- `GENERAL` → `NORMAL`

## Payload Examples

### Workflow Service → Processing Function (via Submission Event)

```json
{
  "id": 123,
  "title": "Campus Recruitment Fair",
  "description": "A large-scale recruitment event with multiple companies and internship opportunities.",
  "location": "Main Hall",
  "date": "2024-04-20",
  "organiser": "Career Center"
}
```

### Processor Output (sent to Result Update, then written to Data Service)

```json
{
  "id": 123,
  "status": "APPROVED",
  "final_status": "APPROVED",
  "category": "OPPORTUNITY",
  "assigned_category": "OPPORTUNITY",
  "priority": "HIGH",
  "assigned_priority": "HIGH",
  "note": "Processing successful."
}
```

## Docker Compose Notes

The repository provides `docker-compose.yml` for containerizing the main services:

- `presentation`
- `workflow-service`
- `data-service`

It also reserves the callback URL environment variables `SUBMISSION_EVENT_URL` and `RESULT_UPDATE_URL` for later extension to function simulation containers.

> Note: Local development tends to be more reliable; the containerized setup may need adjustments depending on your environment (especially the `services/presentation` build).

## Publishing to GitHub

These steps assume you created an empty GitHub repository, e.g. `https://github.com/<your-username>/campus-buzz.git`.

```bash
git status
git add .
git commit -m "Update project"
git remote add origin https://github.com/<your-username>/campus-buzz.git
git push -u origin main
```

If your default branch is `master`, use:

```bash
git push -u origin master
```

## Additional Suggestions

### Extensions

- Extend processing logic in `functions/processor/logic.py`
- Expand the serverless simulators under `functions/`
- Add authentication (optional)
- Migrate from SQLite to PostgreSQL

### Container Deployment

```bash
docker-compose up --build
docker-compose up -d
```

Note: you may need to adjust service-to-service networking settings for your environment.

### Performance

- Tune SQLAlchemy configuration for higher concurrency
- Add caching (e.g. Redis)
- Add frontend code splitting and lazy loading

### Contributing

1. Fork the project
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m "Add amazing feature"`
4. Push branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## FAQ

### Startup Issues

**Q: Running `./start-services.sh` shows "command not found"**

- Ensure the script is executable: `chmod +x start-services.sh`

**Q: Python version issues or dependency installation fails**

- Check your Python version: `python3 --version`
- Ensure you are using the correct environment

**Q: Node.js not found or version too old**

- Check Node.js: `node --version`

**Q: Port already in use**

- Check port usage: `lsof -i :5001 -i :5002 -i :3000`
- Stop the process using the port or update your port configuration

### Runtime Issues

**Q: Frontend shows 504 Gateway Timeout**

- Backend services are not running or not reachable
- Check processes: `ps aux | grep -E "(python|node)"`
- Ensure Workflow Service uses the correct Data Service URL

**Q: Submitting an event has no response or shows errors**

- Ensure all required fields are provided
- Verify backend services:
  - `curl http://localhost:5001/`
  - `curl http://localhost:5002/`

**Q: Event list does not show**

- Ensure the frontend can reach the Data Service
- Verify CORS settings and network connectivity

### Debugging Tips

```bash
curl http://localhost:5001/  # Workflow Service
curl http://localhost:5002/  # Data Service
curl http://localhost:3000   # Frontend
```

### Reset Data

If you want to start fresh, delete the SQLite database file and restart the Data Service:

```bash
rm services/data-service/events.db
```

### Environment Notes

- **macOS**: virtualenv path `venv/bin/activate`
- **Windows**: virtualenv path `venv\\Scripts\\activate`
