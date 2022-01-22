# These utility scripts require make to be installed. 
# They should be able to run from anywhere using 
# make -f <path/to/this/Makefile> [<target>]

# Tested on ubuntu 20.04 with python3
# Requires python3 and pip.

# The following global makefile variables may need to be configured for your environment.
# To override these, export the corresponding environ var prior to calling make
# or call make with environment arguments like: 
# $ make <command> -e GLOBALPYTHON=python3 to override

# Path to global python3 interpreter to use for venv generation (or command if in ${PATH})
GLOBALPYTHON ?= python3

# Path to this Makefile's parent directory. '.' is sufficient if caled from the same directory
MAKEPATH ?= $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

# Path to the location you wish the virtual environment to be created
VENV ?= ${MAKEPATH}/.venv

all: init build docs

init: ${MAKEPATH}/requirements.txt
	@echo "\nInitializing Environment"
	${GLOBALPYTHON} -m venv ${VENV}
	cd ${MAKEPATH} && ${VENV}/bin/pip install -r ${MAKEPATH}/requirements.txt && cd -

test: init
	@echo "\nRunning Unit Tests"
	${VENV}/bin/python3 -m unittest discover -s ${MAKEPATH}/tests || true

devserver: init
	@echo "\nStarting development server"
	@echo 'make devserver not yet implemented - should run flask dev server'

build: init
	@echo "\nGenerating build"
	@echo 'make  build not yet implemented - to build packages in setup.py'

docs: init
	@echo "\nGenerating docs"
	cd docs && ${VENV}/bin/sphinx-build -b html source/ build/html

clean:
	@echo 'Warning! This target can be dangerous depending on your configuration.'
	@echo 'It is disabled for now. Please verify your config.'
	@echo 'MAKEPATH='${MAKEPATH}
	# rm -rf ${VENV}
	# find ${MAKEPATH} -type f -name '*.pyc' -delete
	# find ${MAKEPATH} -type d -name '__pycache__' -delete
	# @echo 'Add build artifact & docs cleanup'

.PHONY: all init devserver test build docs clean