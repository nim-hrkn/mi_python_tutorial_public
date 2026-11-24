"""ベースモデルを Hugging Face のキャッシュに取得する。"""
import argparse
from pathlib import Path

from experiment import MODEL


def main():
    """モデルを取得し、必要な設定・トークナイザー・重みのファイルを確認する。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-files-only", action="store_true",
                        help="Verify the cached snapshot without network access.")
    args = parser.parse_args()

    from huggingface_hub import snapshot_download

    path = snapshot_download(repo_id=MODEL, local_files_only=args.local_files_only)

    for filename in ("config.json", "tokenizer.json", "model.safetensors"):
        file = Path(path) / filename
        if not file.is_file():
            parser.error(f"Required model file is missing: {file}")
    print(path)


if __name__ == "__main__":
    main()
