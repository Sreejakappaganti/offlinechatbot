#!/usr/bin/env python3
"""
Example demonstrating the chatbot interface.

This script shows how the chatbot would work without actually running the model.
Use this to understand the flow before downloading the full model.
"""

def demo_chatbot():
    """Demonstrate the chatbot interface."""
    print("=" * 70)
    print("Offline Chatbot with Gemma Model - DEMO MODE")
    print("=" * 70)
    print("\nThis is a demonstration of the chatbot interface.")
    print("To use the actual chatbot with Gemma model:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Run: python chatbot.py")
    print("\n" + "=" * 70 + "\n")
    
    # Simulated conversation
    examples = [
        {
            "user": "Hello! What can you help me with?",
            "bot": "Hello! I'm an offline chatbot powered by the Gemma model. I can help you with various tasks like answering questions, providing information, having conversations, and more. What would you like to know?"
        },
        {
            "user": "Tell me about Python programming",
            "bot": "Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used for web development, data science, machine learning, automation, and more. Python's syntax is clean and easy to learn, making it great for beginners while being powerful enough for experts."
        },
        {
            "user": "What makes this chatbot special?",
            "bot": "This chatbot is special because it runs completely offline on your local machine after the initial model download. This means:\n\n1. Privacy: Your conversations stay on your device\n2. Speed: No network latency\n3. Availability: Works without internet connection\n4. Cost: No API fees or usage limits\n\nIt uses Google's Gemma model, which is optimized for conversational AI while being small enough to run locally."
        }
    ]
    
    print("Example conversation:\n")
    for i, example in enumerate(examples, 1):
        print(f"You: {example['user']}\n")
        print(f"Bot: {example['bot']}\n")
        if i < len(examples):
            print("-" * 70 + "\n")
    
    print("=" * 70)
    print("\nTo start chatting with the real model, run: python chatbot.py")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    demo_chatbot()
