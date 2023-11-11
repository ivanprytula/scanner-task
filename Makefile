ifeq ($(VIRTUAL_ENV),)
	# Not running inside a virtual environment
	PREFIX = poetry run
else
	# Running inside a virtual environment
	PREFIX =
endif


# -------------------------------------------------------------------------------------------------------------
# Project's commands (local setup)
# -------------------------------------------------------------------------------------------------------------
# NOTE: It's OK if for some targets 'make' shows an unclear error:
# make: [Makefile:15: lint-check] Error 1 (ignored)
# Reason: 'make' throws an error in response to non-zero exit of any commands that we run as Makefile’s targets
# To mitigate this, we use `-` symbol to prefix the command or, if it's possible, add extra options to them
# -------------------------------------------------------------------------------------------------------------

lint-check:
	$(PREFIX) ruff check --exit-zero .

lint-fix:
	$(PREFIX) ruff check --fix --exit-zero .

fmt-check:
	-$(PREFIX) ruff format --check .

fmt-fix:
	-$(PREFIX) ruff format .

basics:
	$(PREFIX) python basics.py


play-codegen:
	poetry run playwright install
	poetry run playwright codegen https://www.upwork.com/ab/account-security/login

codegen-upwork-login-save-auth:
	poetry run playwright codegen https://www.upwork.com/ab/account-security/login --save-storage=auth.json

codegen-upwork-reuse-auth:
	poetry run playwright codegen --load-storage=auth.json https://www.upwork.com/ab/account-security/login

# --------------------------------------------------------------------------------------
# Project's commands (Docker setup)
# --------------------------------------------------------------------------------------
