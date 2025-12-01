"""
Streamlit demo for Gemma Sales models.

Supports either:
- A merged checkpoint (set MODEL_REPO to merged model)
- A LoRA adapter (default): loads base Gemma and applies adapter

Environment variables (set in Hugging Face Space secrets if private):
- HF_TOKEN: token with read access (optional for public repos)
- MODEL_REPO: repo to load, default "ilkeileri/gemma-sales-comprehensive"
- USE_MERGED: "true" to skip PEFT and load a merged full model
"""

import os
import streamlit as st
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel


DEFAULT_REPO = "ilkeileri/gemma-sales-comprehensive"


@st.cache_resource
def load_model(repo: str, use_merged: bool, token: str | None):
    tokenizer = AutoTokenizer.from_pretrained(repo, token=token)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    device_map = "auto"

    if use_merged:
        model = AutoModelForCausalLM.from_pretrained(
            repo,
            torch_dtype=dtype,
            device_map=device_map,
            token=token,
        )
    else:
        base = AutoModelForCausalLM.from_pretrained(
            "google/gemma-1.1-2b-it",
            torch_dtype=dtype,
            device_map=device_map,
            token=token,
        )
        model = PeftModel.from_pretrained(base, repo, token=token)

    model.eval()
    return model, tokenizer


def format_prompt(history, user_input: str) -> str:
    """Builds a simple chat-style prompt using the training template tokens."""
    turns = []
    for turn in history:
        turns.append(f"<start_of_turn>user\n{turn['user']}<end_of_turn>\n<start_of_turn>model\n{turn['model']}<end_of_turn>")
    turns.append(f"<start_of_turn>user\n{user_input}<end_of_turn>\n<start_of_turn>model\n")
    return "\n".join(turns)


def main():
    st.set_page_config(page_title="Gemma Sales Chat", page_icon="💬", layout="centered")
    st.title("Gemma Sales Chat")

    repo = os.getenv("MODEL_REPO", DEFAULT_REPO)
    use_merged = os.getenv("USE_MERGED", "false").lower() == "true"
    token = os.getenv("HF_TOKEN")

    st.caption(f"Model repo: {repo}  •  Mode: {'merged' if use_merged else 'adapter'}")

    model, tokenizer = load_model(repo, use_merged, token)

    if "history" not in st.session_state:
        st.session_state.history = []

    with st.form("chat"):
        user_input = st.text_area("Your prompt", height=120)
        max_new_tokens = st.slider("Max new tokens", 64, 400, 200, step=16)
        temperature = st.slider("Temperature", 0.1, 1.5, 0.7, step=0.05)
        submitted = st.form_submit_button("Send")

    if submitted and user_input.strip():
        prompt = format_prompt(st.session_state.history, user_input.strip())
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id,
            )

        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Get the latest model answer after the last model tag
        if "<start_of_turn>model" in decoded:
            answer = decoded.split("<start_of_turn>model")[-1].strip()
        else:
            answer = decoded[len(prompt) :]

        st.session_state.history.append({"user": user_input.strip(), "model": answer})

    # Display history
    for turn in reversed(st.session_state.history):
        st.markdown(f"**You:** {turn['user']}")
        st.markdown(f"**Model:** {turn['model']}")
        st.markdown("---")


if __name__ == "__main__":
    main()
