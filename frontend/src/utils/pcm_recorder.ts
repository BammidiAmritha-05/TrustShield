/**
 * Web Audio API PCM Recorder for TrustShield.
 * Captures browser microphone audio via AudioContext,
 * downsamples to 16,000 Hz Mono 16-bit PCM, and encodes each 1-second slice into a valid WAV container.
 */

export interface PcmRecorderOptions {
  sampleRate?: number;
  timeSliceMs?: number;
  onAudioChunk: (chunk: ArrayBuffer) => void;
  onError?: (error: Error) => void;
}

export class PcmWavRecorder {
  private audioContext: AudioContext | null = null;
  private mediaStream: MediaStream | null = null;
  private sourceNode: MediaStreamAudioSourceNode | null = null;
  private processorNode: ScriptProcessorNode | null = null;
  private isRecording = false;
  private options: Required<PcmRecorderOptions>;
  private pcmBuffer: Float32Array[] = [];
  private accumulatedSampleCount = 0;
  private sliceSampleLimit = 0;

  constructor(options: PcmRecorderOptions) {
    this.options = {
      sampleRate: options.sampleRate || 16000,
      timeSliceMs: options.timeSliceMs || 1000,
      onAudioChunk: options.onAudioChunk,
      onError: options.onError || ((err) => console.error('PcmWavRecorder error:', err)),
    };
    this.sliceSampleLimit = Math.floor((this.options.sampleRate * this.options.timeSliceMs) / 1000);
  }

  public async start(): Promise<void> {
    if (this.isRecording) return;

    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: this.options.sampleRate,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
      this.audioContext = new AudioContextClass({ sampleRate: this.options.sampleRate });

      this.sourceNode = this.audioContext.createMediaStreamSource(this.mediaStream);
      this.processorNode = this.audioContext.createScriptProcessor(4096, 1, 1);

      this.processorNode.onaudioprocess = (e: AudioProcessingEvent) => {
        if (!this.isRecording) return;
        const inputData = e.inputBuffer.getChannelData(0);
        const clone = new Float32Array(inputData.length);
        clone.set(inputData);
        this.pcmBuffer.push(clone);
        this.accumulatedSampleCount += clone.length;

        if (this.accumulatedSampleCount >= this.sliceSampleLimit) {
          this.flushChunk();
        }
      };

      this.sourceNode.connect(this.processorNode);
      this.processorNode.connect(this.audioContext.destination);

      this.isRecording = true;
    } catch (err: any) {
      this.stop();
      this.options.onError(err);
      throw err;
    }
  }

  public stop(): void {
    if (!this.isRecording && !this.mediaStream && !this.audioContext) return;
    this.isRecording = false;

    if (this.accumulatedSampleCount > 0) {
      this.flushChunk();
    }

    if (this.processorNode) {
      this.processorNode.disconnect();
      this.processorNode = null;
    }

    if (this.sourceNode) {
      this.sourceNode.disconnect();
      this.sourceNode = null;
    }

    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
      this.mediaStream = null;
    }

    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
      this.audioContext = null;
    }

    this.pcmBuffer = [];
    this.accumulatedSampleCount = 0;
  }

  private flushChunk(): void {
    if (this.pcmBuffer.length === 0 || this.accumulatedSampleCount === 0) return;

    const merged = new Float32Array(this.accumulatedSampleCount);
    let offset = 0;
    for (const buf of this.pcmBuffer) {
      merged.set(buf, offset);
      offset += buf.length;
    }

    this.pcmBuffer = [];
    this.accumulatedSampleCount = 0;

    const wavBuffer = this.encodeWav(merged, this.options.sampleRate);
    this.options.onAudioChunk(wavBuffer);
  }

  private encodeWav(samples: Float32Array, sampleRate: number): ArrayBuffer {
    const numChannels = 1;
    const bytesPerSample = 2;
    const blockAlign = numChannels * bytesPerSample;
    const byteRate = sampleRate * blockAlign;
    const dataSize = samples.length * bytesPerSample;
    const buffer = new ArrayBuffer(44 + dataSize);
    const view = new DataView(buffer);

    this.writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + dataSize, true);
    this.writeString(view, 8, 'WAVE');

    this.writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, byteRate, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, 16, true);

    this.writeString(view, 36, 'data');
    view.setUint32(40, dataSize, true);

    let offset = 44;
    for (let i = 0; i < samples.length; i++, offset += 2) {
      const s = Math.max(-1, Math.min(1, samples[i]));
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
    }

    return buffer;
  }

  private writeString(view: DataView, offset: number, string: string): void {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  }
}
