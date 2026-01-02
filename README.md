# Offline Chatbot with Gemma Model

The first offline chatbot powered by Google's Gemma model. This chatbot runs completely offline on your local machine after the initial model download, providing fast and private conversations without requiring an internet connection.

## Features

- 🔒 **Fully Offline**: Runs completely on your local machine after initial setup
- 🚀 **Fast**: Uses the lightweight Gemma 2B model for quick responses
- 💬 **Interactive**: Command-line interface for natural conversations
- 🧠 **Context-Aware**: Maintains conversation history for coherent interactions
- ⚙️ **Configurable**: Easy-to-adjust parameters for different use cases

## Requirements

- Python 3.8 or higher
- At least 8GB RAM (16GB recommended)
- ~5GB disk space for model files
- GPU with CUDA support (optional, but recommended for faster inference)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Sreejakappaganti/offlinechatbot.git
   cd offlinechatbot
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **First-time setup**: On the first run, the chatbot will download the Gemma model (~5GB). This requires an internet connection and may take several minutes depending on your connection speed.

## Usage

### Basic Usage

Run the chatbot with:

```bash
python chatbot.py
```

### Interactive Commands

Once the chatbot is running, you can use these commands:

- Type your message and press Enter to chat
- `quit` or `exit` - End the conversation
- `reset` - Clear conversation history
- `help` - Display available commands

### Example Session

```
You: Hello! What can you help me with?

Bot: Hello! I'm here to help you with a variety of tasks. I can...

You: Tell me about Python programming

Bot: Python is a high-level, interpreted programming language...

You: quit

Goodbye! Thanks for chatting.
```

## Configuration

You can customize the chatbot's behavior by editing `config.py`:

- `MODEL_NAME`: The Gemma model variant to use (default: "google/gemma-2b-it")
- `MAX_NEW_TOKENS`: Maximum response length (default: 256)
- `TEMPERATURE`: Response creativity (0.0 = deterministic, 1.0 = creative)
- `TOP_P`: Nucleus sampling threshold (default: 0.9)
- `TOP_K`: Top-K sampling parameter (default: 50)
- `MAX_HISTORY`: Number of conversation turns to remember (default: 5)

## Model Information

This chatbot uses Google's Gemma 2B instruction-tuned model (`google/gemma-2b-it`):

- **Model Size**: ~5GB
- **Parameters**: 2 billion
- **Type**: Instruction-tuned for conversational AI
- **License**: Gemma Terms of Use

The model is cached locally in the `./models` directory after the first download.

## Offline Operation

After the initial model download:

1. ✅ No internet connection required
2. ✅ All processing happens locally
3. ✅ Your conversations remain private
4. ✅ Works in air-gapped environments

## Troubleshooting

### Model Download Issues

If the model fails to download:
- Ensure you have a stable internet connection
- Check that you have sufficient disk space (~5GB free)
- Try running the script again - downloads can resume from where they left off

### Out of Memory Errors

If you encounter memory errors:
- Close other applications to free up RAM
- Edit `config.py` and reduce `MAX_NEW_TOKENS`
- Consider using a machine with more RAM

### Slow Performance on CPU

The chatbot works on CPU but is slower:
- Responses may take 10-30 seconds on CPU
- For better performance, use a CUDA-compatible GPU
- Consider reducing `MAX_NEW_TOKENS` for faster responses

## Project Structure

```
offlinechatbot/
├── chatbot.py          # Main chatbot implementation
├── config.py           # Configuration parameters
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── .gitignore         # Git ignore rules
└── models/            # Model cache directory (created on first run)
```

## License

This project is open source. The Gemma model is subject to Google's Gemma Terms of Use.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## Acknowledgments

- Google for the Gemma model
- Hugging Face for the transformers library