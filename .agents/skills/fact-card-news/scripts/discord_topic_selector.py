#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord 5-Topic Candidate Sender & Interactive Reply Listener (with Option 6: Refresh).
1. Sends 5 verified news topic candidates + Option 6 (Refresh for 5 new topics) to Discord.
2. If DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID are present in .env, waits for
   the user to reply with '1'~'6' (or react with 1️⃣~6️⃣ / 🔄) in Discord and returns the choice.
   - Choice 1~5: Selected topic index
   - Choice 6: User requested 5 new topic candidates (SELECTED_CHOICE=6 / SELECTED_ACTION=REFRESH)

Usage:
  python .agents/skills/fact-card-news/scripts/discord_topic_selector.py <path/to/candidates.json> [wait_seconds]
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

NUM_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
REFRESH_EMOJIS = ["6️⃣", "🔄"]
ALL_REACTION_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]


def load_env(workspace_root: Path) -> dict:
    cfg = {
        "DISCORD_WEBHOOK_URL": os.environ.get("DISCORD_WEBHOOK_URL", "").strip(),
        "DISCORD_BOT_TOKEN": os.environ.get("DISCORD_BOT_TOKEN", "").strip(),
        "DISCORD_CHANNEL_ID": os.environ.get("DISCORD_CHANNEL_ID", "").strip(),
    }
    for env_file in [workspace_root / ".env", Path.home() / ".env"]:
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k in cfg and v and not cfg[k]:
                    cfg[k] = v
    return cfg


def format_candidates_message(data: dict) -> str:
    date_str = data.get("date", "오늘")
    round_no = data.get("round", 1)
    round_badge = f" (재추천 #{round_no})" if round_no and int(round_no) > 1 else ""
    candidates = data.get("candidates", [])
    lines = [
        f"📋 **[{date_str}] 오늘의 `@__beyondx__` AI·테크 카드뉴스 주제 후보 5선{round_badge}**",
        "제작할 주제 번호(`1` ~ `5`)를 선택하거나, 다른 주제를 원하시면 **`6` (다시 뽑기)**을 눌러주세요!\n",
    ]
    for idx, c in enumerate(candidates[:5], 1):
        emoji = NUM_EMOJIS[idx - 1]
        title = c.get("title", "")
        summary = c.get("summary", "")
        source = c.get("source", "")
        lines.append(f"{emoji} **{title}**")
        if summary:
            lines.append(f"   └ {summary}")
        if source:
            lines.append(f"   └ *출처: {source}*")
        lines.append("")
    lines.append("6️⃣ 🔄 **마음에 드는 주제가 없어요 (새로운 주제 5가지 다시 가져오기)**\n")
    lines.append("💬 **선택 방법**: 아래 이모지(1️⃣~6️⃣)를 누르거나 채팅창에 `1` ~ `6` 숫자를 입력해 주세요!")
    return "\n".join(lines)


