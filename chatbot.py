#!/usr/bin/env python3
"""
Offline Chatbot with Gemma Model

This script implements a chatbot that runs completely offline using Google's Gemma model.
The model is downloaded once and cached locally for subsequent runs.
"""

import os
import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from config import (
    MODEL_NAME,
    MODEL_CACHE_DIR,
    MAX_NEW_TOKENS,
    TEMPERATURE,
    TOP_P,
    TOP_K,
    DO_SAMPLE,
    MAX_HISTORY
)


class OfflineChatbot:
    """Offline chatbot using the Gemma model."""
    
    def __init__(self):
        """Initialize the chatbot by loading the model and tokenizer."""
        print("Initializing offline chatbot with Gemma model...")
        print(f"Model: {MODEL_NAME}")
        print(f"Cache directory: {MODEL_CACHE_DIR}")
        
        # Create cache directory if it doesn't exist
        os.makedirs(MODEL_CACHE_DIR, exist_ok=True)
        
        # Set device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        try:
            # Load tokenizer
            print("\nLoading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                MODEL_NAME,
                cache_dir=MODEL_CACHE_DIR
            )
            
            # Load model
            print("Loading model (this may take a while on first run)...")
            self.model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                cache_dir=MODEL_CACHE_DIR,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            self.model.eval()
            print("Model loaded successfully!\n")
            
        except Exception as e:
            print(f"\nError loading model: {e}")
            print("\nNote: On first run, you need internet to download the model.")
            print("After that, the chatbot will work completely offline.")
            sys.exit(1)
        
        # Initialize conversation history
        self.conversation_history = []
    
    def generate_response(self, user_input):
        """
        Generate a response to user input.
        
        Args:
            user_input (str): The user's message
            
        Returns:
            str: The chatbot's response
        """
        # Add user input to history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Keep only recent history
        if len(self.conversation_history) > MAX_HISTORY * 2:
            self.conversation_history = self.conversation_history[-(MAX_HISTORY * 2):]
        
        # Format conversation for Gemma
        chat_text = self._format_chat()
        
        # Tokenize
        inputs = self.tokenizer(chat_text, return_tensors="pt").to(self.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                top_k=TOP_K,
                do_sample=DO_SAMPLE,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode the response
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the new response (remove the prompt)
        response = full_response[len(chat_text):].strip()
        
        # Add response to history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def _format_chat(self):
        """Format the conversation history for the model."""
        chat_text = ""
        for message in self.conversation_history:
            if message["role"] == "user":
                chat_text += f"<start_of_turn>user\n{message['content']}<end_of_turn>\n"
            elif message["role"] == "assistant":
                chat_text += f"<start_of_turn>model\n{message['content']}<end_of_turn>\n"
        
        # Add the prompt for the next model response
        chat_text += "<start_of_turn>model\n"
        return chat_text
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
        print("Conversation history cleared.\n")
    
    def chat(self):
        """Start an interactive chat session."""
        print("=" * 70)
        print("Offline Chatbot with Gemma Model")
        print("=" * 70)
        print("\nCommands:")
        print("  - Type 'quit' or 'exit' to end the conversation")
        print("  - Type 'reset' to clear conversation history")
        print("  - Type 'help' to see this message again")
        print("\n" + "=" * 70 + "\n")
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit']:
                    print("\nGoodbye! Thanks for chatting.\n")
                    break
                
                if user_input.lower() == 'reset':
                    self.reset_conversation()
                    continue
                
                if user_input.lower() == 'help':
                    print("\nCommands:")
                    print("  - Type 'quit' or 'exit' to end the conversation")
                    print("  - Type 'reset' to clear conversation history")
                    print("  - Type 'help' to see this message again\n")
                    continue
                
                if not user_input:
                    continue
                
                # Generate and display response
                print("\nBot: ", end="", flush=True)
                response = self.generate_response(user_input)
                print(response + "\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! Thanks for chatting.\n")
                break
            except Exception as e:
                print(f"\nError generating response: {e}\n")


def main():
    """Main entry point for the chatbot."""
    chatbot = OfflineChatbot()
    chatbot.chat()


if __name__ == "__main__":
    main()
