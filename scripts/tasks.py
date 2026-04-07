#!/usr/bin/env python3
"""Persistent task tracking CLI — JSON-backed, survives session end.

Usage:
    python3 scripts/tasks.py list
    python3 scripts/tasks.py add "Fix auth bug" --priority high
    python3 scripts/tasks.py update 1 done
    python3 scripts/tasks.py update 1 in_progress
    python3 scripts/tasks.py blocked-by 1 2
    python3 scripts/tasks.py show 1
    python3 scripts/tasks.py clear-done
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

TASKS_FILE = Path(__file__).resolve().parent.parent / "1shot" / "tasks.json"


def load_tasks() -> dict:
    if TASKS_FILE.exists():
        with open(TASKS_FILE) as f:
            return json.load(f)
    return {"version": 1, "tasks": []}


def save_tasks(data: dict) -> None:
    TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TASKS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def next_id(data: dict) -> str:
    if not data["tasks"]:
        return "1"
    return str(max(int(t["id"]) for t in data["tasks"]) + 1)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cmd_list(args):
    data = load_tasks()
    tasks = data["tasks"]
    if not tasks:
        print("No tasks.")
        return
    status_order = {"in_progress": 0, "pending": 1, "done": 2, "blocked": 3}
    tasks.sort(key=lambda t: (status_order.get(t["status"], 99), int(t["id"])))
    for t in tasks:
        blocked = f" (blocked by: {','.join(t.get('blocked_by', []))})" if t.get("blocked_by") else ""
        marker = {"in_progress": ">", "pending": " ", "done": "x", "blocked": "!"}.get(t["status"], "?")
        print(f" [{marker}] #{t['id']} {t['subject']}{blocked}")


def cmd_add(args):
    data = load_tasks()
    tid = next_id(data)
    task = {
        "id": tid,
        "subject": args.title,
        "description": args.description or "",
        "status": "pending",
        "priority": args.priority or "medium",
        "created": now_iso(),
        "updated": now_iso(),
        "blocked_by": [],
    }
    data["tasks"].append(task)
    save_tasks(data)
    print(f"Added #{tid}: {args.title}")


def cmd_update(args):
    data = load_tasks()
    for t in data["tasks"]:
        if t["id"] == args.task_id:
            t["status"] = args.status
            t["updated"] = now_iso()
            save_tasks(data)
            print(f"Updated #{args.task_id}: {args.status}")
            return
    print(f"Task #{args.task_id} not found.", file=sys.stderr)
    sys.exit(1)


def cmd_blocked_by(args):
    data = load_tasks()
    target = None
    for t in data["tasks"]:
        if t["id"] == args.task_id:
            target = t
            break
    if not target:
        print(f"Task #{args.task_id} not found.", file=sys.stderr)
        sys.exit(1)
    blockers = [b for b in args.blockers if b != args.task_id]
    target["blocked_by"] = blockers
    target["updated"] = now_iso()
    save_tasks(data)
    print(f"#{args.task_id} blocked by: {', '.join(blockers)}")


def cmd_show(args):
    data = load_tasks()
    for t in data["tasks"]:
        if t["id"] == args.task_id:
            print(f"#{t['id']} [{t['status']}] {t['subject']}")
            print(f"  Priority: {t['priority']}")
            print(f"  Created: {t['created']}")
            print(f"  Updated: {t['updated']}")
            if t.get("description"):
                print(f"  Description: {t['description']}")
            if t.get("blocked_by"):
                print(f"  Blocked by: {', '.join(t['blocked_by'])}")
            return
    print(f"Task #{args.task_id} not found.", file=sys.stderr)
    sys.exit(1)


def cmd_clear_done(args):
    data = load_tasks()
    before = len(data["tasks"])
    data["tasks"] = [t for t in data["tasks"] if t["status"] != "done"]
    removed = before - len(data["tasks"])
    save_tasks(data)
    print(f"Cleared {removed} completed task(s). {len(data['tasks'])} remaining.")


def main():
    parser = argparse.ArgumentParser(description="Persistent task tracking")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List all tasks")

    add_p = sub.add_parser("add", help="Add a task")
    add_p.add_argument("title", help="Task title")
    add_p.add_argument("--description", "-d", default="")
    add_p.add_argument("--priority", "-p", choices=["high", "medium", "low"], default="medium")

    upd_p = sub.add_parser("update", help="Update task status")
    upd_p.add_argument("task_id", help="Task ID")
    upd_p.add_argument("status", choices=["pending", "in_progress", "done", "blocked"])

    blk_p = sub.add_parser("blocked-by", help="Set task blockers")
    blk_p.add_argument("task_id", help="Task ID")
    blk_p.add_argument("blockers", nargs="+", help="Blocking task IDs")

    sub.add_parser("show", help="Show task details").add_argument("task_id")

    sub.add_parser("clear-done", help="Remove completed tasks")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "list": cmd_list,
        "add": cmd_add,
        "update": cmd_update,
        "blocked-by": cmd_blocked_by,
        "show": cmd_show,
        "clear-done": cmd_clear_done,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
