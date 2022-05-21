# Emo Diary API

## Documentation

You have multiple option for the documentation, all of the option below is a substitute for each other, feel free to use whichever you prefer:

- You can run the app on localhost and:
  - Go to /docs to see a swagger documentation
  - Go to /redoc to see a redoc documentation (Alternative to swagger)
- You can directly go to below url:
  - `https://emodiary-bangkit.et.r.appspot.com/docs` see a swagger documentation
  - `https://emodiary-bangkit.et.r.appspot.com/redoc` see a redoc documentation (Alternative to swagger)
- [Postman public workspace](https://www.postman.com/dafaathaullah/workspace/emodiary/overview)

## How to run

1. Install python 3.9, pip, and postgreSQL.
2. Clone this project to your computer `git clone https://github.com/dafaath/capstone-2022-backend.git`.
3. Install pipenv to handle your environment, `pip install pipenv`
4. Install dependencies with `pipenv install` and enter the environment `pipenv shell`.
5. This project use postgreSQL as database, change the database connection settings to connect to your database in `config.py`, just change the DefaultSettings properties.
6. Update your database to the latest model with Alembic (Alembic is already installed if you install the above dependencies) `alembic upgrade heads`.
7. Start the server with `python start.py`.
