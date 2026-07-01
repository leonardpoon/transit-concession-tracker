# Running The CLI Anywhere

This project can use TiDB as the shared database from any computer. The main
thing to remember is that the CLI still runs on the computer you are using.
TiDB is the shared backend that keeps the data in one place.

Render and Vercel are not a good fit for hosting this as an interactive terminal
program. They are better for web apps, APIs, scheduled jobs, and dashboards.

## Recommended Path

Use GitHub for the code and TiDB for the data.

On each computer:

1. Clone the repo:

   ```text
   git clone <your-repo-url>
   cd transit-concession-tracker
   ```

2. Create a virtual environment:

   ```text
   python -m venv venv
   ```

3. Activate it:

   Windows:

   ```text
   venv\Scripts\activate
   ```

   macOS/Linux:

   ```text
   source venv/bin/activate
   ```

4. Install dependencies:

   ```text
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Copy `.env.example` to `.env` and fill in your TiDB values:

   ```text
   DB_HOST=...
   DB_PORT=4000
   DB_USER=...
   DB_PASSWORD=...
   DB_NAME=transit_tracker
   DB_SSL=true
   ```

6. Test the connection:

   ```text
   python test_connection.py
   ```

7. Run the CLI:

   ```text
   python main.py
   ```

The first startup creates/migrates the database schema if needed. Trips and
concession periods live in TiDB, so each computer sees the same data.

## Packaged CLI Executable

You can also build a Windows executable with PyInstaller. This is useful if you
want to run the tracker on another Windows computer without manually activating
a virtual environment.

On the build computer:

```text
build_cli.bat
```

The executable will be created under:

```text
dist\transit-tracker\transit-tracker.exe
```

Before running it on another computer, place a filled `.env` file beside
`transit-tracker.exe`:

```text
dist\transit-tracker\.env
```

Then double-click `transit-tracker.exe` or run it from Command Prompt. The
executable still connects to TiDB, so your trips remain shared across machines.

Notes:

- Do not commit the filled `.env` file.
- Build Windows executables on Windows. Build macOS/Linux executables on those
  platforms if you need them later.
- The packaged CLI is separate from `dashboard.py`; dashboard dependencies are
  intentionally excluded from the executable.

### Single-file executable with embedded `.env`

If you want only one file to move around, you can build an executable that
embeds the current `.env` file:

```text
build_cli_with_env.bat
```

This creates:

```text
dist\transit-tracker.exe
```

Important: this puts your TiDB host, username, and password inside the
executable. Treat that `.exe` like a secret. Do not upload it publicly or send
it to anyone you do not trust. If the TiDB password changes later, rebuild the
executable so it contains the new `.env` values.

## Where Render Fits

Render is useful if you decide to host a web dashboard or an API, for example:

- `dashboard.py` as a Streamlit service.
- A future FastAPI backend.
- A scheduled backup/export job.

It is not useful for the interactive `main.py` menu, because hosted services do
not expose a normal terminal UI to you as the app interface.

## Optional Dashboard Hosting

If you want browser-only reporting later, deploy `dashboard.py` to a Python web
host such as Streamlit Community Cloud, Render, Railway, or Fly.io.

Use:

```text
dashboard.py
```

as the entrypoint and:

```text
requirements.txt
```

for dependencies. Add these environment variables in the host dashboard:

```text
DB_HOST
DB_PORT
DB_USER
DB_PASSWORD
DB_NAME
DB_SSL=true
```

## If You Want Vercel

Vercel is a good choice if we convert the app to a web/API architecture:

- A small FastAPI backend exposes endpoints for trips, summaries, and
  concession periods.
- A Vercel-hosted frontend calls those endpoints.
- TiDB credentials are stored as Vercel environment variables.

That is a proper rewrite of the terminal menus into web routes/forms, not a
simple upload of `main.py`.
