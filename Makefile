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

all: init test docs build

init: ${MAKEPATH}/requirements.txt
	@echo "\nInitializing Environment"
	${GLOBALPYTHON} -m venv ${VENV}
	cd ${MAKEPATH} && ${VENV}/bin/pip install -r ${MAKEPATH}/requirements.txt && cd -

test: init
	@echo "\nRunning Unit Tests"
	${VENV}/bin/python3 -m unittest discover -s ${MAKEPATH}/tests || true

validate: init
	@echo "\nRunning Unit Tests"
	${VENV}/bin/python3 -m unittest discover -s ${MAKEPATH}/tests_validation || true

devserver: init
	@echo "\nStarting development server"
	export MONGO_URI_22='mongodb://localhost:27017/' &&\
	export MONGO_USERNAME_22='root' &&\
	export MONGO_PASSWORD_22='example' &&\
	export FLASK_APP="flask_frontend:create_app" &&\
	export FLASK_ENV='development' &&\
	${VENV}/bin/flask run

build: init
	@echo "\nGenerating build"
	docker build -t urlinfo ${MAKEPATH}

prodserver: init
	@echo "\nRunning Sample Prod server"
	docker-compose build &&\
	docker-compose up -d &&\
	${VENV}/bin/python3 sample_resources/load_unsafe_urls.py
	@echo "You can access the sample production API at http://localhost:8000/urlinfo/1/"
	@echo "Example usage (non malicious url): http://localhost:8000/urlinfo/1/www.facebook.com:443/messages/t/62132"
	@echo "Example usage (malicious url): http://localhost:8000/urlinfo/1/evil.com:80"

docs: init
	@echo "\nGenerating docs"
	cd ${MAKEPATH}/docs && ${VENV}/bin/sphinx-build -b html source/ build/html

clean:
	@echo 'Warning! This target can be dangerous depending on your configuration.'
	@echo 'It is disabled for now. Please verify your config.'
	@echo 'MAKEPATH='${MAKEPATH}
	# rm -rf ${VENV}
	# find ${MAKEPATH} -type f -name '*.py[co]' -delete
	# find ${MAKEPATH} -type d -name '*.egg-info' -delete
	# find ${MAKEPATH} -type d -name '__pycache__' -delete
	# @echo 'Add build artifact & docs cleanup'

.PHONY: all init devserver prodserver test build docs clean