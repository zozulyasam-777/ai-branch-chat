# 🌿 AI Branching Chat

A non-linear dialogue interface for LLMs. Explore multiple conversation paths simultaneously, version your thoughts, and publish dialogues as JSON Feeds.

## 🚀 Features

- **Branching Logic**: Fork conversations like Git branches (`/fork`).
- **Context Switching**: Switch between hypotheses without losing history (`/switch`).
- **JSON Storage**: All dialogues stored in human-readable JSON.
- **JSON Feed Export**: Publish conversations as subscribable feeds (`/export`).
- **Git-Friendly**: Designed to be versioned in Git repositories.

## 🔄 How It Works

┌───────────┐   ┌────────────────┐   ┌─────────────┐
│     You   │   │  AI Branching  │   │    AI API   │
│    (CLI)  │──▶│      Chat      │──▶│ (OpenAI,    │
│           │◀──│ (Python Core)  │◀──│ Local, etc) │
└───────────┘   └────────────────┘   └─────────────┘
     │
     ▼
┌──────────────┐
│  JSON Files  │
│(data/ folder)│
└──────────────┘
     │
     ▼
┌───────────────┐
│    JSON Feed  │
│(web/feed.json)│
└───────────────┘
     │
     ▼
┌───────────────┐
│   Publishers  │
│ (Readers, Web)│
└───────────────┘
Configuration
### Data Flow

1.  **Input**: You type a message in the CLI.
2.  **Processing**: The core saves the message to `data/session.json` and prepares context.
3.  **AI Generation**: The message is sent to the AI provider (OpenAI, Anthropic, or Mock).
4.  **Storage**: The AI response is saved as a new node in the conversation tree.
5.  **Export**: Run `/export` to generate a standard **JSON Feed** (`web/feed.json`).
6.  **Publish**: Host the `web/` folder on GitHub Pages or any static host.
7.  **Consumption**: Readers subscribe to `feed.json` using any JSON Feed reader.


## 🔌 AI Integration

The program supports multiple AI providers through a simple configuration.

## 🔒 Privacy & Anonymization

This project supports local data anonymization before sending to AI APIs.

### Features

- **Pattern-based detection**: Names, phones, emails, passports, cards
- **Multiple masking strategies**: Tokens, partial mask, full mask, hash, generalize
- **Reversible**: Original data stored locally, only anonymized sent to AI
- **Offline**: No external dependencies for anonymization





### Supported Providers

| Provider |      Configuration      |              Description                    |
|----------|-------------------------|---------------------------------------------|
| **Mock** | `"ai_provider": "mock"` | Built-in test responses (no API key needed) |
|**OpenAI**|`"ai_provider": "openai"`|         GPT-3.5, GPT-4 via official API     |
|**Local** | `"ai_provider": "local"`|         Ollama, LM Studio via localhost     |

### Setup Example (OpenAI)

Edit `config.json`:

```json
{
  "ai_provider": "openai",
  "api_key": "sk-your-key-here",
  "model": "gpt-4",
  "api_endpoint": "https://api.openai.com/v1/chat/completions"
}
```

## 🛠 Installation

1. **Clone the repo**:
   ```bash
   git clone https://github.com/zozulyasam-777/ai-branch-chat.git
   cd ai-branch-chat
   ```

## 🚀 Project Structure
- cli.py: Main interface.
- conversation.py: Logic for branching and JSON handling.
- data/: Where sessions are stored.
- web/: Exported feeds for publishing.


## 📄 License
MIT License. Feel free to fork and experiment!

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run**:
   ```bash
   python cli.py
   ```

## 💡 Usage Examples

**Start Chatting**:
    ```bashConfiguration

**Create a Branch (Hypothesis)**:
    ```bash
    [hypothesis_flu] > /switch main
    [main] > Let's check ORVI instead.
    ```

**Switch Back**:
    ```bash
    [hypothesis_flu] > /switch main
    [main] > Let's check ORVI instead.
    ```

**Export for Publishing**:
    ```bash
    [main] > /export
    ```
Check web/feed.json for the result!

## 🗺️ Roadmap

- [ ] Add support for real OpenAI API
- [ ] Build web visualizer with D3.js
- [ ] Add multi-user collaboration via GitHub Actions
- [ ] Support for local LLMs (Ollama, LM Studio)


## ⭐ Show your support

If you like this project, please give it a star on GitHub! It helps others find it and motivates me to keep improving it. 