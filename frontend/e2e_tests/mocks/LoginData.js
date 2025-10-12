const LoginSuccessMockData = {
  access_token:
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhQGIuY29tIiwidWlkIjoxLCJpYXQiOjE3NjAyOTUwMzMsImV4cCI6MTc2MDI5NTkzM30.51m9j5VrWLW0MWquLjLf6O0OWur9eydVSQPHNfG0KQY',
  token_type: 'bearer',
  user: {
    id: 1,
    email: 'a@b.com',
    name: 'Alice',
  },
}

const LoginFailInvalidCredentials = { detail: 'Invalid email or password' }
