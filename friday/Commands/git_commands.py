"""
Git Commands — voice se git operations.
"""

import os
import subprocess
from friday.voice import speak


def run_git(args: list, cwd: str = None) -> tuple:
    """Git command run karo aur output return karo."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            cwd=cwd or os.getcwd(),
            timeout=30,
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1


def git_status():
    out, err, code = run_git(["status", "--short"])
    if code != 0:
        speak("Not a git repo, boss.")
        return
    if not out:
        speak("All clean, nothing to commit, boss.")
    else:
        lines = out.split('\n')
        speak(f"{len(lines)} files changed, boss. Check terminal.")
    print(f"📋 Git Status:\n{out or 'Clean'}")


def git_add_all():
    out, err, code = run_git(["add", "."])
    if code == 0:
        speak("All files staged, boss.")
        print("✅ git add .")
    else:
        speak("Staging failed, boss.")
        print(f"❌ Error: {err}")


def git_commit(message: str):
    out, err, code = run_git(["commit", "-m", message])
    if code == 0:
        speak(f"Committed — {message}, boss.")
        print(f"✅ Committed: {message}")
    else:
        speak("Commit failed, boss. Check terminal.")
        print(f"❌ Error: {err}")


def git_push():
    speak("Pushing to remote, boss.")
    out, err, code = run_git(["push"])
    if code == 0:
        speak("Pushed successfully, boss.")
        print("✅ git push done")
    else:
        speak("Push failed, boss. Check terminal.")
        print(f"❌ Error: {err}")


def git_pull():
    speak("Pulling from remote, boss.")
    out, err, code = run_git(["pull"])
    if code == 0:
        speak("Pulled successfully, boss.")
        print(f"✅ {out}")
    else:
        speak("Pull failed, boss.")
        print(f"❌ Error: {err}")


def git_log():
    out, err, code = run_git([
        "log", "--oneline", "-5"
    ])
    if code == 0:
        print(f"📋 Last 5 commits:\n{out}")
        lines = out.split('\n')
        speak(f"Last commit — {lines[0] if lines else 'none'}, boss.")
    else:
        speak("Couldn't get git log, boss.")


def git_branch():
    out, err, code = run_git(["branch", "--show-current"])
    if code == 0:
        speak(f"You're on branch {out}, boss.")
        print(f"🌿 Branch: {out}")
    else:
        speak("Couldn't get branch info, boss.")


def git_new_branch(name: str):
    out, err, code = run_git(["checkout", "-b", name])
    if code == 0:
        speak(f"New branch {name} created, boss.")
        print(f"✅ New branch: {name}")
    else:
        speak(f"Couldn't create branch {name}, boss.")
        print(f"❌ Error: {err}")


def git_checkout(branch: str):
    out, err, code = run_git(["checkout", branch])
    if code == 0:
        speak(f"Switched to {branch}, boss.")
        print(f"✅ Checkout: {branch}")
    else:
        speak(f"Couldn't switch to {branch}, boss.")
        print(f"❌ Error: {err}")


def git_diff():
    out, err, code = run_git(["diff", "--stat"])
    if out:
        print(f"📋 Git Diff:\n{out}")
        lines = out.split('\n')
        speak(f"{len(lines)} files changed. Check terminal, boss.")
    else:
        speak("No changes, boss.")


def handle_git_command(user_input: str) -> bool:
    u = user_input.lower().strip()

    # Git triggers check
    git_keywords = [
        "git", "commit", "push", "pull",
        "branch", "checkout", "stage",
        "repository", "repo",
    ]
    if not any(k in u for k in git_keywords):
        return False

    # Status
    if any(t in u for t in [
        "git status", "status check", "kya changes hain",
        "what changed", "git changes",
    ]):
        git_status()
        return True

    # Add all
    if any(t in u for t in [
        "git add", "stage all", "sab stage karo",
        "add all files", "stage karo",
    ]):
        git_add_all()
        return True

    # Commit
    if "commit" in u:
        import re
        # Message extract karo
        msg_match = re.search(
            r'commit\s+(?:karo\s+)?["\']?(.+?)["\']?$', u
        )
        if msg_match:
            message = msg_match.group(1).strip()
            # Common words remove karo
            for word in ["karo", "with message", "message"]:
                message = message.replace(word, "").strip()
            if message:
                git_commit(message)
            else:
                git_add_all()
                git_commit("Update")
        else:
            git_add_all()
            git_commit("Update")
        return True

    # Push
    if any(t in u for t in [
        "git push", "push karo", "push code",
        "upload code", "push to github",
    ]):
        git_push()
        return True

    # Pull
    if any(t in u for t in [
        "git pull", "pull karo", "pull code",
        "download changes", "pull from github",
    ]):
        git_pull()
        return True

    # Log
    if any(t in u for t in [
        "git log", "commits dikhao", "last commits",
        "commit history", "recent commits",
    ]):
        git_log()
        return True

    # Branch
    if any(t in u for t in [
        "current branch", "kaun sa branch",
        "branch kya hai", "which branch",
    ]):
        git_branch()
        return True

    # New branch
    if any(t in u for t in [
        "new branch", "create branch", "branch banao",
        "naya branch",
    ]):
        import re
        branch_match = re.search(
            r'branch\s+(?:banao\s+)?(?:named?\s+)?(\S+)$', u
        )
        if branch_match:
            name = branch_match.group(1).strip()
            git_new_branch(name)
        else:
            speak("Branch ka naam batao, boss.")
        return True

    # Checkout
    if "checkout" in u or "switch branch" in u:
        import re
        branch_match = re.search(r'(?:checkout|switch to|switch branch)\s+(\S+)$', u)
        if branch_match:
            branch = branch_match.group(1).strip()
            git_checkout(branch)
        else:
            speak("Kaunse branch pe jaana hai, boss?")
        return True

    # Diff
    if any(t in u for t in [
        "git diff", "kya badla", "what's different",
        "changes dikhao",
    ]):
        git_diff()
        return True

    # Add + Commit + Push — ek saath
    if any(t in u for t in [
        "save and push", "commit and push",
        "sab push karo", "deploy karo",
        "github pe daal do",
    ]):
        import re
        msg_match = re.search(r'(?:message|msg|commit)\s+["\']?(.+?)["\']?$', u)
        message = msg_match.group(1) if msg_match else "Update"
        git_add_all()
        git_commit(message)
        git_push()
        return True

    return False