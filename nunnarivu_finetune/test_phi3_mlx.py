from mlx_lm import load, generate


def main():
    # Base Phi-3 Mini instruct model from Hugging Face.
    model_name = "microsoft/Phi-3-mini-4k-instruct"

    print(f"Loading model: {model_name} (this may take a while the first time)...")
    model, tokenizer = load(model_name)

    # Simple chat-style prompt so it behaves like Sunny/Nunnarivu
    messages = [
        {
            "role": "system",
            "content": "You are Nunnarivu (Sunny), a short, direct offline Mac assistant.",
        },
        {
            "role": "user",
            "content": "Say your name and one thing you can do on my Mac.",
        },
    ]

    # Build the chat prompt for chat-style models
    prompt = tokenizer.apply_chat_template(messages, add_generation_prompt=True)

    print("Generating response...")
    response = generate(
        model=model,
        tokenizer=tokenizer,
        prompt=prompt,
        max_tokens=64,   # no temperature arg, use defaults
    )

    print("\n=== Model Response ===")
    print(response)


if __name__ == "__main__":
    main()