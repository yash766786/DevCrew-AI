import { useEffect } from "react";

export function useSessionSocket(onMessage: (data: any) => void) {
  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onopen = () => {
      console.log("Socket connected");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    ws.onclose = () => {
      console.log("Socket closed");
    };

    return () => ws.close();
  }, []);
}
