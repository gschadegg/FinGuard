# FinGuard

personal finance management with real time fraud detection

## Setup

There are two main ways to run FinGuard:

- **Local development** (separate frontend & backend processes)
- **Docker environment** (runs containerized system)

#### Prerequisites

- Clone monolith repository from Github
- Install [pnpm](https://pnpm.io/installation)
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop)

#### Local Dev Setup

Use for working on the code / hot reloading:

- Go to the Frontend doc and complete it's [setup instructions](./frontend/README.md#setup)
- Go to the Backend doc and complete it's [setup instructions](./backend/README.md#setup). This will setup the Backend service layer as well as the local database.

After setup, you can:

- Run the frontend dev server from `./frontend`
- Run the backend dev server from `./backend`

_Details for those commands live in their respective READMEs_

#### Docker Setup

Use for running system e2e:

- For Initial setup: (at root level) run `pnpm run docker:up:setup` _this will build and start the db, api, and frontend. It will run the alembic migrations in the container_

  - Once complete, you can access the system at:
    - Frontend: http://localhost:3000
    - Backend API: http://localhost:8000
    - Backend API docs(swagger): http://localhost:8000/docs
    - pgAdmin: http://localhost:5050

- To spin up container after initial setup: (at root level) run `pnpm run docker:up`

##### Other commands

run at root level:

- Stop container: `pnpm run docker:down`
- Reset container:

```
    pnpm run docker:db:reset
    pnpm run docker:backend:migrate
    pnpm run docker:backend:seed
```

## Additional Notes

For Frontend information and notes visit the [directory's README](./frontend/README.md).

For Service information and notes visit the [directory's README](./backend/README.md).

For Database information and notes visit the [directory's README](./database/README.md).

## Creating Plaid Connections

All endpoints and data usage from Plaid are from the sandbox environment. When creating a Connection Item that links a financial account here is the login information to use:

- username: _user_good_
- password: _pass_good_
- 2FA: _1234_
