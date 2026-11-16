#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sends generated Card News (6 PNG slides + Instagram Caption) to a Discord Webhook.
Reads DISCORD_WEBHOOK_URL from .env file in workspace root or environment variable.
Usage:
  python .agents/skills/fact-card-news/scripts/send_discord.py output/YYYYMMDD_<slug>
"""

import json
import os
import re
import sys
import urllib.request
import uuid
from pathlib import Path


def load_webhook_url(workspace_root: Path) -> str:
    env_url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if env_url:
        return env_url
    for env_file in [workspace_root / ".env", Path.home() / ".env"]:
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("DISCORD_WEBHOOK_URL="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
    raise ValueError("DISCORD_WEBHOOK_URL not found in .env or environment variables.")


def extract_caption_blocks(manuscript_path: Path) -> list[str]:
    if not manuscript_path.exists():
        return []
    text = manuscript_path.read_text(encoding="utf-8")
    blocks = [b.strip() for b in re.findall(r"```text\s*(.*?)\s*```", text, flags=re.DOTALL) if b.strip()]
    return blocks


def post_json(webhook_url: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "BeyondX-CardNews-Agent/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status


def post_multipart_files(webhook_url: str, payload: dict, file_paths: list[Path]):
    boundary = f"----BeyondXBoundary{uuid.uuid4().hex}"
    body = bytearray()

    # 1. payload_json part
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(b'Content-Disposition: form-data; name="payload_json"\r\n')
    body.extend(b"Content-Type: application/json\r\n\r\n")
    body.extend(json.dumps(payload).encode("utf-8"))
    body.extend(b"\r\n")

    # 2. files[i] parts
    for idx, fpath in enumerate(file_paths):
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(
            f'Content-Disposition: form-data; name="files[{idx}]"; filename="{fpath.name}"\r\n'.encode("utf-8")
        )
        body.extend(b"Content-Type: image/png\r\n\r\n")
        body.extend(fpath.read_bytes())
        body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        webhook_url,
        data=bytes(body),
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "BeyondX-CardNews-Agent/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.status


def send_card_news_to_discord(package_dir: Path):
    workspace_root = Path(__file__).resolve().parents[4]
    webhook_url = load_webhook_url(workspace_root)

    storyboard_path = package_dir / "storyboard.json"
    manuscript_path = package_dir / "manuscript.md"
    slides_dir = package_dir / "slides"

    storyboard = json.loads(storyboard_path.read_text(encoding="utf-8"))
    meta = storyboard.get("meta", {})
    title = meta.get("title", "오늘의 AI 카드뉴스")
    date_str = meta.get("date", "")

    slide_files = sorted(slides_dir.glob("slide_*.png"))
    if not slide_files:
        raise FileNotFoundError(f"No slide_*.png found in {slides_dir}")

    # 1. Send the 6 slide images in a single batch message
    header_payload = {
        "username": "BEYOND-X 카드뉴스 봇",
        "content": f"⚡ **[{date_str}] 오늘의 `@__beyondx__` 카드뉴스 6장 생성 완료!**\n**제목**: {title}\n*(아래 이미지를 순서대로 저장한 뒤, 다음 메시지의 본문 캡션을 복사해 인스타에 업로드하세요)*",
    }
    post_multipart_files(webhook_url, header_payload, slide_files[:10])
    print(f"[OK] Sent {len(slide_files)} slide images to Discord.")

    # 2. Send the Instagram caption (with max 5 targeted hashtags) and Threads copy in separate clean messages
    blocks = extract_caption_blocks(manuscript_path)
    if blocks:
        insta_caption = blocks[0]
        # Enforce Instagram 5-hashtag limit on hashtag lines
        caption_lines = insta_caption.splitlines()
        cleaned_lines = []
        for ln in caption_lines:
            tags = re.findall(r"#[^\s#]+", ln)
            if len(tags) > 5 and ln.strip().startswith("#"):
                ln = " ".join(tags[:5])
            cleaned_lines.append(ln)
        insta_caption = "\n".join(cleaned_lines)[:1950]
        post_json(
            webhook_url,
            {
                "username": "BEYOND-X 인스타 캡션 (복사용)",
                "content": insta_caption,
            },
        )
        print("[OK] Sent copy-ready Instagram caption to Discord.")

    if len(blocks) >= 2:
        threads_caption = blocks[1].strip()
        # Threads hard limit is 500 chars (including spaces, newlines, and multi-codepoint emojis).
        # Trim safely by paragraph/line if over 460 python chars so it never exceeds Threads' 500-char counter.
        if len(threads_caption) > 460:
            lines = threads_caption.splitlines()
            trimmed = []
            cur_len = 0
            for ln in lines:
                if cur_len + len(ln) + 1 > 460:
                    break
                trimmed.append(ln)
                cur_len += len(ln) + 1
            threads_caption = "\n".join(trimmed).strip()
        post_json(
            webhook_url,
            {
                "username": "BEYOND-X 스레드(Threads) 원고 (복사용)",
                "content": threads_caption,
            },
        )
        print(f"[OK] Sent copy-ready Threads post to Discord ({len(threads_caption)} chars).")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python send_discord.py <output/YYYYMMDD_slug>")
        sys.exit(1)
    send_card_news_to_discord(Path(sys.argv[1]))
