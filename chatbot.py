"""
chatbot.py
==========
A simple, modular, text-based dialogue assistant built for a university project.

Architecture:
  - NLU  (Natural Language Understanding) : keyword-based intent detection
  - DM   (Dialogue Manager)               : frame / form-filling slot tracker
  - NLG  (Natural Language Generation)    : template-based response builder
  - Mock Data Layer                       : fake weather / restaurant / bus data

To add a NEW domain later, follow the three steps marked with  # [EXTENSIBILITY]
"""

import random
import re
from datetime import datetime, timedelta


# =============================================================================
# 1. CONFIGURATION  –  Intents & Slots
# =============================================================================

# [EXTENSIBILITY] Step 1:
# Add a new entry here to register a new intent.
# Keys:
#   "keywords"  – any of these words found in the user's text trigger this intent
#   "slots"     – ordered list of slot names that must be filled before answering
#   "handler"   – the function that produces the final answer (defined in §4)

INTENT_CONFIG = {
    "weather": {
        "keywords": [
            "weather", "forecast", "rain", "temperature", "sunny",
            "cloudy", "wind", "humid", "cold", "hot", "snow",
            "هوا", "آب و هوا", "باران", "دما", "برف", "آفتاب",
        ],
        "slots": ["city", "date"],
        "handler": "handle_weather",
    },
    "restaurant": {
        "keywords": [
            "restaurant", "eat", "food", "lunch", "dinner", "hungry",
            "cafe", "dine", "meal", "cuisine",
            "رستوران", "غذا", "ناهار", "شام", "گرسنه", "کافه",
        ],
        "slots": ["cuisine", "neighborhood"],
        "handler": "handle_restaurant",
    },
    "bus": {
        "keywords": [
            "bus", "tram", "transit", "schedule", "next bus", "departure",
            "stop", "route", "transport",
            "اتوبوس", "تراموا", "ایستگاه", "خط", "حرکت", "برنامه زمانی",
        ],
        "slots": ["stop_name", "direction"],
        "handler": "handle_bus",
    },
    # [EXTENSIBILITY] Add more intents below, e.g.:
    # "hotel": {
    #     "keywords": ["hotel", "accommodation", "room", "stay"],
    #     "slots": ["city", "check_in", "guests"],
    #     "handler": "handle_hotel",
    # },
}

# ---- Slot prompt messages ------------------------------------------------
# When the chatbot needs to fill a slot it uses these questions.
# [EXTENSIBILITY] Step 2: add slot prompts for any new slot names you create.

SLOT_PROMPTS = {
    # Weather slots
    "city": "Which city? (e.g. Tehran, Berlin, Paris)",
    "date": "For which date? (e.g. today, tomorrow, 2024-12-01)",
    # Restaurant slots
    "cuisine": "What type of cuisine? (e.g. Italian, Persian, Japanese)",
    "neighborhood": "In which neighborhood or area?",
    # Bus / Tram slots
    "stop_name": "What is the name of the bus/tram stop?",
    "direction": "Which direction? (e.g. north, city-center, airport)",
}


# =============================================================================
# 2. MOCK DATA LAYER  –  Simulated back-end responses
# =============================================================================

def get_weather(city: str, date: str) -> dict:
    """Return fake weather data for any city and date."""
    conditions = ["Sunny", "Partly Cloudy", "Rainy", "Windy", "Snowy", "Foggy"]
    return {
        "city": city.title(),
        "date": date,
        "condition": random.choice(conditions),
        "temperature_c": random.randint(-5, 38),
        "humidity_pct": random.randint(20, 95),
    }


def get_restaurants(cuisine: str, neighborhood: str) -> list[dict]:
    """Return a list of 3 fake restaurant suggestions."""
    mock_names = [
        "The Golden Fork", "Bella Napoli", "Saffron Kitchen",
        "Dragon Palace", "Le Petit Bistro", "Tandoori Nights",
        "Green Garden Cafe", "The Rustic Spoon", "Ocean Blue",
    ]
    random.shuffle(mock_names)
    results = []
    for i in range(3):
        results.append({
            "name": mock_names[i],
            "cuisine": cuisine.title(),
            "neighborhood": neighborhood.title(),
            "rating": round(random.uniform(3.0, 5.0), 1),
            "wait_minutes": random.choice([5, 10, 15, 20, 30]),
        })
    return results


def get_next_buses(stop_name: str, direction: str) -> list[dict]:
    """Return the next 3 departure times from a given stop."""
    now = datetime.now()
    departures = []
    delta = random.randint(3, 12)          # first bus arrives in 3-12 minutes
    for i in range(3):
        dep_time = now + timedelta(minutes=delta)
        departures.append({
            "line": f"Line {random.randint(1, 99)}",
            "stop": stop_name.title(),
            "direction": direction.title(),
            "departs_at": dep_time.strftime("%H:%M"),
            "minutes_away": delta,
        })
        delta += random.randint(8, 20)     # space subsequent buses apart
    return departures


# =============================================================================
# 3. NLU  –  Intent Detection via Keyword Matching
# =============================================================================

def detect_intent(user_text: str) -> str | None:
    """
    Scan the user's message for keywords defined in INTENT_CONFIG.

    Returns the matched intent name (e.g. "weather") or None if no match.
    The comparison is case-insensitive and strips punctuation.
    """
    cleaned = user_text.lower()
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)   # remove punctuation
    tokens = set(cleaned.split())

    for intent, config in INTENT_CONFIG.items():
        for kw in config["keywords"]:
            # Support multi-word keywords (e.g. "next bus")
            if kw.lower() in cleaned:
                return intent

    return None


