# Scanning Task for Scanner Engineer position

## Setup

1. [Install Poetry](https://python-poetry.org/docs/#installation)
2. Install project dependencies with `poetry install`
3. Create `.env` file in repo root or export environment variables into shell

```env
# Note: functionality was tested with primary credentials/account, i.e. Dave Worker
IDENTITY_USERNAME=Dave Worker
EMAIL=
PASSWORD=
SECRET_ANSWER=
PORTAL_LINK=https://www.upwork.com/ab/account-security/login
```

4. Easily run with `make scanner-go`
5. Estimated time per run: 45 seconds
6. Check Makefile for other options
7. Pay attention to `results/` directory and terminal output.
