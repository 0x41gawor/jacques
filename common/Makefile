APP_NAME=common
PYTHON?=python3
PIP?=$(PYTHON) -m pip

.PHONY: install reinstall uninstall build clean

# -------- INSTALL --------

install:
	$(PIP) install .

reinstall:
	$(PIP) uninstall -y $(APP_NAME) || true
	$(PIP) install .

uninstall:
	$(PIP) uninstall -y $(APP_NAME)

# -------- BUILD (wheel) --------

build:
	$(PYTHON) -m build

# -------- CLEAN --------

clean:
	rm -rf build dist *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +