# A simple example using FastAPI

# Functionalities

* Create a partner
* Load partner by id
* Search partner

# HOW TO

## Run locally

The steps bellow work for Linux/Windows environmets. But when running in Windows
after installl the requirements you need to add to PATH the pytest and uvicorn
binaries.

**Pre-requirements**
* git
* python 3.8
* pip
* docker

1. Clone this repository and cd into it
    ```
    $ git clone https://github.com/johannesssf/fastapi-example.git
    ```
1. Install the project requirements (sugestion: use virtual env)
    ```
    $ pip install -r requirements.txt
    ```
1. Start a mongo Docker container or a local server
    ```
    $ docker run -d --rm -p 27017:27017 mongo
    ```
1. (Optional) run the tests
    ```
    $ cd partner_app/tests
    $ pytest -sv
    ```
1. Start the application from project root
    ```
    $ uvicorn partner_app.main:app
    ```
1. The auto-generated documentation can be found at
    ```
    http://localhost:8000/redoc
    ```

### Points of improvement

* Create a generic way to get the database connection
* The tests should have a separated database
* Improvements on database use, like authentication and access
