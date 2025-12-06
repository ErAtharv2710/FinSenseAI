import os
from datetime import datetime
from google import genai
from google.genai import types

# ==============================================================================
# 1. COMPREHENSIVE SYSTEM INSTRUCTION (Core of the Chatbot Logic)
#
# This string contains all the persona, safety rules, response templates, and
# regional context you designed.
# ==============================================================================

SYSTEM_INSTRUCTION = """
You are FINNY, a highly professional, patient, and knowledgeable Financial Literacy Coach specializing in educational guidance for young adults in India (16-28 years).

# CORE MISSION AND TONE
1. Primary Purpose: To educate, explain complex financial concepts clearly, and promote healthy money habits.
2. Regional Context: All examples, advice, and product references MUST be tailored to the **Indian financial system** (e.g., use **₹** currency, reference **CIBIL** score, mention **SIPs**, **Mutual Funds**, **PPF**, **NPS**).
3. Language: Use simple, encouraging, and jargon-free language.

# SAFETY, LEGAL, AND PROFESSIONAL GUARDRAILS (CRITICAL - NEVER VIOLATE)
1. ❌ **Refusal:** You must firmly refuse any request for specific stock/fund recommendations, market predictions, or personalized tax/legal planning.
2. ✅ **Disclaimer (Mandatory):** You MUST include one of the appropriate Disclaimer Templates (e.g., for Investment Topics) at the end of relevant responses.
3. **Risk Emphasis:** Always mention the associated risks (e.g., 'Mutual funds are subject to market risks').

# RESPONSE TEMPLATES & FORMATTING
1. **Use Headings:** Bold key sections for readability (e.g., *What is [CONCEPT]?*).
2. **Bullet Points:** Use for lists and key takeaways.
3. **Template Use:** Adopt the structure of the provided templates (Concept Explanations, Comparison Questions, Step-by-Step Guidance) where relevant.
4. **Concise:** Keep responses focused and generally under 800 tokens.

# CONVERSATION GUIDELINES
1. **Opening:** Start with the greeting: "Hello! I'm Finny, your financial education assistant..."
2. **Personal Info:** When personal data is shared, respond with the 'When Users Share Personal Financial Info' guideline.
3. **Outside Scope:** Use the 'When Questions Are Outside Scope' guideline for complex professional inquiries.
4. **Progressive Learning:** Guide users from basic to intermediate concepts.
"""

# ==============================================================================
# 2. CHATBOT CONFIGURATION
# ==============================================================================

# Using a low temperature for factual, reliable responses
GENERATION_CONFIG = types.GenerateContentConfig(
    temperature=0.3,
    top_p=0.8,
    max_output_tokens=800,
    system_instruction=SYSTEM_INSTRUCTION,  # Inject the comprehensive instruction here
    # Safety settings can be explicitly added if needed, but the SYSTEM_INSTRUCTION
    # is the primary way to enforce professional guardrails.
)


# ==============================================================================
# 3. INITIALIZATION AND CONVERSATION MANAGEMENT
# ==============================================================================

def initialize_chat_client(model_name: str = "gemini-2.5-flash"):
    """Initializes the Gemini client and starts a persistent chat session."""
    try:
        # The client automatically picks up the GEMINI_API_KEY from the environment
        client = genai.Client()

        # Create a persistent chat session with the customized configuration
        chat_session = client.chats.create(
            model=model_name,
            config=GENERATION_CONFIG,
        )

        print("=" * 60)
        print("✅ Finny Financial Education Chatbot Initialized for Hackathon")
        print(f"Model: {model_name} | Persona: Finny (Indian Context)")
        print("=" * 60)

        return chat_session

    except Exception as e:
        print(f"❌ Error initializing chatbot: {e}")
        print("Please ensure your GEMINI_API_KEY is correctly set.")
        return None


def main():
    """Main function to run the interactive console chat."""

    chat = initialize_chat_client()
    if not chat:
        return

    # Start the conversation with the mandated opening greeting
    first_response = chat.send_message(
        "Start the conversation with the Opening Greeting, then ask what topic they want to learn about.")
    print(f"\nFinny: {first_response.text}")

    print("\nType 'exit' or 'quit' to end the session.\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ['exit', 'quit']:
                print(
                    "\nFinny: Thank you for learning with me! Remember to consult professionals for personal advice. Goodbye! 👋")
                break

            if not user_input:
                continue

            # Send the user message to the persistent chat session
            response = chat.send_message(user_input)
            print(f"\nFinny: {response.text}")

        except Exception as e:
            print(f"\nFinny: I encountered an error. Please try rephrasing your question. Error: {str(e)}")
            break


if __name__ == "__main__":
    # Ensure this script is run in the same terminal where GEMINI_API_KEY was set
    main()