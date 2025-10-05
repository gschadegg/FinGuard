import { renderHook, act, waitFor } from '@testing-library/react'
import useCursor from './../hooks/useCursor'

function makeFetch() {
  const pages = {
    start: { rows: [{ id: 1 }, { id: 2 }], nextCursor: 'cursor1', hasMore: true },
    cursor1: { rows: [{ id: 3 }], nextCursor: null, hasMore: false },
  }

  const fetchPage = jest.fn(async ({ cursor }) => {
    await Promise.resolve()
    const key = cursor ?? 'start'
    return pages[key]
  })
  return fetchPage
}

beforeEach(() => {
  jest.clearAllMocks()
})

//   TC-TABLE-CURSOR-001: Base Scenario, initial page fetch
test('Initial fetch success', async () => {
  const fetchPage = makeFetch()

  const { result } = renderHook(() => useCursor(fetchPage, 50, { userId: 1 }))

  expect(result.current.isLoading).toBe(true)

  await waitFor(() => expect(result.current.isLoading).toBe(false))

  expect(fetchPage).toHaveBeenCalledTimes(1)
  expect(fetchPage).toHaveBeenLastCalledWith(
    expect.objectContaining({ limit: 50, cursor: null, userId: 1 })
  )
  expect(result.current.rows).toEqual([{ id: 1 }, { id: 2 }])
  expect(result.current.hasMore).toBe(true)
  expect(result.current.pageIndex).toBe(0)
  expect(result.current.pageCount).toBe(2)
})

//   TC-TABLE-CURSOR-002: fetch next page with cursor
test('Fetch next page with cursor', async () => {
  const fetchPage = makeFetch()
  const { result } = renderHook(() => useCursor(fetchPage, 50, { userId: 1 }))

  await waitFor(() => expect(result.current.isLoading).toBe(false))
  expect(result.current.rows).toHaveLength(2)

  act(() => result.current.setPageIndex(1))
  await waitFor(() => expect(result.current.isLoading).toBe(false))

  expect(fetchPage).toHaveBeenCalledTimes(2)
  expect(fetchPage.mock.calls[1][0]).toEqual(
    expect.objectContaining({ cursor: 'cursor1', limit: 50, userId: 1 })
  )
  expect(result.current.rows).toEqual([{ id: 3 }])
  expect(result.current.hasMore).toBe(false)
})

//   TC-TABLE-CURSOR-003: Go back a page and uses cache
test('Going back uses cache', async () => {
  const fetchPage = makeFetch()
  const { result } = renderHook(() => useCursor(fetchPage, 50, { userId: 1 }))

  await waitFor(() => expect(result.current.isLoading).toBe(false))
  act(() => result.current.setPageIndex(1))

  await waitFor(() => expect(result.current.isLoading).toBe(false))
  const calls = fetchPage.mock.calls.length

  act(() => result.current.setPageIndex(0))
  expect(result.current.rows).toEqual([{ id: 1 }, { id: 2 }])
  expect(fetchPage.mock.calls.length).toBe(calls)
})

//   TC-TABLE-CURSOR-004: fetch next page with cursor
test('Fetch fails', async () => {
  const fetchPage = jest.fn(async () => {
    await Promise.resolve()
    throw new Error('Failed Fetch')
  })

  const { result } = renderHook(() => useCursor(fetchPage, 50, { userId: 1 }))

  await waitFor(() => expect(result.current.isLoading).toBe(false))
  expect(result.current.error).toBeInstanceOf(Error)
  expect(result.current.rows).toEqual([])
  expect(result.current.hasMore).toBe(false)
})
