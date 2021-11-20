# CV Generator
## Create superuser
```bash
python manage.py createsuperuser
```
## Running celery worker
```bash
celery -A cv_generator worker -l info
```

## Table of Contents
* [Development Setup](#development-setup)
    * [Prerequisites](#prerequisites)
    * [Initial Setup](#initial-setup)
    * [Running with docker](#running-project-with-docker)

## Development Setup

### Prerequisites
---------------------
- python >= 3.8
- Git
- Virtualenv

### Initial Setup
---------------------
- Clone main repository locally.
```
    $ git clone git@github.com:Prateena/cv_generator.git
    $ cd cv_generator
```

- Create a virtualenv
```
    $ virtualenv venv --python=python3.8
    $ source venb/bin/activate
```

on Windows,
```
    > env\Scripts\activate
```

- install development dependencies.
```
   $ pip install -r requirements.txt
```


- Copy .env.example to .env in root directory of the project
```
    $ cp .env.example .env
```
 > Note: Make sure you have required values in .env file before development.
## Running project with docker
### Prerequisites
---------------------
- docker
- docker-compose

### Running project
```
    $ docker-compose up
```

### Stopping project
```
    $ docker-compose down
```

&nbsp;
