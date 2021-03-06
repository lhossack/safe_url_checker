# Safe Url Checker

A web service for checking if urls are known to contain malware.

If you are interested in using the service, please see the [User Documentation](http://urlinfo-project-safeurlchecker-docs-sphinx-4312lkj1234.s3-website.ca-central-1.amazonaws.com)

API documentation is available at [API Documentation](http://urlinfo-project-safeurlchecker-docs-sphinx-4312lkj1234.s3-website.ca-central-1.amazonaws.com/#api-documentation)

The rest of this document is brief notes for developers improving or extending this project, or operators interested in customizing the behaviour or deployment environment (e.g. deploying to AWS lambda instead of flask on ECS).

## Getting Started Developing
### Architecture/ Design and Important Files
The project architecture is based on hexagonal (ports & adaptors) style architecture.
The central component is the urlchecker.UrlChecker object, which handles the core logic for handling a request.
That is, it ensures all registered databases have been checked before returning a response.

The configuration object is also of significant note as it plays a key role during startup.

The API frameworks (flask) are intended to play a minimal role in the execution or control flow of the business logic and should be kept separate in case they are to be swapped out. This could happen for example if there was a decision to change to using a serverless model such as AWS Lambda.

Similarly, the backing stores are responsible for ensuring inputs are not dangerous to their own systems (e.g. SQL injection due to lack of parameterized queries) and must obey the "interface" defined by database_abc.DatabaseABC to be registered to the app.

### Using the Makefile
If you have make installed, there are make commands available for most common operations.

The makefile runs all operations using a virtual environment, and creates one if it doesn't exist or can't be found.
It also ensures all dependencies in the virtual environment are up to date before each command.

The makefile should be able to run from any directory using:
`make -f ../path/to/Makefile <target>`
however it has only been tested on Ubuntu20.04 in bash. If it is not working for you, there 
are a couple configuration variables that you can set to match your environment:
- `GLOBALPYTHON`: May need to be set if python3 is not the interpretter you want to use or is not in your path.
- `MAKEPATH`: May need to be set to the project root directory in the case the `shell` command doesn't work in your environment.
- `VENV`: Will need to be set if you configured a virtual environment in a different location.

#### Makefile commands
`make init` to initialize and install a virtual environment. 
Note that this does not activate the venv in your current shell. 

`make test` run test discovery (all unit and integration tests)

`make validate URLINFO_SERVER=http://localhost:5000` to run validation tests against the endpoint at http://localhost:5000 (enter the server to validate)

`make devserver` to run the flask development server

`make build` to generate a build package (docker image)

`make prodserver` to generate a build package consisting of a sample server linked to mongo and dbm.

`make docs` to build the sphinx documentation (html)

### Manually setting up your virtual environment
It is recommended that you work in a virtual environment to keep project dependencies separated.
See the section below on "Using virtual environments" if you are unfamiliar with virtual environments.
The commands below assume:
- you have installed the required dependencies (or they are available on your sys.path)
- that your python interpretter is on your path, named `python3`, and
- that you are in the project root directory (safe_url_checker/)

### Running unit and integration tests
Unit and integration tests are defined in `tests` and are in the files named like "test_*".

You can run them individually by running them directly. E.g:
```
$ cd test
$ python3 test_urlchecker.py
```

Or you can run them all using test discovery:
```
$ python3 -m unittest -s tests/
```

### Building the sphinx documentation
Sphinx documentation sources are in `docs/source`

You can build them like this:
```
cd docs
sphinx-build -b html source/ build/html
```

And access your newly built docs by navigating to 
`docs/build/source/html/index.html` in your browser.

### Running the Development Server
To run the dev server (flask) in development mode:

```
export FLASK_APP="flask_frontend:create_app"
export FLASK_ENV=development
.venv/bin/flask run
```

This will allow you to use flask's debug features in the browser and on the command line.
To learn more, visit the flask documentation.


### Connecting urlinfo to MongoDB instances:
Note: If your configuration file defines mongo databases, to access them from the development server, export the connection environment variables also:

```
export MONGO_URI_22='mongodb://localhost:27017/' &&\
export MONGO_USERNAME_22='root' &&\
export MONGO_PASSWORD_22='example' &&\
```

These are the example environment variables. Check your configuration file to to see which environment variables you need to modify.

Please see the ["Configuration Docs"](http://urlinfo-project-safeurlchecker-docs-sphinx-4312lkj1234.s3-website.ca-central-1.amazonaws.com#configuration) for more information about the configuration file.

### Running the Sample Production Server/ Building a docker image
Note: Please see ["Deployment Quickstart" and "Deployment - Advanced"](http://urlinfo-project-safeurlchecker-docs-sphinx-4312lkj1234.s3-website.ca-central-1.amazonaws.com#deployment-quickstart) for information regarding what should be customized for a docker build.

To run build and run the sample production server, make is the easiest way to deploy:
```make prodserver```

The server will be available at localhost:8000.

Otherwise, you can use docker-compose:

```
docker-compose build
docker-compose up -d
python3 sample_resources/load_unsafe_urls.py
```

### Running Validation Tests
Validation tests are stored in tests_validation and require some setup.

First, a server must be running, and that server is required to have either copies of or access to the sample_resources dbm databases and access and configuration for any mongodb instances. These databases contain URLs which are tested against for validation.

The server must be running to run the validation tests against it. Running the flask development server as described in 
"Running the Sample Production Server" above, with `URLINFO_CONFIG` unset or pointing to 
`../sample_resources/default_config.json` will cause it to acquire the required sample databases.

Prepare a separate shell to run the validation tester by navigating to the project root and activating your virtual environment.

There is an environment variable to set in the 'validation test' shell when running the validation tests:

   - `URLINFO_SERVER` defines the server's location. It must include schema, host and port. e.g. `http://localhost:5000` with no trailing '/'. This should be exported in the shell that the validation tests are being run from.

In the validation shell, run: 

```make validate URLINFO_SERVER=http://localhost:5000``` 

or manually,

```
export URLINFO_SERVER=http://localhost:5000
python3 tests_validation/test_server.py
```


## Release Process
For a release to go to test:
- All code changes need to go through final review before being merged.
- All unit and integration tests must be passing. #TODO automate these checks in CI
- All documentation must be up to date and building, including version information.
- All end to end tests must be passing on sandbox environments.
- #TODO: Static analysis tools are not yet incorporated into the workflow, but they will also be required to pass

Once in test, manual and end to end tests must pass before being released.

This product is not operated by the developer. For discussion regarding deployment
configuration and options, please see the [User Documentation](http://urlinfo-project-safeurlchecker-docs-sphinx-4312lkj1234.s3-website.ca-central-1.amazonaws.com/).


## Release History
Please see CHANGELOG.md

## Contributing
If you would like to contribute, please feel free to fork and create a pull request, submit an issue via github, or otherwise participate.

## Customization for deployment scenarios
Frameworks and databases are implemented as adaptors so that new adaptors can easily replace old ones.
If you intend to deploy this to AWS lambda, for example, you can create a new entry point (handler) for lambda 
to replace the flask one.
You can also use any database or database service by creating an adaptor for it by subclassing database_abc.DatabaseABC and registering it to the urlchecker instance.

## Using virtual environments

To initialize a virtualenv on a *nix based OS:

```
$ python3 -m venv .venv
```

After venv initialization, activate your venv using:

```
$ source .venv/bin/activate
```

On Windows, activate venv like this:

```
% .venv\Scripts\activate.bat
```

To install required dependencies, run this command:

```
$ pip install -r requirements.txt
```

To add additional dependencies, add them to the `setup.py` file and 
rerun the `pip install -r requirements.txt` command.
