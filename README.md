# capstone-2022-backend

## How to run
1. Install python, pip, and postgreSQL.
2. Clone this project to your computer `git clone https://github.com/dafaath/capstone-2022-backend.git`.
3. Install depedencies with `pip install -r requirements.txt`.
4. This project use postgreSQL as database, change the database connection settings to connect to your database in `config.py`, just change the DefaultSettings properties.
5. Update your database to the latest model with Alembic (Alembic is already installed if you run the above requirements.txt) `alembic upgrade heads`.
6. Start the server with `python start.py`.
