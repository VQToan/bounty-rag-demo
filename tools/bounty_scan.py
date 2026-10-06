#!/usr/bin/env python3
"""Daily small-bounty scanner (GitHub API via gh CLI).

Finds fresh $-labeled issues, filters bot-farms, ranks by trust+fit.
Usage: .venv/bin/python tools/bounty_scan.py [--days 7] [--out reports/]
Zero cost. Uses authenticated gh API (5000 req/hr).
"""
import argparse
import json
import re
import subprocess
from datetime import date, datetime, timezone

AMOUNT_RE = re.compile(r"\$\s?(\d[\d,]*)")
BOT_RE = re.compile(r"watch|radar|upstream sync|sync:|skills?(-| )agent|mermail|bountic|pilot|onboard|verify.*pilot", re.I)
STACK = ("typescript", "python", "javascript")


def gh(*args):
    out = subprocess.run(["gh", "api", *args], capture_output=True, text=True, check=True)
    return json.loads(out.stdout or "{}")


def search(q, per_page=30):
    out = subprocess.run(
        ["gh", "search", "issues", q, "--sort", "created", "--order", "desc",
         "--limit", str(per_page), "--json",
         "repository,number,title,createdAt,commentsCount,url,labels,state"],
        capture_output=True, text=True, check=True)
    items = []
    for it in json.loads(out.stdout or "[]"):
        if (it.get("state") or "").upper() != "OPEN":
            continue
        items.append({
            "repository_url": "https://api.github.com/repos/" + it["repository"]["nameWithOwner"],
            "number": it["number"], "title": it["title"],
            "created_at": it["createdAt"], "comments": it.get("commentsCount", 0),
            "html_url": it["url"],
        })
    return items


def repo_meta(full_name, cache):
    if full_name not in cache:
        try:
            cache[full_name] = gh(f"repos/{full_name}", "--jq",
                                  "{stars: .stargazers_count, created: .created_at, lang: .language}")
        except subprocess.CalledProcessError:
            cache[full_name] = {}
    return cache[full_name]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--out", default="reports")
    ap.add_argument("--min", type=int, default=20)
    ap.add_argument("--max", type=int, default=500)
    a = ap.parse_args()

    queries = [
        "Bounty in:title state:open",  # $ filtered in Python ($ breaks search syntax)
        "Paid in:title state:open",
    ]
    seen, cands = set(), []
    for q in queries:
        for it in search(q):
            key = (it["repository_url"], it["number"])
            if key in seen:
                continue
            seen.add(key)
            m = AMOUNT_RE.search(it["title"] or "")
            if not m:
                continue
            amount = int(m.group(1).replace(",", ""))
            if not (a.min <= amount <= a.max):
                continue
            if BOT_RE.search(it["title"] or ""):
                continue
            created = datetime.fromisoformat(it["created_at"].replace("Z", "+00:00"))
            age_days = (datetime.now(timezone.utc) - created).days
            if age_days > a.days:
                continue
            repo = "/".join(it["repository_url"].rstrip("/").split("/")[-2:])
            cands.append({"repo": repo, "num": it["number"], "title": it["title"],
                          "created": str(created.date()), "age": age_days,
                          "comments": it["comments"], "amount": amount,
                          "url": it["html_url"]})

    cache, rows = {}, []
    for c in cands[:25]:
        meta = repo_meta(c["repo"], cache)
        stars = meta.get("stars") or 0
        rcreated = (meta.get("created") or "")[:10]
        try:
            repo_age = (date.today() - date.fromisoformat(rcreated)).days
        except ValueError:
            repo_age = 9999
        lang = (meta.get("lang") or "").lower()
        score, flags = 0, []
        score += 30 if c["age"] <= 2 else (15 if c["age"] <= 4 else 5)
        if stars >= 500:
            score += 25
        elif stars >= 100:
            score += 15
        elif stars >= 20:
            score += 5
        else:
            flags.append("LOW-STARS")
        if repo_age < 60:
            flags.append("NEW-ORG")
        else:
            score += 10
        if lang in STACK:
            score += 15
        if c["comments"] == 0:
            score += 5
            flags.append("UNTOUCHED")
        rows.append({**c, "stars": stars, "repo_age": repo_age, "lang": lang,
                     "score": score, "flags": ",".join(flags) or "-"})
    rows.sort(key=lambda r: -r["score"])

    lines = [f"# Bounty scan {date.today()} ({len(rows)} candidates)",
             "", "| $ | repo | issue | age | stars | org age | lang | cmt | score | flags |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['amount']} | {r['repo']} | [#{r['num']}]({r['url']}) {r['title'][:60]} "
                     f"| {r['age']}d | {r['stars']} | {r['repo_age']}d | {r['lang']} "
                     f"| {r['comments']} | {r['score']} | {r['flags']} |")
    lines += ["", "_Rule: only work after maintainer confirms funding in comments._"]
    import os
    os.makedirs(a.out, exist_ok=True)
    path = f"{a.out}/bounty-scan-{date.today()}.md"
    open(path, "w").write("\n".join(lines) + "\n")
    print(f"wrote {path} ({len(rows)} rows)")
    for r in rows[:10]:
        print(f"${r['amount']:>4} s{r['score']:>3} {r['repo']}#{r['num']} [{r['flags']}] {r['title'][:70]}")


if __name__ == "__main__":
    main()
