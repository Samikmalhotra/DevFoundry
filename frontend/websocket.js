class ObservabilityWS {
  constructor(onEvent) {
    this.onEvent = onEvent;
    this.ws = null;
    this.reconnectTimer = null;
    
    // Resolve ws protocol and host dynamically
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    this.wsUrl = `${protocol}//${window.location.host}/ws`;
  }

  connect() {
    if (this.ws) {
      this.ws.close();
    }
    console.log("Connecting to WebSocket:", this.wsUrl);
    this.ws = new WebSocket(this.wsUrl);

    this.ws.onopen = () => {
      console.log("WebSocket connected successfully");
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer);
        this.reconnectTimer = null;
      }
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.onEvent(data);
      } catch (e) {
        console.error("Error parsing WebSocket message content:", e);
      }
    };

    this.ws.onclose = () => {
      console.log("WebSocket connection closed. Reconnecting in 3s...");
      if (!this.reconnectTimer) {
        this.reconnectTimer = setTimeout(() => this.connect(), 3000);
      }
    };

    this.ws.onerror = (err) => {
      console.error("WebSocket encountered an error:", err);
      this.ws.close();
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}
