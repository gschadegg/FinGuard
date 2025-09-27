This is the service layer for FinGuard built with FastAPI & Python

## Setup

_uses pnpm for easy access scripts_

To create a new local dev database and API environment run the following commands:

- `cd backend`
- `pnpm run init-setup`

To install dependencies running the following scripts:

- `cd backend`
- `pnpm install --frozen-lockfile`
- `pnpm run req:install`

##### Additional Scripts Available

- Recreate requirements.txt file: `pnpm run req:freeze`

#### Running

- Dev Server: `pnpm run dev`

#### Open Swagger Docs

Run `pnpm run dev` and visit `http://localhost:8000/docs`

#### Testing

- Unit & Module Tests `pnpm run test`
- Postman Tests: `pnpm run postman:test`

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
| Postman   | System testing        |
| Plaid API | Transactional Data    |
