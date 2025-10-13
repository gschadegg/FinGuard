import { renderHook, act } from '@testing-library/react'
import { useSessionTimers } from '@/hooks/useSessionTimers'

jest.mock('../lib/utils', () => ({ getExp: jest.fn() }))
import { getExp } from '../lib/utils'
const getExpMock = getExp

beforeEach(() => {
  jest.clearAllMocks()
  jest.useFakeTimers()
})

afterEach(() => {
  jest.useRealTimers()
})

function setExpSecondsFromNow(secondsFromNow) {
  if (secondsFromNow === null) {
    getExpMock.mockReturnValue(null)
    return
  }
  const nowSec = Math.floor(Date.now() / 1000)
  getExpMock.mockReturnValue(nowSec + secondsFromNow)
}

// TC-AUTH-TIMER-001: Base scenario, token exists timer delays are set and called
test('schedules prompt then expire at expected times', () => {
  const onPrompt = jest.fn()
  const onExpire = jest.fn()

  setExpSecondsFromNow(600)
  renderHook(() => useSessionTimers('jwt', { leadSeconds: 120, onPrompt, onExpire }))

  act(() => jest.advanceTimersByTime(479_000))
  expect(onPrompt).not.toHaveBeenCalled()
  act(() => jest.advanceTimersByTime(1_000))
  expect(onPrompt).toHaveBeenCalledTimes(1)
  expect(onExpire).not.toHaveBeenCalled()

  act(() => jest.advanceTimersByTime(119_000))
  expect(onExpire).not.toHaveBeenCalled()
  act(() => jest.advanceTimersByTime(1_000))
  expect(onExpire).toHaveBeenCalledTimes(1)
})

// TC-AUTH-TIMER-002: No token exist, no timers set
test('no token: does nothing', () => {
  const onPrompt = jest.fn()
  const onExpire = jest.fn()

  renderHook(() => useSessionTimers(null, { leadSeconds: 120, onPrompt, onExpire }))

  act(() => jest.advanceTimersByTime(60_000))
  expect(onPrompt).not.toHaveBeenCalled()
  expect(onExpire).not.toHaveBeenCalled()
})

// TC-AUTH-TIMER-003: Token change clears existing timers and creates new ones
test('token change clears previous timers and reschedules', () => {
  const onPrompt = jest.fn()
  const onExpire = jest.fn()

  setExpSecondsFromNow(600)
  const { rerender } = renderHook(
    ({ token }) => useSessionTimers(token, { leadSeconds: 120, onPrompt, onExpire }),
    { initialProps: { token: 'token-A' } }
  )

  setExpSecondsFromNow(90)
  rerender({ token: 'token-B' })

  act(() => jest.advanceTimersByTime(0))
  expect(onPrompt).toHaveBeenCalledTimes(1)
  expect(onExpire).not.toHaveBeenCalled()

  act(() => jest.advanceTimersByTime(89_000))
  expect(onExpire).not.toHaveBeenCalled()
  act(() => jest.advanceTimersByTime(1_000))
  expect(onExpire).toHaveBeenCalledTimes(1)
})