def extract_slot_value(slot_name: str, user_text: str) -> str:
    """
    A lightweight slot extractor.
    Currently treats the entire trimmed user input as the slot value.
    You can expand this with regex patterns per slot if needed.
    """
    return user_text.strip()


# =============================================================================
# 4. HANDLERS  –  Domain-Specific Response Generators
# =============================================================================
# [EXTENSIBILITY] Step 3: write a handle_<domain>(slots) function here and
# reference it in INTENT_CONFIG["handler"].

def handle_weather(slots: dict) -> str:
    """Generate a weather report response using mock data."""
    data = get_weather(slots["city"], slots["date"])
    return (
        f"[Weather] {data['city']} on {data['date']}:\n"
        f"   Condition   : {data['condition']}\n"
        f"   Temperature : {data['temperature_c']} deg C\n"
        f"   Humidity    : {data['humidity_pct']}%"
    )


def handle_restaurant(slots: dict) -> str:
    """Generate restaurant suggestions using mock data."""
    results = get_restaurants(slots["cuisine"], slots["neighborhood"])
    lines = [f"[Restaurants] Top {slots['cuisine'].title()} in {slots['neighborhood'].title()}:\n"]
    for i, r in enumerate(results, start=1):
        lines.append(
            f"   {i}. {r['name']}  [{r['rating']}*]  "
            f"(~{r['wait_minutes']} min wait)"
        )
    return "\n".join(lines)


def handle_bus(slots: dict) -> str:
    """Generate next bus/tram departure times using mock data."""
    departures = get_next_buses(slots["stop_name"], slots["direction"])
    lines = [
        f"[Bus/Tram] Next from '{slots['stop_name'].title()}' "
        f"-> {slots['direction'].title()}:\n"
    ]
    for d in departures:
        lines.append(
            f"   {d['line']:10s}  at {d['departs_at']}  "
            f"({d['minutes_away']} min away)"
        )
    return "\n".join(lines)


# Map handler names (strings) → actual functions
HANDLER_REGISTRY = {
    "handle_weather": handle_weather,
    "handle_restaurant": handle_restaurant,
    "handle_bus": handle_bus,
    # [EXTENSIBILITY] Register new handlers here, e.g.:
    # "handle_hotel": handle_hotel,
}


# =============================================================================
# 5. DIALOGUE MANAGER  –  Frame-Based / Form-Filling
# =============================================================================

class DialogueManager:
    """
    Manages the state of a conversation using a simple frame-based approach.

    State variables:
        current_intent (str | None) : the active task (e.g. "weather")
        slots          (dict)       : collected slot values for the active task
        pending_slot   (str | None) : the next slot the system is waiting for
    """

    def __init__(self):
        self.reset()

    def reset(self):
        """Clear all state (called at the start or after delivering a result)."""
        self.current_intent: str | None = None
        self.slots: dict = {}
        self.pending_slot: str | None = None

    # ------------------------------------------------------------------
    def process(self, user_input: str) -> str:
        """
        Main entry point: given the user's raw text, return the bot's reply.

        Flow:
          1. If we are waiting for a slot value  → fill it, then continue
          2. Else try to detect a new intent     → start filling its slots
          3. If no intent found                  → ask for clarification
        """

        # ── Case 1: We are mid-conversation waiting for a slot value ──────
        if self.pending_slot is not None:
            value = extract_slot_value(self.pending_slot, user_input)
            self.slots[self.pending_slot] = value
            self.pending_slot = None
            return self._continue_filling()

        # ── Case 2: Start fresh – detect what the user wants ──────────────
        intent = detect_intent(user_input)

        if intent is None:
            return self._fallback_response(user_input)

        # New intent detected – set up the frame
        self.current_intent = intent
        self.slots = {}
        self.pending_slot = None
        return self._continue_filling()

    # ------------------------------------------------------------------
    def _continue_filling(self) -> str:
        """
        Check which slots still need to be filled for the current intent.
        Ask for the next missing slot, or call the handler if all are filled.
        """
        config = INTENT_CONFIG[self.current_intent]
        required_slots = config["slots"]

        for slot in required_slots:
            if slot not in self.slots:
                # Ask the user to provide this slot
                self.pending_slot = slot
                return f"[?] {SLOT_PROMPTS[slot]}"

        # All slots are filled – call the domain handler
        handler_fn = HANDLER_REGISTRY[config["handler"]]
        response = handler_fn(self.slots)

        # Reset state so the next user message starts fresh
        self.reset()
        return response

    # ------------------------------------------------------------------
    @staticmethod
    def _fallback_response(user_input: str) -> str:
        """Politely handle unrecognised inputs."""
        return (
            "[Bot] I'm not sure I understand. I can help with:\n"
            "   - Weather forecasts  (e.g. 'What's the weather in Paris?')\n"
            "   - Restaurant suggestions  (e.g. 'I want to eat Italian food')\n"
            "   - Next bus/tram times  (e.g. 'When is the next bus?')\n"
            "Please try rephrasing your request."
        )


# =============================================================================
# 6. MAIN  –  Command-Line Chat Loop
# =============================================================================

def main():
    print("=" * 60)
    print("  [Bot] Welcome to the Dialogue Assistant Chatbot")
    print("=" * 60)
    print("  I can help you with weather, restaurants, and transit.")
    print("  Type 'quit' or 'exit' to end the conversation.\n")

    dm = DialogueManager()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[Bot] Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in {"quit", "exit", "bye", "goodbye"}:
            print("[Bot] Goodbye! Have a great day!")
            break

        response = dm.process(user_input)
        print(f"\nBot: {response}\n")


if __name__ == "__main__":
    main()
