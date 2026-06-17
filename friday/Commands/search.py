"""
Real-time Search — DuckDuckGo se live information.
"""

import threading
from friday.voice import speak
from friday.AI.chat import client


def web_search(query: str) -> str:
    """DuckDuckGo se search karo aur result return karo."""
    try:
        from ddgs import DDGS

        with DDGS() as ddgs:
            # News query hai toh news search use karo
            if any(n in query.lower() for n in [
                "news", "latest", "today", "headlines",
                "score", "result", "winner"
            ]):
                results = list(ddgs.news(query, max_results=5))
                if results:
                    context = ""
                    for r in results:
                        context += f"Title: {r['title']}\n"
                        context += f"Source: {r.get('source', '')}\n"
                        context += f"Summary: {r.get('body', r.get('excerpt', ''))}\n\n"
                    return context

            # Normal search
            results = list(ddgs.text(query, max_results=3))
            if not results:
                return "No results found."

            context = ""
            for r in results:
                context += f"Title: {r['title']}\n"
                context += f"Info: {r['body']}\n\n"

            return context

    except Exception as e:
        print(f"Search error: {e}")
        return "Search failed."


def search_and_answer(query: str):
    """Search karo aur AI se natural answer banao."""
    print(f"🔍 Searching: {query}")
    speak("Let me look that up, boss.")

    def _search():
        try:
            results = web_search(query)

            if "failed" in results or "No results" in results:
                speak("Couldn't find anything, boss.")
                return

            # AI se natural answer banao
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are FRIDAY, a smart assistant. "
                            "Extract the TOP 3 most important and interesting news headlines from the search results. "
                            "Present them naturally as: 'Here are the top stories boss — [story 1], [story 2], and [story 3].' "
                            "Focus on major events — politics, sports, technology, world news. "
                            "Skip religious, regional, or trivial stories. "
                            "2-3 sentences max. No markdown. English only."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Give me top news headlines from these results:\n\n{results}"
                    }
                ],
                max_tokens=150,
            )

            answer = response.choices[0].message.content.strip()
            print(f"🔍 Answer: {answer}")
            speak(answer)

        except Exception as e:
            print(f"Search answer error: {e}")
            speak("Couldn't get an answer, boss.")

    threading.Thread(target=_search, daemon=True).start()


def handle_search_command(user_input: str) -> bool:
    u = user_input.lower().strip()

    search_triggers = [
        "search for", "look up", "find out",
        "what is the latest", "current price",
        "live score", "news about", "tell me about",
        "who won", "what happened", "latest news",
        "search online", "google karo", "dhundho",
        "real time", "abhi kya", "aaj ka",
        "score kya hai", "price kya hai",
        "weather in", "stock price", "crypto price",
    ]

    # Direct search triggers
    if any(t in u for t in search_triggers):
        query = u
        for t in [
            "search for", "look up", "find out",
            "search online", "google karo", "dhundho",
            "friday", "tell me about",
        ]:
            query = query.replace(t, "").strip()

        if query:
            # News query improve karo
            if any(n in query for n in ["news", "latest", "today", "aaj"]):
                query = "top world news headlines today June 2026"
            search_and_answer(query)
            return True

    # Question words — real time info chahiye
    real_time_hints = [
        "score", "price", "weather", "news",
        "stock", "crypto", "bitcoin", "ipl",
        "match", "election", "result", "winner",
        "latest", "current", "today", "abhi",
        "rate", "value",
    ]

    if any(hint in u for hint in real_time_hints):
        search_and_answer(user_input)
        return True

    return False    