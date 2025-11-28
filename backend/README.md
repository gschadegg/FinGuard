This is the service layer for FinGuard built with FastAPI & Python

_Note: the setup here focuses on local dev env for the API and DB, for Docker setup view the [root level README](../README.md)_

## Setup

_uses pnpm for easy access scripts_

### API & Database local Environment

To create a new local dev database and API environment run the following commands:

- `cd backend`
- `pnpm run init-setup`

_This will create local .venv, install py dependencies, start local db and run alembic migrations, seed the DB, and start the API_

If you only need to install dependencies, run the following scripts:

- `cd backend`
- `pnpm install --frozen-lockfile`
- `pnpm run req:install`

#### Running

Running after setup (if init-setup has been previously ran):

- Start DB: `pnpm run db:up`
- Start API: `pnpm run dev`

_API will be available at http://localhost:8000_

### ML local Environment

_Env so ML model jupiter notebooks can be ran and model retrained_

To create ML env, install dependencies and register as a kernal, run the following commands:

- `cd backend`
- `pnpm run init-setup:ml`
- In VS Code, navigate to jupiter notebook files in `backend/fraud-detection` folder
- Select `Select Kernal` in top right, select `Jupiter kernal...` and then click the refresh icon
- Select `FinGuard-ML` (.venv-ml) environment

_Note: synthetic data needs to be created by running the notebook file `Synthetic-Data-Creation` before being able to run `Fraud-Detection-Model-final` to re-train and create the Fraud Detection model._

##

##### Additional Scripts Available

- Recreate requirements.txt file: `pnpm run req:freeze`
- Recreate requirements-ml.txt file: `pnpm run req:freeze:ml`

#### Activating Env

- API Env: `.venv\Scripts\activate`
- ML Env: `.venv-ml\Scripts\activate`

#### Open Swagger Docs

Run `pnpm run dev` and visit `http://localhost:8000/docs`

#### Testing

- Unit & Module Tests `pnpm run test`
- With Coverage `pnpm run test:coverage`

#### QA & Metrics

- Linting: `pnpm run lint`
- Auto-fix lint and formatting issues: `npm run lint:fix`

- Security Scan: `npm run qa:security`
- Complexity Report: `npm run qa:complexity`
- Maintainability Report: `npm run qa:maintainability`
- Raw Metics (LOC, LLOC, SLOC): `npm run metrics:raw`

## Tech Stack

Using Plaid API Sandbox data exclusively.

|           |                       |
| --------- | --------------------- |
| FastAPI   | Framework             |
| PyTest    | Unit & Module testing |
| Plaid API | Transactional Data    |
