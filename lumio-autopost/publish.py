#!/usr/bin/env python3
"""Schedules Lumio posts into Buffer's X queue without X API credits."""
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

API = "https://api.buffer.com"
TZ = ZoneInfo("Asia/Kolkata")
START = date(2026, 10, 23)
SLOTS = (9, 14, 19)
MAX_QUEUE = 10


def gql(query, variables=None):
    key = os.environ["BUFFER_API_KEY"].strip()
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            obj = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        raise RuntimeError("Buffer HTTP error: " + str(exc.code)) from exc
    if obj.get("errors"):
        raise RuntimeError("Buffer: " + "; ".join(
            e.get("message", "Unknown error") for e in obj["errors"]))
    if not isinstance(obj.get("data"), dict):
        raise RuntimeError("Missing Buffer data")
    return obj["data"]


def get_channel():
    orgs = gql("query { account { organizations { id name } } }")["account"]["organizations"]
    candidates = []
    for org in orgs:
        query = ("query { channels(input: { organizationId: " +
                 json.dumps(org["id"]) +
                 " }) { id name displayName service isQueuePaused } }")
        for ch in gql(query)["channels"]:
            if str(ch["service"]).lower() in ("twitter", "x"):
                candidates.append((org["id"], ch))
    configured = os.environ.get("BUFFER_CHANNEL_ID", "").strip()
    if configured:
        matches = [(o, c) for o, c in candidates if c["id"] == configured]
    else:
        matches = [(o, c) for o, c in candidates if "lumiolearn" in
                   (str(c.get("name", "")) + str(c.get("displayName", ""))).lower().replace("@", "")]
        if not matches and len(candidates) == 1:
            matches = candidates
    if len(matches) != 1:
        raise RuntimeError("Unable to select one X account. Set GitHub Actions variable BUFFER_CHANNEL_ID.")
    org, ch = matches[0]
    if ch.get("isQueuePaused"):
        raise RuntimeError("Buffer queue is paused; resume it first")
    print("Selected X channel: " + str(ch.get("displayName") or ch.get("name")))
    return org, ch["id"]


def existing_posts(org, channel):
    query = ("query { posts(first: 50, input: {organizationId: " +
             json.dumps(org) + ", filter: {status: [scheduled], channelIds: [" +
             json.dumps(channel) + "]}}) { edges { node { id dueAt } } "
             "pageInfo {hasNextPage} } }")
    page = gql(query)["posts"]
    if page["pageInfo"]["hasNextPage"]:
        raise RuntimeError("Unexpectedly large scheduled queue")
    return [edge["node"] for edge in page["edges"]]


def create_post(channel, content, when):
    query = """
    mutation Schedule($input: CreatePostInput!) {
      createPost(input: $input) {
        ... on PostActionSuccess { post { id dueAt } }
        ... on MutationError { message }
      }
    }"""
    values = {"input": {"channelId": channel, "text": content,
                        "schedulingType": "automatic", "mode": "customScheduled",
                        "dueAt": when.astimezone(timezone.utc).isoformat(
                            timespec="milliseconds").replace("+00:00", "Z")}}
    result = gql(query, values)["createPost"]
    if not result.get("post"):
        raise RuntimeError("Buffer rejected post: " + result.get("message", "Unknown reason"))
    return result["post"]["id"]


def run():
    posts = json.loads(Path(__file__).with_name("posts.json").read_text(encoding="utf-8"))
    if not isinstance(posts, list) or not posts:
        raise RuntimeError("Missing posts.json list")
    for idx, txt in enumerate(posts):
        if not isinstance(txt, str) or not (1 <= len(txt) <= 280):
            raise RuntimeError("Post #" + str(idx + 1) + " must be 1 to 280 characters")
    now = datetime.now(TZ)
    upcoming = []
    for ahead in range(5):
        d = now.date() + timedelta(days=ahead)
        day_idx = (d - START).days
        if day_idx < 0:
            continue
        for slot_idx, hour in enumerate(SLOTS):
            idx = day_idx * len(SLOTS) + slot_idx
            when = datetime.combine(d, time(hour=hour), tzinfo=TZ)
            if idx < len(posts) and when > now + timedelta(minutes=15):
                upcoming.append((when, posts[idx]))

    if "--dry-run" in sys.argv:
        for when, post in upcoming[:9]:
            print("[DRY RUN]", when.isoformat(), post)
        return

    if not os.environ.get("BUFFER_API_KEY", "").strip():
        raise RuntimeError("Missing GitHub Actions secret BUFFER_API_KEY")
    org, channel = get_channel()
    scheduled = existing_posts(org, channel)
    occupied = set()
    for post in scheduled:
        if post.get("dueAt"):
            value = datetime.fromisoformat(post["dueAt"].replace("Z", "+00:00"))
            occupied.add(value.astimezone(timezone.utc).replace(second=0, microsecond=0))
    created = 0
    for when, content in upcoming:
        key = when.astimezone(timezone.utc).replace(second=0, microsecond=0)
        if key in occupied:
            continue
        if len(scheduled) + created >= MAX_QUEUE:
            break
        post_id = create_post(channel, content, when)
        print("Scheduled", when.isoformat(), "post", post_id)
        occupied.add(key)
        created += 1
    print("Finished:", created, "new posts;", len(scheduled) + created, "queued")
    if not upcoming:
        print("Content bank has ended. Append fresh posts to posts.json.")


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        print("::error::" + str(exc), file=sys.stderr)
        sys.exit(1)
