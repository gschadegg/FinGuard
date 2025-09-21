This is the persistence layer documentation for FinGuard built with PostgresSQL, Docker, and sqlAlchemy.

All Models and Repositories are located at: `/backend/infrastructure`

## Initial Local Setup

To create a new local dev database environment run the following commands:

- `cd backend`
- `pnpm run init-setup`

The `init-setup` script will automatically run the following scripts that sets up the backend and database:

- Creates venv: `pnpm run venv:create`
- Install dependencies: `pnpm run req:install`
- Spins up local DB docker container: `pnpm run db:up`
- Applies Models to DB SQL tables: `pnpm run migrate:up`
- Seeds mock data: `pnpm run seed`
- Spins up API dev: `pnpm run dev`

### Running Local Database

Once the initial setup has been completed, the local database can be started with the following script: `pnpm run db:up`

### Shutting Down Local Database

Once running, the local database can be shut down with the following script: `pnpm run db:down`

### View Local Database

Once the local database is running, it can be viewed at `http://localhost:5050`. With the pgAdmin login information found in the `docker-compose.yml` file.

- pgAdmin email: admin@example.com
- pgAdmin password: admin

#### Register Server

On initial setup and after any database resets, the server will need to be registered with the following information from within the pgAdmin view in order to view data tables:

- Host: db
- Port: 5432
- DB: appdb
- Username / Password: app / app

## Updating Database Models

When there have been changes to the SQL models located at `/backend/infrastructure/db/models`, the database tables need to be updated by running the following scripts:

- Generates new version in `alembic/versions`: `pnpm run migrate:make`
- Applies Models to DB SQL tables: `pnpm run migrate:up`

## Resetting Local Database

To clean out local database and it's data volumes run the following scripts:

- Shuts down, deletes volumes, and spins up new docker container: `pnpm run db:reset`
- Applies Models to DB SQL tables: `pnpm run migrate:up`
- Seeds mock data: `pnpm run seed`

## Tech Stack

Using Plaid API Sandbox data exclusively.

|             |                    |
| ----------- | ------------------ |
| PostgresSQL | Database           |
| SQLAlchemy  | ORMapper & Toolkit |
| Docker      | Containerization   |