def discord_api_request(method: str, endpoint: str, bot_token: str, payload: dict = None):
    url = f"https://discord.com/api/v10{endpoint}"
    headers = {
        "Authorization": f"Bot {bot_token}",
        "User-Agent": "BeyondX-CardNews-Agent/1.0",
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def send_via_webhook(webhook_url: str, content: str) -> dict:
    sep = "&" if "?" in webhook_url else "?"
    url = f"{webhook_url}{sep}wait=true"
    data = json.dumps({"username": "BEYOND-X 주제 선택 봇", "content": content[:1990]}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "BeyondX-CardNews-Agent/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def notify_choice(bot_token: str, channel_id: str, choice: int, suffix: str = ""):
    if choice == 6:
        msg = "🔄 **6번 (새로운 주제 다시 뽑기)**를 선택하셨습니다! 이전 후보와 겹치지 않는 새로운 AI·테크 주제 5가지를 다시 찾아서 보내드릴게요 🔍⏳"
    else:
        msg = f"✅ **{choice}번 주제**{suffix}가 선택되었습니다! 지금 바로 카드뉴스 6장 제작을 시작합니다 ⏳"
    discord_api_request("POST", f"/channels/{channel_id}/messages", bot_token, {"content": msg})


def poll_discord_choice(bot_token: str, channel_id: str, prompt_msg_id: str, wait_seconds: int = 1800) -> int:
    # Add 1️⃣~6️⃣ reactions onto the prompt message so user can 1-tap on mobile or PC
    for em in ALL_REACTION_EMOJIS:
        try:
            enc = urllib.parse.quote(em)
            discord_api_request(
                "PUT",
                f"/channels/{channel_id}/messages/{prompt_msg_id}/reactions/{enc}/@me",
                bot_token,
            )
            time.sleep(0.35)
        except Exception:
            pass

    print(f"[WAIT] Waiting up to {wait_seconds}s for user selection (1~6) in Discord channel {channel_id}...")
    deadline = time.time() + wait_seconds

    while time.time() < deadline:
        # 1. Check new text replies in channel after prompt_msg_id
        try:
            msgs = discord_api_request(
                "GET",
                f"/channels/{channel_id}/messages?after={prompt_msg_id}&limit=10",
                bot_token,
            )
            for m in reversed(msgs):
                if m.get("author", {}).get("bot"):
                    continue
                txt = m.get("content", "").strip()
                match = re.match(r"^[#]?([1-6])(?:\s*번)?$", txt)
                if match:
                    choice = int(match.group(1))
                    notify_choice(bot_token, channel_id, choice)
                    return choice
                if txt in ("다시", "새로고침", "리프레시", "다른 주제", "다른주제", "🔄"):
                    notify_choice(bot_token, channel_id, 6)
                    return 6
        except Exception as e:
            print(f"[WARN] Message poll error: {e}", file=sys.stderr)

        # 2. Check emoji reactions (1️⃣~6️⃣ or 🔄) on the prompt message
        try:
            msg_obj = discord_api_request(
                "GET",
                f"/channels/{channel_id}/messages/{prompt_msg_id}",
                bot_token,
            )
            for r in msg_obj.get("reactions", []):
                em_name = r.get("emoji", {}).get("name", "")
                if r.get("count", 0) > 1:
                    if em_name in NUM_EMOJIS:
                        choice = NUM_EMOJIS.index(em_name) + 1
                        notify_choice(bot_token, channel_id, choice, f"({em_name})")
                        return choice
                    if em_name in REFRESH_EMOJIS:
                        notify_choice(bot_token, channel_id, 6, f"({em_name})")
                        return 6
        except Exception:
            pass

        time.sleep(4)

    raise TimeoutError("Timed out waiting for topic selection in Discord.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python discord_topic_selector.py <candidates.json> [wait_seconds]")
        sys.exit(1)

    candidates_path = Path(sys.argv[1]).resolve()
    wait_seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 1800

    workspace_root = Path(__file__).resolve().parents[4]
    env = load_env(workspace_root)
    webhook_url = env["DISCORD_WEBHOOK_URL"]
    bot_token = env["DISCORD_BOT_TOKEN"]
    channel_id = env["DISCORD_CHANNEL_ID"]

    data = json.loads(candidates_path.read_text(encoding="utf-8"))
    content = format_candidates_message(data)

    prompt_msg_id = None
    if webhook_url:
        msg_info = send_via_webhook(webhook_url, content)
        prompt_msg_id = msg_info.get("id")
        if not channel_id:
            channel_id = msg_info.get("channel_id", "")
        print(f"[OK] Sent topic candidates via Webhook (msg_id={prompt_msg_id}, channel_id={channel_id})")
    elif bot_token and channel_id:
        msg_info = discord_api_request(
            "POST",
            f"/channels/{channel_id}/messages",
            bot_token,
            {"content": content[:1990]},
        )
        prompt_msg_id = msg_info.get("id")
        print(f"[OK] Sent topic candidates via Bot API (msg_id={prompt_msg_id})")
    else:
        raise ValueError("Neither DISCORD_WEBHOOK_URL nor DISCORD_BOT_TOKEN is configured in .env")

    if bot_token and channel_id and prompt_msg_id:
        choice = poll_discord_choice(bot_token, channel_id, prompt_msg_id, wait_seconds)
        out_sel = candidates_path.parent / "selected_topic.json"
        if choice == 6:
            result = {"selected_index": 6, "action": "REFRESH", "selected_topic": None}
            out_sel.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            print("SELECTED_CHOICE=6")
            print("SELECTED_ACTION=REFRESH")
        else:
            selected = data["candidates"][choice - 1]
            result = {"selected_index": choice, "action": "PROCEED", "selected_topic": selected}
            out_sel.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"SELECTED_CHOICE={choice}")
            print("SELECTED_ACTION=PROCEED")
            print(f"SELECTED_TITLE={selected.get('title')}")
    else:
        print("[INFO] DISCORD_BOT_TOKEN not set in .env; sent candidates via Webhook only.")


if __name__ == "__main__":
    main()
