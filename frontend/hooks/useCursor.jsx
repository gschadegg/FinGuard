'use client'
import { useState, useEffect, useRef, useMemo } from 'react'

export default function useCursor(fetchPage, initialPageSize = 50, staticArgs = {}) {
  const [pageIndex, setPageIndex] = useState(0)
  const [pageSize, setPageSize] = useState(initialPageSize)
  const [cursorStack, setCursorStack] = useState([null])

  const [pages, setPages] = useState({})

  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  const current = pages[pageIndex]
  const hasMore = current?.hasMore ?? false
  const staticKey = useMemo(() => JSON.stringify(staticArgs), [staticArgs])

  useEffect(() => {
    setPageIndex(0)
    setCursorStack([null])
    setPages({})
  }, [staticKey, pageSize])

  const cursor = cursorStack[pageIndex] ?? null
  const reqIdRef = useRef(0)
  const hasPage = !!pages[pageIndex]

  useEffect(() => {
    if (pages[pageIndex]) return

    const myId = ++reqIdRef.current
    let aborted = false

    setIsLoading(true)
    setError(null)

    async function fetchData() {
      try {
        const res = await fetchPage({ limit: pageSize, cursor, ...staticArgs })
        if (aborted || reqIdRef.current !== myId) return

        // res = { rows, nextCursor, hasMore } changed these values in the fetch function
        setPages((page) => ({ ...page, [pageIndex]: res }))
        if (res.nextCursor !== null) {
          setCursorStack((stack) => {
            const next = [...stack]
            next[pageIndex + 1] = res.nextCursor
            return next
          })
        }
      } catch (e) {
        if (aborted || reqIdRef.current !== myId) return
        setError(e)
      } finally {
        if (aborted || reqIdRef.current !== myId) return
        setIsLoading(false)
      }
    }

    fetchData()
    return () => {
      aborted = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pageIndex, pageSize, cursor, fetchPage, staticKey, hasPage])

  return {
    pageIndex,
    pageSize,
    rows: current?.rows ?? [],
    isLoading,
    error,
    hasMore,
    setPageIndex,
    setPageSize,
    pageCount: hasMore ? pageIndex + 2 : pageIndex + 1,
  }
}
