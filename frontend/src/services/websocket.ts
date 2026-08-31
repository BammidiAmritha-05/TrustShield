import { config } from '../config';
import { WSServerEvent } from '../types/backend';

export type EventCallback = (event: WSServerEvent) => void;
export type ConnectionStatusCallback = (status: 'connecting' | 'connected' | 'disconnected' | 'error', error?: string) => void;

export class TrustShieldWebSocketClient {
  private socket: WebSocket | null = null;
  private sessionId: string;
  private onEventCallback: EventCallback;
  private onStatusCallback: ConnectionStatusCallback;
  private isIntentionallyClosed = false;

  constructor(sessionId: string, onEvent: EventCallback, onStatus: ConnectionStatusCallback) {
    this.sessionId = sessionId;
    this.onEventCallback = onEvent;
    this.onStatusCallback = onStatus;
  }

  public connect(): void {
    this.isIntentionallyClosed = false;
    this.onStatusCallback('connecting');

    const wsUrl = `${config.wsBaseUrl}/api/v1/sessions/${this.sessionId}/stream`;

    try {
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        this.onStatusCallback('connected');
      };

      this.socket.onmessage = (event) => {
        try {
          const parsed: WSServerEvent = JSON.parse(event.data);
          if (parsed && parsed.type) {
            this.onEventCallback(parsed);
          }
        } catch (e) {
          console.error('Failed to parse WebSocket server event:', e);
        }
      };

      this.socket.onerror = (event) => {
        console.error('WebSocket connection error:', event);
        this.onStatusCallback('error', 'WebSocket connection error occurred.');
      };

      this.socket.onclose = (event) => {
        if (!this.isIntentionallyClosed) {
          this.onStatusCallback('disconnected', `Closed (code: ${event.code})`);
        }
      };
    } catch (err: any) {
      this.onStatusCallback('error', err.message || 'Failed to initialize WebSocket');
    }
  }

  public sendText(text: string): boolean {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ action: 'send_text', text }));
      return true;
    }
    return false;
  }

  public sendAudioChunk(arrayBuffer: ArrayBuffer): boolean {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(arrayBuffer);
      return true;
    }
    return false;
  }

  public flushUtterance(): boolean {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ action: 'flush_utterance' }));
      return true;
    }
    return false;
  }

  public stopSession(): boolean {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ action: 'stop' }));
      return true;
    }
    return false;
  }

  public disconnect(): void {
    this.isIntentionallyClosed = true;
    if (this.socket) {
      this.socket.close(1000, 'User initiated disconnect');
      this.socket = null;
    }
    this.onStatusCallback('disconnected');
  }

  public isConnected(): boolean {
    return this.socket !== null && this.socket.readyState === WebSocket.OPEN;
  }
}
