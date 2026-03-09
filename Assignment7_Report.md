# Assignment 7: Dialogue Systems and Question Answering
## Project Implementation Report

### 1. Introduction and System Overview
For this assignment, we have implemented a **hybrid, multilingual digital assistant** capable of handling text-based conversations. The system is designed to go beyond simple predefined flows and aims for a natural, flexible dialogue style. It integrates classical frame-based architectures with modern, robust Natural Language Processing (NLP) techniques, allowing the assistant to process user intents even when explicitly stated keywords are missing or when the input language changes mid-conversation.

The assistant currently supports **three primary domains**:
1. **Weather Forecast** (retrieving temperature and conditions for a specific location and date)
2. **Restaurant Recommendations** (finding dining options based on cuisine, location, and price range)
3. **Transportation / Transit** (finding scheduled routes based on origin, destination, and time)

Additionally, the system acts as a **Question Answering (QA)** engine over a private knowledge base (simulating RAG - Retrieval-Augmented Generation) to answer specific static questions (e.g., office locations, discount policies).

### 2. Implemented Features and Methodology

#### 2.1 Multilingual Support (Non-Trivial Functionality)
A core feature of our system is its **Translation Layer**. Instead of hardcoding NLP rules for every language, the system transparently translates user input from supported languages (Persian, Swedish, German, French, Arabic, Spanish, Ukrainian) into English before processing.
* **Method:** We utilized `langdetect` to identify the user's language and `deep-translator` (GoogleTranslator) to convert the text to English.
* **Robustness:** We implemented custom overrides for Persian characters to bypass `langdetect` inaccuracies on short strings, and added exception handling to gracefully manage API rate limits.

#### 2.2 Intent Classification via Latent Semantic Analysis (LSA)
To move beyond trivial keyword matching (e.g., "Enter 1 for weather"), we implemented an **LSA-based Intent Classifier**.
* **Method:** We used `TfidfVectorizer` and `TruncatedSVD` (from `scikit-learn`) on a small training corpus of utterances. This allows the system to capture the *semantic meaning* of a sentence. For example, the system understands that "I'm freezing" relates to the weather, even without the explicit word "weather".
* **Fallback:** If LSA confidence falls below a specific threshold (e.g., 0.3), the system falls back to an expanded keyword matching dictionary for maximum reliability.

#### 2.3 Frame-based Dialogue Management
Following the classic GUS architecture, we implemented a stateful `EntityGrid` and `DialogueManager`.
* **Entity Grid (Context Carryover):** The system remembers previously mentioned entities (like a specific city). If a user asks for weather in London, and subsequently asks for a restaurant, the system implicitly assumes London without asking again.
* **Frame Tracking:** The system evaluates which 'slots' (e.g., Cuisine, Price) are required for the active intent and dynamically prompts the user only for the missing information.

#### 2.4 Hybrid RAG Architecture
Before routing a query to the LSA classifier, the system checks a localized Question-Answering retriever function. If the user asks a factual question present in the `private_data` database (e.g., "discount"), the system intercepts the dialogue and answers from the knowledge base directly.

### 3. Sample Dialogue Outputs

**Example 1: Multilingual Mixed-Initiative (Persian)**
```
You: سلام! من فردا میرم تهران. چی بپوشم؟ (Hello! I'm going to Tehran tomorrow. What should I wear?)
[System translates to English internally -> extracts Intent: Weather, Location: Tehran, Date: tomorrow]
Agent: [Weather Service] هوا در tehran برای tomorrow ابری با دمای 14 درجه است. پیشنهاد لباس: یک لایه اضافی بپوشید.

You: گرسنه هستم (I am hungry)
[System detects Restaurant intent. Carries over Location: Tehran from previous turn]
Agent: چه نوع غذایی؟ (مثلا پیتزا، سوشی، کباب)
```

**Example 2: Semantic Understanding (Ukrainian & English)**
```
You: Яку погоду очікувати в Стокгольмі завтра? (What weather to expect in Stockholm tomorrow?)
Agent: [Weather Service] Weather in stockholm for tomorrow is partly cloudy...

You: I want to book a flight to Paris
Agent: چه زمانی می‌خواهید حرکت کنید؟ (What time do you want to depart?)
[System recognized Transport intent, extracted destination Paris, prompted for missing Time slot]
```

### 4. Limitations and Future Improvements

While functional, the current system has several limitations:
1. **Entity Extraction Weakness:** We currently rely on a hardcoded list of `KEYWORDS` and regex patterns for entity extraction (NER). If a user types a city not in our predefined list, the system will not recognize it. 
   * *Improvement:* Integrating a pre-trained robust NER model (like spaCy) would allow dynamic extraction of any location or time expression.
2. **Translation Dependency:** The system's intelligence relies heavily on external translation APIs. If the API fails or rate-limits, the system falls back to native text, processing of which is currently limited to English.
   * *Improvement:* Training cross-lingual embeddings (like un-translated multilingual BERT) would remove the dependency on external translation services.
3. **Rigid Dialogue Flows:** While the Entity Grid handles slot carry-over, the system struggles with conversational repairs (e.g., user saying "Actually, no, I meant Tuesday instead of Monday").
   * *Improvement:* Implementing a belief-tracker or a reinforcement learning-based dialogue policy manager would handle dialogue state corrections more naturally.
