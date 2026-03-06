import nbformat as nbf

def create_tutorial_notebook():
    nb = nbf.v4.new_notebook()

    # 1. Introduction
    nb.cells.append(nbf.v4.new_markdown_cell("""# راهنمای جامع طراحی سیستم‌های گفتگو (مقدماتی تا پیشرفته)
## Comprehensive Guide to Dialogue Systems

در این نوت‌بوک، ما قدم به قدم یاد می‌گیریم که چطور یک سیستم گفتگو بسازیم. این نوت‌بوک شامل ۵ بخش اصلی است:
1. مفاهیم کلاسیک و معماری GUS
2. پیاده‌سازی گام به گام سیستم مبتنی بر فرم (Frame-based)
3. ابزار تعامل مستقیم (چت با ایجنت)
4. آشنایی با سیستم‌های مدرن عصب‌محور (LLM)
5. پیاده‌سازی سیستم هوشمند ترکیبی (Hybrid + RAG) برای کار با داده‌های خصوصی
"""))

    # 2. Section 1: GUS & Frames
    nb.cells.append(nbf.v4.new_markdown_cell("""## بخش اول: مفهوم فرم (Frame) در گفتگو
در سیستم‌های کلاسیک، ما گفتگو را مثل یک "فرم" می‌بینیم که باید پر شود. هر فیلد در این فرم یک **Slot** نامیده می‌شود.

مثلاً برای رزرو رستوران، ما به ۳ قطعه اطلاعات نیاز داریم:
*   نوع غذا (Cuisine)
*   مکان (Location)
*   محدوده قیمت (Price Range)
"""))

    nb.cells.append(nbf.v4.new_code_cell("""# تعریف کلاس پایه برای فریم‌ها
class DialogueFrame:
    def __init__(self, name, slots):
        self.name = name
        self.slots = {slot: None for slot in slots}

    def is_complete(self):
        # چک می‌کند آیا تمام فیلدها پر شده‌اند یا خیر
        return all(value is not None for value in self.slots.values())

    def get_missing_slot(self):
        # اولین فیلدی که هنوز خالی است را برمی‌گرداند
        for slot, value in self.slots.items():
            if value is None:
                return slot
        return None

    def reset(self):
        # پاک کردن اطلاعات قبلی
        self.slots = {slot: None for slot in self.slots}
"""))

    nb.cells.append(nbf.v4.new_markdown_cell("""### تعریف سرویس‌های ایجنت
در اینجا ما ۳ سرویس مختلف (آب و هوا، رستوران، حمل و نقل) را تعریف می‌کنیم:"""))

    nb.cells.append(nbf.v4.new_code_cell("""# ساخت نمونه‌های واقعی از فریم‌ها
def get_initial_frames():
    return {
        "weather": DialogueFrame("Weather", ["location", "date"]),
        "restaurant": DialogueFrame("Restaurant", ["cuisine", "location", "price_range"]),
        "transport": DialogueFrame("Transport", ["origin", "destination", "time"])
    }

frames = get_initial_frames()
print(f"سرویس‌های فعال: {list(frames.keys())}")
"""))

    # 3. Section 2: NLP & Extraction
    nb.cells.append(nbf.v4.new_markdown_cell("""## بخش دوم: درک زبان کاربر (NLP)
چطور بفهمیم کاربر چه می‌گوید؟ ما از **Keyword Matching** استفاده می‌کنیم تا کلمات کلیدی را در متن کاربر پیدا کنیم.
"""))

    nb.cells.append(nbf.v4.new_code_cell("""# لغت‌نامه استخراج اطلاعات
keywords = {
    "intents": {
        "weather": ["weather", "forecast", "آب و هوا", "هوا"],
        "restaurant": ["restaurant", "food", "eat", "hungry", "رستوران", "غذا"],
        "transport": ["bus", "train", "flight", "بلیط", "اتوبوس"]
    },
    "entities": {
        "location": ["london", "tehran", "paris", "shiraz"],
        "date": ["today", "tomorrow", "friday"],
        "cuisine": ["italian", "pizza", "persian", "kebab"],
        "price_range": ["cheap", "expensive", "luxury"],
        "origin": ["home", "airport"],
        "destination": ["work", "city center"],
        "time": ["morning", "10am", "8pm"]
    }
}

def extract_info(text):
    text = text.lower()
    found_intent = None
    found_entities = {}

    # یافتن قصد کاربر
    for intent, words in keywords["intents"].items():
        if any(word in text for word in words):
            found_intent = intent
            break
    
    # استخراج مقادیر فیلدها
    for entity_type, examples in keywords["entities"].items():
        for example in examples:
            if example in text:
                found_entities[entity_type] = example
                
    return found_intent, found_entities
"""))

    # 4. Dialogue Management
    nb.cells.append(nbf.v4.new_markdown_cell("""## بخش سوم: مدیریت گفتگو (Dialogue Manager)
این مغز متفکر ایجنت است. تصمیم می‌گیرد که کی اطلاعات را ذخیره کند و کی از کاربر سوال بپرسد.
"""))

    nb.cells.append(nbf.v4.new_code_cell("""class DialogueManager:
    def __init__(self, frames):
        self.frames = frames
        self.active_frame = None

    def process_input(self, text):
        intent, entities = extract_info(text)
        
        # ۱. تغییر سرویس در صورت لزوم
        if intent and (not self.active_frame or intent != self.active_frame.name.lower()):
            self.active_frame = self.frames[intent]
            print(f"[System] Switching to {self.active_frame.name} service.")

        if not self.active_frame:
            return "سلام! من می‌توانم در زمینه آب‌وهوا، رستوران یا بلیط کمک کنم. چه کاری انجام بدهم؟"

        # ۲. پر کردن فیلدها
        for entity_type, value in entities.items():
            if entity_type in self.active_frame.slots:
                self.active_frame.slots[entity_type] = value

        # ۳. تصمیم‌گیری برای گام بعدی (Mixed Initiative)
        if self.active_frame.is_complete():
            result = f"انجام شد! درخواست شما ثبت شد: {self.active_frame.slots}"
            self.active_frame.reset() 
            self.active_frame = None 
            return result
        else:
            missing = self.active_frame.get_missing_slot()
            return f"لطفاً مقدار {missing} را به من بگویید تا بتوانم کمکتان کنم."

dm = DialogueManager(get_initial_frames())
"""))

    # 5. Interactive Section
    nb.cells.append(nbf.v4.new_markdown_cell("""## بخش چهارم: تعامل مستقیم (با ایجنت حرف بزنید)
سلول زیر را اجرا کنید تا یک باکس چت باز شود. شما می‌توانید با ایجنت در مورد رستوران یا آب و هوا صحبت کنید.
"""))

    nb.cells.append(nbf.v4.new_code_cell("""# اجرای چت تعاملی
def start_chat():
    print("--- شروع گفتگو (برای خروج بنویسید exit) ---")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Agent: خداحافظ!")
            break
        response = dm.process_input(user_input)
        print(f"Agent: {response}")

# start_chat() # این خط را از حالت کامنت خارج کنید تا چت شروع شود
"""))

    # 6. RAG Section
    nb.cells.append(nbf.v4.new_markdown_cell("""## بخش پنجم: سیستم هوشمند ترکیبی (RAG)
یکی از سوالات مهم این بود: **چطور اطلاعات خصوصی را به ایجنت اضافه کنیم؟**
روش RAG اجازه می‌دهد ابتدا در دیتای خصوصی جستجو کنیم و بعد پاسخ را تولید کنیم.

در اینجا ما یک دیتای خصوصی فرضی داریم (شرایط تخفیف):
"""))

    nb.cells.append(nbf.v4.new_code_cell("""# دیتابیس اطلاعات اختصاصی شما
private_data = {
    "discount": "تخفیف ۲۰ درصدی برای دانشجویان در پروازهای پاریس فعال است.",
    "office": "دفتر مرکزی ما در تهران، میدان ونک واقع شده است.",
    "conference": "کنفرانس بعدی سیستم‌های گفتگو در لندن، تیرماه برگزار می‌شود."
}

def retriever(query):
    # جستجوی ساده در دیتای اختصاصی
    query = query.lower()
    for key in private_data:
        if key in query:
            return private_data[key]
    return None
"""))

    # 7. Hybrid Integration
    nb.cells.append(nbf.v4.new_markdown_cell("""### پیاده‌سازی ایجنت هوشمند ترکیبی (Hybrid Agent)
این ایجنت هم می‌تواند فرم‌های رزرو را پر کند و هم اگر سوال خاصی در مورد دیتای خصوصی (مثل تخفیف) داشتید، آن را از دیتابیس استخراج کند.
"""))

    nb.cells.append(nbf.v4.new_code_cell("""class HybridSmartAgent:
    def __init__(self, dialogue_manager, private_db_func):
        self.dm = dialogue_manager
        self.retrieve = private_db_func

    def handle(self, user_text):
        # اول چک می‌کنیم آیا سوالی درباره اطلاعات خصوصی است؟
        private_info = self.retrieve(user_text)
        if private_info:
            return f"[AI با استفاده از دیتای خصوصی شما]: {private_info}"
        
        # اگر نبود، به سیستم رزرو (کلاسیک) واگذار می‌کنیم
        return self.dm.process_input(user_text)

# ساخت ایجنت هوشمند
smart_agent = HybridSmartAgent(dm, retriever)
"""))

    nb.cells.append(nbf.v4.new_markdown_cell("""### تست نهایی ایجنت هوشمند
حالا در اینجا می‌توانید هر دو نوع سوال را بپرسید:
"""))

    nb.cells.append(nbf.v4.new_code_cell("""print(f"User: Is there any discount?\\nAgent: {smart_agent.handle('discount')}\\n")
print(f"User: I want to go to London\\nAgent: {smart_agent.handle('I want to go to London')}")
"""))

    # Save
    with open('Dialogue_Systems_Tutorial.ipynb', 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    with open('Final_Assignment_7_Tutorial.ipynb', 'w', encoding='utf-8') as f:
        nbf.write(nb, f)

if __name__ == "__main__":
    create_tutorial_notebook()
    print("Notebooks refactored into granular cells and hybrid logic added.")
