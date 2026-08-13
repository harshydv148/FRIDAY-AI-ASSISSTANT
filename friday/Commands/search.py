"""
Real-time Search — DuckDuckGo se live information.
"""

import threading
from friday.voice import speak
from friday.AI.chat import client


def web_search(query: str) -> str:
    """Search karo aur result return karo."""
    try:
        from ddgs import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))

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


def fetch_news() -> str:
    """BBC RSS se live headlines fetch karo."""
    try:
        import urllib.request
        import xml.etree.ElementTree as ET

        url = "http://feeds.bbci.co.uk/news/rss.xml"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            content = response.read()

        root = ET.fromstring(content)
        channel = root.find("channel")

        headlines = []
        for item in channel.findall("item")[:6]:
            title = item.find("title")
            desc = item.find("description")
            if title is not None:
                headline = title.text.strip()
                description = desc.text.strip() if desc is not None else ""
                headlines.append(f"- {headline}: {description}")

        if headlines:
            return "\n".join(headlines)
        return "No headlines found."

    except Exception as e:
        print(f"BBC RSS error: {e}")
        # Fallback to DuckDuckGo
        return web_search("top world news today")


def search_and_answer(query: str, is_news: bool = False):
    print(f"🔍 Searching: {query}")
    speak("Let me look that up, boss.")

    def _search():
        try:
            if is_news:
                results = fetch_news()
            else:
                results = web_search(query)

            if "failed" in results or "No results" in results:
                speak("Couldn't find anything, boss.")
                return

            # AI se natural answer banao
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
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
                        "content": f"Give me top news headlines from these results:\n\n{results}",
                    },
                ],
                max_tokens=150,
            )

            answer = response.choices[0].message.content.strip()
            print(f"🔍 Answer: {answer}")
            if answer:
                speak(answer)
            else:
                speak("Couldn't find relevant results, boss.")

        except Exception as e:
            print(f"Search answer error: {e}")
            speak("Couldn't get an answer, boss.")

    threading.Thread(target=_search, daemon=True).start()


def handle_search_command(user_input: str) -> bool:
    u = user_input.lower().strip()

    search_triggers = [
        "search for",
        "look up",
        "find out",
        "what is the latest",
        "current price",
        "live score",
        "news about",
        "tell me about",
        "who won",
        "what happened",
        "latest news",
        "search online",
        "google karo",
        "dhundho",
        "real time",
        "abhi kya",
        "aaj ka",
        "score kya hai",
        "price kya hai",
        "weather in",
        "stock price",
        "crypto price",
    ]

    # Direct search triggers
    # News specific commands pehle handle karo
    news_triggers = [
        "news batao",
        "news batana",
        "news chahiye",
        "aaj ki khabar",
        "latest news",
        "news kya hai",
        "top news",
        "headlines",
        "khabar batao",
    ]
    if any(t in u for t in news_triggers):
        search_and_answer("news", is_news=True)
        return True

    if any(t in u for t in search_triggers):
        query = u
        for t in [
            "search for",
            "look up",
            "find out",
            "search online",
            "google karo",
            "dhundho",
            "friday",
            "tell me about",
        ]:
            query = query.replace(t, "").strip()

        if query:
            if any(n in query for n in ["news", "latest", "today", "aaj"]):
                query = "top world news headlines today 2026"
            search_and_answer(query)
            return True

    # Question words — real time info chahiye
    real_time_hints = [
        "score",
        "price",
        "weather",
        "news",
        "stock",
        "crypto",
        "bitcoin",
        "ipl",
        "match",
        "election",
        "result",
        "winner",
        "latest",
        "current",
        "rate",
        "value",
    ]

    if any(hint in u for hint in real_time_hints):
        search_and_answer(user_input)
        return True

    return False
