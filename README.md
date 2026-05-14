# PodFlow

Document to Podcast — Upload documents and automatically generate dual-host podcast audio.

## Feature

- 📄 Supports PDF / DOC / DOCX / TXT / EPUB / URL
- 🎙️ Two modes: Dual-host podcast & Single-host lecture
- 🤖 Multiple LLM backends: Ollama / llama.cpp / OpenAI / Deepseek / SiliconFlow
- 🔊 Multiple TTS backends: Edge-TTS (free) / VoxCPM2 / ChatTTS / OpenAI TTS
- 🌐 Web UI interface, user-friendly for non-technical users
- 🏠 Supports 100% local deployment

## Quick Start

### pip Installation

```bash
uv pip install podflow
podflow
```

Open your browser and visit http://localhost:8080

### Docker

```bash
git clone https://github.com/heliubj18/podflow.git
cd podflow

# No GPU (cloud LLM + Edge-TTS)
docker compose up

# With GPU (local Ollama)
docker compose --profile gpu up
```

## Configuration

After first startup, visit the Settings page to configure the LLM and TTS backends.

### LLM Backends

| Backend | Type | Description |
|------|------|------|
| Ollama | Local | Recommended, easy to install |
| llama.cpp | Local | Best performance |
| OpenAI | Cloud | Requires API Key |
| Deepseek | Cloud | Cost-effective |

### TTS Backends

| Backend | Type | Description |
|------|------|------|
| Edge-TTS | Cloud (free) | Default, zero configuration |
| VoxCPM2 | Local | GPU |
| ChatTTS | Local | GPU |
| OpenAI TTS | Cloud | Paid service |

## License

MIT
