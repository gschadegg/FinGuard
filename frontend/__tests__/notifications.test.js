import React from 'react'
import '@testing-library/jest-dom'

import { render, screen, fireEvent } from '@testing-library/react'
import { NotificationCard } from './../components/notification'

import {
  NotificationProvider,
  useNotify,
  useNotifications,
} from '@/components/notification/NotificationProvider'

function renderCard(partial = {}, onClose = jest.fn()) {
  const notice = {
    id: 'notice1',
    type: 'success',
    title: 'OK',
    message: 'Action was successful',
    duration: 1000,
    ...partial,
  }
  const utils = render(<NotificationCard notice={notice} onClose={onClose} />)
  return { notice, onClose, ...utils }
}

beforeEach(() => {
  jest.useFakeTimers()
})

afterEach(() => {
  jest.runOnlyPendingTimers()
  jest.useRealTimers()
  jest.clearAllMocks()
})

/* TC-NOTIFY-CARD-001: Success Notification */
test('Success Message', () => {
  renderCard({ type: 'success', title: 'Success Title', message: 'Action was successful' })

  expect(screen.getByText('Success Title')).toBeInTheDocument()
  expect(screen.getByText('Action was successful')).toBeInTheDocument()
})

/* TC-NOTIFY-CARD-002: Notification with no message or title */
test('empty message and title does not render alert', () => {
  renderCard({ type: 'success', title: '', message: '' })
  expect(screen.queryByRole('status')).not.toBeInTheDocument()
})

/* TC-NOTIFY-CARD-003: Notification with message and title = null */
test('null message and title does not render alert', () => {
  renderCard({ type: 'success', title: null, message: null })

  expect(screen.queryByRole('status')).not.toBeInTheDocument()
})

/* TC-NOTIFY-CARD-004: Error Notification  */
test('Error Message', () => {
  renderCard({ type: 'error', title: 'Error', message: 'Action was unsuccessful' })

  expect(screen.getByText('Error')).toBeInTheDocument()
  expect(screen.getByText('Action was unsuccessful')).toBeInTheDocument()
})

/* TC-NOTIFY-CARD-005: Info Notification  */
test('Info message', () => {
  renderCard({ type: 'info', title: 'Info', message: 'Info on Action' })

  expect(screen.getByText('Info')).toBeInTheDocument()
  expect(screen.getByText('Info on Action')).toBeInTheDocument()
})

function Scenario() {
  const notify = useNotify()
  const { notices, remove } = useNotifications()

  const handleNotify = () => notify({ type: 'success', title: 'OK', message: 'was a success' })

  const handleRemoveFirst = () => {
    if (notices[0]) remove(notices[0].id)
  }

  return (
    <>
      <button onClick={handleNotify}>notify</button>
      <button onClick={handleRemoveFirst}>remove-first</button>

      <div data-testid="count">{notices.length}</div>
      <div data-testid="first-id">{notices[0]?.id ?? ''}</div>
    </>
  )
}

/* TC-NOTIFY-PROVIDER-001: Able to add / remove notifications  */
test('notify() adds alert, remove() removes it', () => {
  render(
    <NotificationProvider>
      <Scenario />
    </NotificationProvider>
  )

  expect(screen.getByTestId('count')).toHaveTextContent('0')

  fireEvent.click(screen.getByText('notify'))
  expect(screen.getByTestId('count')).toHaveTextContent('1')

  const id = screen.getByTestId('first-id').textContent
  expect(id).not.toBe('')

  fireEvent.click(screen.getByText('remove-first'))
  expect(screen.getByTestId('count')).toHaveTextContent('0')
})
