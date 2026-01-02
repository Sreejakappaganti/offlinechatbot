"""Configuration for the offline chatbot."""

# Model configuration
MODEL_NAME = "google/gemma-2b-it"  # Instruction-tuned Gemma 2B model
MODEL_CACHE_DIR = "./models"  # Local directory to cache the model

# Generation parameters
MAX_NEW_TOKENS = 256  # Maximum number of tokens to generate
TEMPERATURE = 0.7  # Controls randomness (0.0 = deterministic, 1.0 = creative)
TOP_P = 0.9  # Nucleus sampling threshold
TOP_K = 50  # Top-K sampling parameter
DO_SAMPLE = True  # Enable sampling for more diverse responses

# Chat parameters
MAX_HISTORY = 5  # Maximum number of conversation turns to keep in context
