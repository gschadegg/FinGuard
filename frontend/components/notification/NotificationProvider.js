'use client'
import { createContext, useContext, useState, useCallback, useMemo } from 'react'

const NotificationContext = createContext({
  notify: () => {},
  remove: () => {},
  notices: [],
})

export function NotificationProvider({ children }) {
  const [notices, setNotices] = useState([])

  const remove = useCallback((id) => {
    setNotices((prev) => prev.filter((notices) => notices.id !== id))
  }, [])

  const notify = useCallback((new_notice) => {
    const id = `${Math.random().toString(36).slice(2)}`

    if (!new_notice.message && !new_notice.title) return

    const notice = {
      id,
      type: new_notice.type || 'success',
      title: new_notice.title,
      message: new_notice.message,
      duration: new_notice.duration ?? 6000,
    }

    setNotices((prev) => [notice, ...prev])
  }, [])

  // preventing rerenders except if notices change
  const value = useMemo(() => ({ notify, remove, notices }), [notify, remove, notices])

  return <NotificationContext.Provider value={value}>{children}</NotificationContext.Provider>
}

export function useNotify() {
  const { notify } = useContext(NotificationContext)
  return notify
}

export function useNotifications() {
  return useContext(NotificationContext)
}
