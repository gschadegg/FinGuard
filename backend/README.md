This is the service layer for FinGuard built with FastAPI & Python

## Setup

_uses pnpm for easy access scripts_

- Install dependencies running the following scripts:
  - `cd backend`
  - `pnpm install --frozen-lockfile`
  - `pnpm run install-deps`

##### Additional Scripts Available

- Activate python env: `pnpm run activate`
- Deactivate python env: `pnpm run deactivate`
- Recreate requirements.txt file: `pnpm run req-freeze`
- Linting: `pnpm run lint`

#### Running

- Dev Server: `pnpm run dev`

#### Testing

- Unit & Module Tests `pnpm run test`
- Postman Tests: `pnpm run postman-test`

## Tech Stack

Using Plaid API Sandbox data exclusively.

|           |                       |
| --------- | --------------------- |
| FastAPI   | Framework             |
| PyTest    | Unit & Module testing |
| Postman   | System testing        |
| Plaid API | Transactional Data    |
