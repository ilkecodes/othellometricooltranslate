"""
Minimal example: call Hugging Face hf-inference (serverless router) with OpenAI SDK.
Requires HF_TOKEN env var and a model available on hf-inference.
"""

import os
from openai import OpenAI


def main():
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.environ["HF_TOKEN"],
    )

    completion = client.chat.completions.create(
        model="HuggingFaceTB/SmolLM3-3B:hf-inference",
        messages=[{"role": "user", "content": "What is the capital of France?"}],
        max_tokens=128,
        temperature=0.7,
    )

    print(completion.choices[0].message)


if __name__ == "__main__":
    main()
