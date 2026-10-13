from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.postgres import PostgresSaver
from dotenv import load_dotenv
from datetime import datetime
import random, json, math, os, urllib.request, urllib.parse

load_dotenv()

DB_URI         = os.getenv("SUPABASE_DB_URI")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

# ═══════════════════════════════════════════════════════════════
#  TOOLS
# ═══════════════════════════════════════════════════════════════

# ── Text tasks ────────────────────────────────────────────────

def summarize_text(text: str) -> str:
    """Summarize a long piece of text into key points. Pass the full text to summarize."""
    return f"[SUMMARIZE THIS TEXT]\n{text}"

def improve_text(text: str, goal: str = "clarity") -> str:
    """Rewrite and improve text. goal can be: clarity, professional, concise, creative, formal."""
    return f"[IMPROVE THIS TEXT - Goal: {goal}]\n{text}"

def translate_text(text: str, target_language: str) -> str:
    """Translate text to the given target language."""
    return f"[TRANSLATE TO {target_language.upper()}]\n{text}"

def extract_key_points(text: str) -> str:
    """Extract key points and action items from notes or documents."""
    return f"[EXTRACT KEY POINTS AND ACTION ITEMS]\n{text}"

def analyze_sentiment(text: str) -> str:
    """Analyze the sentiment of text. Returns positive, negative, neutral with reasoning."""
    return f"[ANALYZE SENTIMENT - return JSON with: sentiment, confidence, reasoning]\n{text}"

# ── Reasoning & analysis ──────────────────────────────────────

def explain_concept(concept: str, level: str = "simple") -> str:
    """Explain a complex concept. level can be: simple, intermediate, expert."""
    return f"[EXPLAIN '{concept}' at {level} level with examples]"

def compare_things(item_a: str, item_b: str, criteria: str = "") -> str:
    """Compare two things side by side. Optionally specify criteria to compare on."""
    return f"[COMPARE '{item_a}' vs '{item_b}' — criteria: {criteria or 'general'}]"

def pros_and_cons(topic: str) -> str:
    """Give a balanced pros and cons analysis of a topic or decision."""
    return f"[PROS AND CONS ANALYSIS for: {topic}]"

# ── Creative ──────────────────────────────────────────────────

def write_creative(type: str, topic: str, style: str = "") -> str:
    """Write creative content. type: story, poem, script, product_description, blog_post. topic: what to write about. style: optional style hint."""
    return f"[WRITE A {type.upper()} about '{topic}' — style: {style or 'engaging'}]"

def brainstorm(topic: str, count: int = 10) -> str:
    """Brainstorm ideas on any topic. Returns a numbered list."""
    return f"[BRAINSTORM {count} creative ideas for: {topic}]"

def generate_quiz(topic: str, num_questions: int = 5, difficulty: str = "medium") -> str:
    """Generate quiz questions with answers on a topic. difficulty: easy, medium, hard."""
    return f"[GENERATE {num_questions} {difficulty.upper()} quiz questions with answers about: {topic}]"

# ── Structured output ─────────────────────────────────────────

def parse_to_json(text: str, schema_hint: str = "") -> str:
    """Parse unstructured text into structured JSON. Optionally provide a schema hint."""
    return f"[PARSE TO JSON{' — schema: ' + schema_hint if schema_hint else ''}]\n{text}"

def fill_template(template: str, raw_input: str) -> str:
    """Fill a template using raw input data. Provide the template with {{placeholders}} and raw input."""
    return f"[FILL TEMPLATE]\nTemplate: {template}\nRaw input: {raw_input}"

def generate_report(bullet_points: str, report_type: str = "summary") -> str:
    """Generate a structured report from bullet points. report_type: summary, detailed, executive."""
    return f"[GENERATE {report_type.upper()} REPORT from these points]\n{bullet_points}"

# ── Tools with real logic ─────────────────────────────────────

def generate_image(prompt: str, width: int = 768, height: int = 512, model: str = "flux") -> str:
    """Generate an image from a text prompt using AI. Returns the image URL.
    model options: flux (best quality), turbo (fastest), stable-diffusion.
    width and height should be multiples of 64, max 1024."""
    import urllib.parse
    encoded = urllib.parse.quote(prompt)
    seed    = random.randint(1, 99999)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={width}&height={height}&model={model}&seed={seed}&nologo=true&enhance=true"
    )
    # Return a special marker the app uses to render it as an image
    return f"IMAGE_URL:{url}"

