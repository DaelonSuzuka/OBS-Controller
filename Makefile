# **************************************************************************** #
# General Make configuration

# This suppresses make's command echoing. This suppression produces a cleaner output. 
# If you need to see the full commands being issued by make, comment this out.
MAKEFLAGS += -s

# Fix bad built-in make behaviors
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

# Use > instead of \t
.RECIPEPREFIX = >

# **************************************************************************** #

# load the pypi credentials
ifneq (,$(wildcard .env))
include .env
# export them for twine
export
endif

# **************************************************************************** #

APP_FOLDER := src
APP_NAME := stagehand
APP_MAIN := $(APP_FOLDER)/$(APP_NAME)/__main__.py

# **************************************************************************** #
# Development Targets

# run the application
run: venv
> $(VENV_PYTHON) $(APP_MAIN)

# run the application in pdb
debug: venv
> $(VENV_PYTHON) -m pdb $(APP_MAIN)

#
build:
> uv build

#
publish:
> twine upload dist/* -u __token__

#
reload:
> -pipx uninstall stagehand
> pipx install . -e

# ---------------------------------------------------------------------------- #

PORTABLE_FLAG := $(APP_FOLDER)/.portable

# create the portable flag folder
portable:
> mkdir "$(PORTABLE_FLAG)"

# remove the portable flag folder
non_portable:
> $(RM) "$(PORTABLE_FLAG)"

# **************************************************************************** #
# Utility Targets

# open the qtawesome icon browser
qta: venv
> $(VENV)/qta-browser

obs: venv
> $(VENV_PYTHON) app/plugins/obs_core/gen.py

# build all the plugins into zips
plugins: venv
> $(VENV_PYTHON) tools/plugins.py build

install_plugins: venv
> $(VENV_PYTHON) tools/plugins.py install

clean_plugins: venv
> $(VENV_PYTHON) tools/plugins.py clean

# **************************************************************************** #
# Build Targets

# build a self-contained onefile executable 
onefile: venv plugins
> $(VENV_PYINSTALLER) -y onefile.spec

# build a one folder bundle 
bundle: venv plugins
> $(VENV_PYINSTALLER) -y bundle.spec

# run the bundled executable
run_bundle:
ifeq ($(OS),Windows_NT)
> dist/$(AppName)/$(AppName).exe
else
> dist/$(AppName)/$(AppName)
endif

# **************************************************************************** #
# Release Targets

# wrap the bundle into a zip file
zip:
> $(PYTHON) -m zipfile -c dist/$(AppName)-$(AppVersion)-portable.zip dist/$(AppName)/

# remove the various build outputs
clean:
> -@ $(RM) build
> -@ $(RM) dist

# **************************************************************************** #
# python venv settings
VENV_NAME := .venv
REQUIREMENTS := requirements.txt

VENV_DIR := $(VENV_NAME)
PYTHON := python

ifeq ($(OS),Windows_NT)
	VENV := $(VENV_DIR)/Scripts
else
	VENV := $(VENV_DIR)/bin
endif

VENV_CANARY_DIR := $(VENV_DIR)/canary
VENV_CANARY_FILE := $(VENV_CANARY_DIR)/$(REQUIREMENTS)
VENV_TMP_DIR := $(VENV_DIR)/tmp
VENV_TMP_FREEZE := $(VENV_TMP_DIR)/freeze.txt
VENV_PYTHON := $(VENV)/$(PYTHON)
VENV_PYINSTALLER := $(VENV)/pyinstaller
RM := rm -rf 
CP := cp

# Add this as a requirement to any make target that relies on the venv
.PHONY: venv
# venv: $(VENV_DIR) $(VENV_CANARY_FILE)
venv: $(VENV_DIR)

# Create the venv if it doesn't exist
$(VENV_DIR):
> uv venv

# Update the venv if the canary is out of date
$(VENV_CANARY_FILE): $(REQUIREMENTS)
> uv pip install -r $(REQUIREMENTS)
> -$(RM) $(VENV_CANARY_DIR)
> -mkdir $(VENV_CANARY_DIR)
> -$(CP) $(REQUIREMENTS) $(VENV_CANARY_FILE)

# forcibly update the canary file
canary: $(VENV_CANARY_DIR)
> -$(RM) $(VENV_CANARY_DIR)
> -mkdir $(VENV_CANARY_DIR)
> $(CP) $(REQUIREMENTS) $(VENV_CANARY_FILE)

# update requirements.txt to match the state of the venv
freeze_reqs: venv
> $(VENV_PYTHON) -m pip freeze > $(REQUIREMENTS)

# try to update the venv - expirimental feature, don't rely on it
update_venv: venv
> uv pip sync $(REQUIREMENTS)
> -$(RM) $(VENV_CANARY_DIR)
> -mkdir $(VENV_CANARY_DIR)
> -$(CP) $(REQUIREMENTS) $(VENV_CANARY_FILE)

# remove all packages from the venv
clean_venv:
> $(RM) $(VENV_CANARY_DIR)
> mkdir $(VENV_TMP_DIR)
> uv pip freeze > $(VENV_TMP_FREEZE)
> uv pip uninstall -y -r $(VENV_TMP_FREEZE)
> $(RM) $(VENV_TMP_DIR)

# clean the venv and rebuild it
reset_venv: clean_venv update_venv
