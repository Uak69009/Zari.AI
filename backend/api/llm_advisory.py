import os
import json

# Fallback Urdu advisories per disease family for seamless offline/fallback operation
URDU_ADVISORY_MAP = {
    "Late_Blight": "اسلام علیکم! آپ کی فصل میں لیٹ بلائٹ (Late Blight) فنگس کے اثرات پائے گئے ہیں۔ علاج کے لیے فوری طور پر کوپر آکسی کلورائیڈ یا مینکوزیب کا سپرے کریں۔ کھیت میں پانی جمع نہ ہونے دیں اور متاثرہ پتوں کو تلف کریں۔",
    "Early_Blight": "اسلام علیکم! آپ کے پودے میں ارلی بلائٹ (Early Blight) کی علامات ہیں۔ پودوں کے نچلے متاثرہ پتے ہٹا دیں اور فنجی سائیڈ (Mancozeb یا Chlorothalonil) کا وقت پر سپرے کریں۔",
    "Yellow_Rust": "اسلام علیکم! گندم یا فصل میں زرد کنگی (Yellow Rust) کا حملہ ظاہر ہوا ہے۔ علاج کے لیے پروپیکونازول (Tilt/Propiconazole) یا ٹیبوکونازول کا فوری سپرے کریں۔",
    "Common_Rust": "اسلام علیکم! فصل میں براؤن یا رَسٹ (Rust) فنگس پایا گیا ہے۔ نائٹروجن کی زیادہ مقدار سے گریز کریں اور فنجی سائیڈ کا مناسب سپرے انجام دیں۔",
    "Bacterial_Spot": "اسلام علیکم! پودے میں بیکٹیریل اسپاٹ (Bacterial Spot) کا انفیکشن ہے۔ کاپر بیسڈ مائیکرو بائیسائیڈ کا سپرے کریں اور آبپاشی اوپر سے نہ کریں بلکہ جڑوں کے پاس دیں۔",
    "Greening": "اسلام علیکم! لیموں/مالٹے میں سٹرس گریننگ یا سٹرس سائلا کا اثر ہے۔ متاثرہ شاخوں کو کاٹ کر جلا دیں اور مکھیاں ختم کرنے کے لیے امیڈا کلوپرڈ کا سپرے کریں۔",
    "Powdery_Mildew": "اسلام علیکم! پودوں پر سفید سفوف یا پاؤڈری ملڈیو کا حملہ ہے۔ سلفر یا بائیو فنجی سائیڈ کا سپرے کریں تاکہ پھیلاؤ روکا جا سکے۔",
    "Healthy": "اسلام علیکم! مبارک ہو، آپ کا پودا بالکل تندرست اور صحت مند دکھائی دے رہا ہے۔ فصل کو متوازن کھادیں دیں اور روزانہ معائنہ جاری رکھیں۔",
}

def generate_advisory(cv_result: dict) -> str:
    """
    Synthesizes classification result into localized Urdu advisory text.
    Uses Groq Llama-3.3 if GROQ_API_KEY is available, or high-quality rule-based Urdu fallback.
    """
    data = cv_result.get("data", {})
    canonical_name = data.get("canonical_name", cv_result.get("class_name", "Unknown"))
    crop = data.get("crop", "Crop")
    disease = data.get("disease", "Disease")
    confidence = cv_result.get("confidence", 0.0)

    # 1. Try Groq API if key is present
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            system_prompt = (
                "You are 'ZARI', an expert Pakistani agricultural advisor. "
                "Write your response strictly in Urdu script. "
                "Keep the response conversational, concise (2-3 sentences), easy to understand, without markdown formatting or bullet points."
            )
            user_prompt = f"Identify: Crop={crop}, Disease={disease}, Confidence={confidence*100:.1f}%. Provide greeting, diagnosis, and treatment."
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.6,
                max_tokens=250
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Groq API call fallback: {e}")

    # 2. Localized Expert Urdu Advisory Engine
    for key, advisory_template in URDU_ADVISORY_MAP.items():
        if key.lower() in canonical_name.lower():
            return advisory_template

    # Default Rule-based Advisory
    if "healthy" in canonical_name.lower():
        return f"اسلام علیکم! آپ کی {crop} کی فصل بالکل صحت مند دکھائی دے رہی ہے۔ متوازن آبپاشی اور دیکھ بھال جاری رکھیں۔"
    else:
        return f"اسلام علیکم! آپ کی {crop} کی فصل میں {disease} کی تشخیصی علامات (اعتماد: {confidence*100:.0f}%) پائی گئی ہیں۔ فصل کو متاثرہ حصوں سے پاک کریں اور قریبی زرعی ماہر کی ہدایت کے مطابق فنجی سائیڈ سپرے کریں۔"
