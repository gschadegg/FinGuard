# FinGuard

personal finance management with real time fraud detection

## Setup

To setup the

- Clone monolith repository from Github
- Go to the Frontend doc and complete it's [setup instructions](./frontend/README.md#setup)
- Go to the Backend doc and complete it's [setup instructions](./backend/README.md#setup). This will setup the Backend service layer as well as the local database.

## Additional Notes

For Frontend information and notes visit the [directory's README](./frontend/README.md).

For Service information and notes visit the [directory's README](./backend/README.md).

For Database information and notes visit the [directory's README](./database/README.md).

## Scripts Available at Root Directory

_Scripts are ran at repo root level_

- Run Frontend & Service devs in tandem: `pnpm run dev`
- Run Frontend & Service unit tests in tandem: `pnpm run test`

## Creating Plaid Connections

All endpoints and data usage from Plaid are from the sandbox environment. When creating a Connection Item that links a financial account here is the login information to use:

- username: _user_good_
- password: _pass_good_
- 2FA: _1234_
