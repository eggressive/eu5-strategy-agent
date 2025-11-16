#!/usr/bin/env python3
"""
Test OpenAI API Key with gpt-5-mini

Simple script to verify OpenAI API authentication and model availability.
"""

from openai import OpenAI
import time


def test_api_key():
    """Test the OpenAI API key with specified configuration."""

    # Configuration from config.toml
    config = {
        "model": "gpt-5-mini",
        "base_url": "https://api.openai.com/v1",
        "api_key": "YOUR_OPENAI_API_KEY",
        "max_tokens": 8192,
        "temperature": 0.0,
    }

    print("=" * 70)
    print("OPENAI API KEY TEST")
    print("=" * 70)
    print(f"\nModel: {config['model']}")
    print(f"Base URL: {config['base_url']}")
    print(f"API Key: {config['api_key'][:20]}...{config['api_key'][-10:]}")
    print(f"Max Tokens: {config['max_tokens']}")
    print(f"Temperature: {config['temperature']}")
    print("\n" + "-" * 70)

    try:
        # Initialize OpenAI client
        print("\n[1/3] Initializing OpenAI client...")
        client = OpenAI(api_key=config["api_key"], base_url=config["base_url"])
        print("✓ Client initialized")

        # Make API call
        print(f"\n[2/3] Testing API call with {config['model']}...")
        start_time = time.time()

        response = client.chat.completions.create(
            model=config["model"],
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'API test successful' if you can read this."},
            ],
            max_completion_tokens=50,  # gpt-5 models use max_completion_tokens
            # Note: gpt-5-mini only supports temperature=1 (default), so we omit it
        )

        elapsed_time = time.time() - start_time
        print(f"✓ API call completed in {elapsed_time:.2f}s")

        # Display results
        print("\n[3/3] Analyzing response...")
        print("\n" + "=" * 70)
        print("SUCCESS: API KEY IS VALID")
        print("=" * 70)

        print(f"\nModel used: {response.model}")
        print(f"Response ID: {response.id}")
        print("\nAssistant response:")
        print(f"  {response.choices[0].message.content}")

        print("\nToken usage:")
        usage = getattr(response, "usage", None)
        if usage is not None:
            print(f"  Prompt tokens: {usage.prompt_tokens}")  # type: ignore
            print(f"  Completion tokens: {usage.completion_tokens}")  # type: ignore
            print(f"  Total tokens: {usage.total_tokens}")  # type: ignore
        else:
            print("  (usage details not provided)")

        print(f"\nFinish reason: {response.choices[0].finish_reason}")

        print("\n" + "=" * 70)
        print("✓ All tests passed! API key is working correctly.")
        print("=" * 70)

        return True

    except Exception as e:
        print("\n" + "=" * 70)
        print("FAILURE: API KEY TEST FAILED")
        print("=" * 70)
        print(f"\nError type: {type(e).__name__}")
        print(f"Error message: {str(e)}")

        # Provide helpful guidance
        print("\n" + "-" * 70)
        print("TROUBLESHOOTING:")
        print("-" * 70)

        error_str = str(e).lower()

        if "401" in error_str or "invalid_api_key" in error_str:
            print("\n✗ Invalid or expired API key")
            print("  → Get a new key from: https://platform.openai.com/api-keys")
            print("  → Ensure the key has not been revoked")

        elif "404" in error_str or "model_not_found" in error_str:
            print("\n✗ Model not found or not accessible")
            print("  → Check if 'gpt-5-mini' is available for your account")
            print("  → Try with 'gpt-4o' or 'gpt-4-turbo' instead")

        elif "429" in error_str or "rate_limit" in error_str:
            print("\n✗ Rate limit exceeded")
            print("  → Wait a moment and try again")
            print("  → Check your API usage quota")

        elif "connection" in error_str or "network" in error_str:
            print("\n✗ Network connectivity issue")
            print("  → Check your internet connection")
            print("  → Verify firewall settings")

        else:
            print("\n✗ Unknown error")
            print("  → Check the error message above for details")
            print("  → Verify all configuration settings")

        print("\n" + "=" * 70)

        return False


if __name__ == "__main__":
    success = test_api_key()
    exit(0 if success else 1)
