"""
To-Do List — task management.
"""

import os
import json
from datetime import datetime
from friday.voice import speak

TODO_FILE = "friday_todos.json"


def load_todos() -> list:
    try:
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_todos(todos: list):
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=4, ensure_ascii=False)


def add_todo(task: str):
    todos = load_todos()
    entry = {
        "id": len(todos) + 1,
        "task": task,
        "done": False,
        "created": datetime.now().strftime("%d %b %Y %H:%M"),
    }
    todos.append(entry)
    save_todos(todos)
    print(f"✅ Todo added: {task}")
    speak(f"Added to your list, boss.")


def show_todos():
    todos = load_todos()
    pending = [t for t in todos if not t["done"]]

    if not pending:
        speak("Nothing on your list, boss. All clear!")
        return

    print("\n📋 Your To-Do List:")
    for t in pending:
        print(f"  [{t['id']}] {t['task']}")

    if len(pending) == 1:
        speak(f"One thing on your list — {pending[0]['task']}")
    else:
        speak(f"{len(pending)} things pending boss. First up — {pending[0]['task']}")


def complete_todo(task_query: str):
    todos = load_todos()
    found = False

    for todo in todos:
        if not todo["done"] and task_query.lower() in todo["task"].lower():
            todo["done"] = True
            found = True
            save_todos(todos)
            print(f"✅ Done: {todo['task']}")
            speak(f"Marked as done, boss.")
            break

    if not found:
        # Number se bhi dhundho
        try:
            num = int(task_query)
            for todo in todos:
                if todo["id"] == num and not todo["done"]:
                    todo["done"] = True
                    save_todos(todos)
                    speak(f"Done, boss.")
                    return
        except:
            pass
        speak(f"Couldn't find that task, boss.")


def delete_todo(task_query: str):
    todos = load_todos()
    original_len = len(todos)

    # Number se delete
    try:
        num = int(task_query)
        todos = [t for t in todos if t["id"] != num]
    except:
        # Name se delete
        todos = [
            t for t in todos
            if task_query.lower() not in t["task"].lower()
        ]

    if len(todos) < original_len:
        save_todos(todos)
        speak("Removed from your list, boss.")
    else:
        speak("Couldn't find that task, boss.")


def clear_todos():
    save_todos([])
    speak("List cleared, boss.")


def show_completed():
    todos = load_todos()
    done = [t for t in todos if t["done"]]

    if not done:
        speak("Nothing completed yet, boss.")
        return

    print("\n✅ Completed Tasks:")
    for t in done:
        print(f"  [✓] {t['task']}")

    speak(f"{len(done)} tasks completed, boss.")


def handle_todo_command(user_input: str) -> bool:
    u = user_input.lower().strip()

    # Show completed
    if any(t in u for t in [
        "completed tasks", "done tasks", "finished tasks",
        "kya complete kiya", "completed list",
    ]):
        show_completed()
        return True

    # Clear all
    if any(t in u for t in [
        "clear todo", "clear list", "todo clear",
        "saari tasks delete", "all tasks delete",
        "clear all tasks", "empty list",
    ]):
        clear_todos()
        return True

    # Show todos
    if any(t in u for t in [
        "show todo", "todo list", "my tasks",
        "task list", "pending tasks", "kya karna hai",
        "todo dikhao", "tasks dikhao", "meri list",
        "what's on my list", "show tasks", "show my list",
    ]):
        show_todos()
        return True

    # Complete task
    if any(t in u for t in [
        "complete", "done", "finish", "mark done",
        "task complete", "ho gaya", "kar liya",
        "completed", "finished",
    ]):
        # Task extract karo
        content = u
        for t in ["complete", "done", "finish", "mark done",
                  "ho gaya", "kar liya", "completed", "finished"]:
            content = content.replace(t, "").strip()
        content = content.replace("task", "").strip()

        if content:
            complete_todo(content)
        else:
            speak("Which task, boss?")
        return True

    # Delete task
    if any(t in u for t in [
        "delete task", "remove task", "task delete",
        "task remove", "task hatao",
    ]):
        content = u
        for t in ["delete task", "remove task", "task delete",
                  "task remove", "task hatao"]:
            content = content.replace(t, "").strip()
        if content:
            delete_todo(content)
        else:
            speak("Which task to delete, boss?")
        return True

    # Add task
    add_triggers = [
        "add task", "todo add", "task add",
        "add to list", "add todo", "todo karo",
        "task hai", "karna hai", "remind karna",
        "list mein add", "add it to my list",
    ]

    for trigger in add_triggers:
        if trigger in u:
            content = u
            for t in add_triggers:
                content = content.replace(t, "").strip()
            content = content.replace("friday", "").strip()
            if content:
                add_todo(content)
            else:
                speak("What's the task, boss?")
            return True

    return False