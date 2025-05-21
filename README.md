# DeputyDev Binary

DeputyDev Binary is a Sanic-based application designed to provide various services related to code analysis, search, and management.

## Project Structure

The project is organized as follows:

```
deputydev-binary/
├── app/
│   ├── clients/
│   ├── models/
│   ├── repository/
│   ├── routes/
│   ├── services/
│   ├── utils/
│   ├── __init__.py
│   ├── listeners.py
│   ├── logging_config.py
│   └── service.py
├── .gitignore
├── pyproject.toml
├── README.md
└── uv.lock
```

## Installation

1. Clone the repository:
   ```
   git clone git@bitbucket.org:tata1mg/deputydev-binary.git
   cd deputydev-binary
   ```

2. Install dependencies:
   ```
   uv venv --python 3.11
   source .venv/bin/activate
   uv sync
   ```

## Usage

To run the application:

```
python -m app.service
```
