"""
Reliable Hugging Face upload helper.

Usage examples:
  python upload_model.py --repo ilkeileri/gemma-sales-comprehensive --model-path outputs/gemma-sales-comprehensive/checkpoint-75 --private
  HF_TOKEN=xxx python upload_model.py --repo ilkeileri/gemma-sales-comprehensive --model-path models/gemma-sales-comprehensive-merged
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Optional

from huggingface_hub import HfApi, create_repo


def resolve_model_path(path_str: str) -> Path:
    path = Path(path_str).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Model path not found: {path}")
    return path


def get_token() -> Optional[str]:
    # Respect standard env vars; falls back to cached login if unset.
    return os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")


def upload(model_path: Path, repo_id: str, private: bool) -> None:
    api = HfApi(token=get_token())

    print(f"→ Ensuring repo exists: {repo_id} (private={private})")
    create_repo(repo_id, exist_ok=True, private=private, repo_type="model", token=get_token())

    print(f"→ Uploading from {model_path}")
    api.upload_folder(
        folder_path=str(model_path),
        repo_id=repo_id,
        repo_type="model",
    )

    print("\n✅ Upload complete")
    print(f"🔗 https://huggingface.co/{repo_id}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload a finetuned model or adapter to Hugging Face.")
    parser.add_argument("--repo", required=True, help="Repo name, e.g. your-username/model-name")
    parser.add_argument(
        "--model-path",
        required=True,
        help="Path to folder containing model files (relative or absolute).",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Create/keep the repo private (default public).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    upload(resolve_model_path(args.model_path), args.repo, private=args.private)
