
from google import genai


def generate_health_remarks(
    glucose, haemoglobin, cholesterol, api_key
):
    prompt = f"""
    Review these patient blood test values:

    Glucose: {glucose}
    Haemoglobin: {haemoglobin}
    Cholesterol: {cholesterol}

    Provide a short informational health-risk summary.
    Do not diagnose any disease or claim certainty.
    Mention that interpretation depends on fasting status,
    age, sex and laboratory reference ranges.
    Recommend professional medical consultation.
    Keep the response within 100 words.
    """

    models = [
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash"
    ]

    client = genai.Client(api_key=api_key)

    for model in models:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            if response.text:
                return response.text.strip()

        except Exception as error:
            print(f"{model} failed: {error}")
            continue

    return (
        "AI service is temporarily unavailable. "
        "Please try generating remarks again later."
    )
