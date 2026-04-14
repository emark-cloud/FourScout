import { useState, useEffect, useRef, useCallback } from 'react'

const WS_URL = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`

export function useWebSocket() {
  const [messages, setMessages] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(WS_URL)
      wsRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        console.log('[WS] Connected')
      }

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          setMessages((prev) => [msg, ...prev].slice(0, 100))
        } catch (e) {
          console.error('[WS] Parse error:', e)
        }
      }

      ws.onclose = () => {
        setIsConnected(false)
        console.log('[WS] Disconnected, reconnecting in 3s...')
        reconnectTimeoutRef.current = setTimeout(connect, 3000)
      }

      ws.onerror = (err) => {
        console.error('[WS] Error:', err)
        ws.close()
      }
    } catch (e) {
      console.error('[WS] Connection error:', e)
      reconnectTimeoutRef.current = setTimeout(connect, 3000)
    }
  }, [])

  useEffect(() => {
    connect()
    return () => {
      if (wsRef.current) wsRef.current.close()
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current)
    }
  }, [connect])

  // Get latest messages of a specific type
  const getByType = useCallback(
    (type) => messages.filter((m) => m.type === type),
    [messages]
  )

  return { messages, isConnected, getByType }
}