def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely. Examples: '2 + 2', 'sqrt(144)', '15% of 200'."""
    try:
        # Handle percentage expressions like "15% of 200"
        if "% of" in expression:
            parts = expression.split("% of")
            result = (float(parts[0].strip()) / 100) * float(parts[1].strip())
            return str(result)
        # Safe math eval
        allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith('_')}
        allowed['abs'] = abs
        result = eval(expression.replace('^', '**'), {"__builtins__": {}}, allowed)
        return str(result)
    except Exception as e:
        return f"Could not calculate: {e}"

def web_search(query: str) -> str:
    """Search the web for current information using DuckDuckGo. Returns top results."""
    try:
        encoded = urllib.parse.quote(query)
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_redirect=1&no_html=1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())

        results = []
        if data.get("AbstractText"):
            results.append(f"Summary: {data['AbstractText']}")
        for topic in data.get("RelatedTopics", [])[:4]:
            if isinstance(topic, dict) and topic.get("Text"):
                results.append(f"• {topic['Text']}")

        return "\n".join(results) if results else f"No direct results found for: {query}. Try rephrasing."
    except Exception as e:
        return f"Search failed: {e}"

def get_current_time() -> str:
    """Return the current date and time."""
    return datetime.now().strftime("%A, %B %d %Y – %I:%M %p")

def get_word_count(text: str) -> str:
    """Count words, characters, sentences and reading time of text."""
    words     = len(text.split())
    chars     = len(text)
    sentences = text.count('.') + text.count('!') + text.count('?')
    read_time = max(1, round(words / 200))
    return json.dumps({
        "words": words,
        "characters": chars,
        "sentences": sentences,
        "estimated_reading_time_minutes": read_time
    })

# ── Small talk extras ─────────────────────────────────────────

def tell_joke() -> str:
    """Tell a short, clean joke."""
    return random.choice([
        "Why don't scientists trust atoms? Because they make up everything.",
        "Why did the scarecrow win an award? He was outstanding in his field.",
        "Why do cows wear bells? Because their horns don't work.",
        "I'm reading a book about anti-gravity. It's impossible to put down.",
    ])

def get_fun_fact() -> str:
    """Return a random fun fact."""
    return random.choice([
        "Honey never spoils — 3000-year-old honey was found still edible in Egyptian tombs.",
        "A group of flamingos is called a flamboyance.",
        "Octopuses have three hearts and blue blood.",
        "Bananas are technically berries, but strawberries are not.",
        "Wombat poop is cube-shaped.",
    ])

# ═══════════════════════════════════════════════════════════════
#  LLM + AGENT FACTORY
# ═══════════════════════════════════════════════════════════════

llm = ChatOpenAI(
    model="gemma4:31b",
    base_url="https://ollama.com/v1",
    api_key=OLLAMA_API_KEY,
)

SYSTEM_PROMPT = """
You are Aria — a highly capable assistant. You handle a wide range of tasks:

TEXT TASKS: Summarize, improve, translate, extract key points, analyze sentiment.
REASONING:  Explain concepts, compare things, give pros/cons.
CREATIVE:   Write stories/poems/scripts, brainstorm, create quizzes.
STRUCTURED: Parse text to JSON, fill templates, generate reports.
TOOLS:      Search the web, calculate math, count words, tell the time.
IMAGES:     Generate images from text descriptions using generate_image tool.

RULES:
- Always use the most appropriate tool for the task.
- For image requests, ALWAYS call generate_image() and return ONLY the result (IMAGE_URL:...) with a brief description. Do NOT add extra text after the IMAGE_URL line.
- For summarize/improve/translate/extract/sentiment tasks, call the tool then produce the actual result.
- For structured output (JSON, reports), format the response cleanly with proper markdown.
- Keep responses focused and well-formatted. Use markdown headers and bullets where helpful.
- Remember the user's name and preferences across the conversation.
"""

ALL_TOOLS = [
    # Text
    summarize_text, improve_text, translate_text, extract_key_points, analyze_sentiment,
    # Reasoning
    explain_concept, compare_things, pros_and_cons,
    # Creative
    write_creative, brainstorm, generate_quiz,
    # Structured
    parse_to_json, fill_template, generate_report,
    # Tool-based
    generate_image, calculate, web_search, get_current_time, get_word_count,
    # Fun
    tell_joke, get_fun_fact,
]

def get_agent(checkpointer):
    return create_agent(
        model=llm,
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )
