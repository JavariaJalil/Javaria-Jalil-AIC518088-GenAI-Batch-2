import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI
from langchain.agents import create_agent
from typing import List
from langchain.tools import tool
import messanger
from messanger import send_message_to_client, start_bot
from pydantic import BaseModel, Field
from datetime import datetime
from structured_llm import extract_structured_output
from schemas import UserRequest
import qrcode
from PIL import Image
now = datetime.now()

load_dotenv()

llm = ChatMistralAI(
    model_name="ministral-8b-2512",
    # model_name="mistral-large-2512",
    api_key=os.getenv("MISTRAL_API_KEY"),
    temperature=0.8
)

supervisior_llm = ChatGroq(

    model="qwen/qwen3-32b",
    api_key=os.getenv("GROQ_API"),
    temperature=0.1,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
)

class SMSInput(BaseModel):
    keywords: list[str] = Field(
        ..., description="List of keywords related to the business"
    )
    business_niche: str = Field(
        ..., description="Type of business or niche"
    )
    business_name: str = Field(
        ..., description="Name of the business"
    )


class PitchVerify(BaseModel):
    keywords: list[str] = Field(
        ..., description="List of keywords related to the business"
    )
    business_niche: str = Field(
        ..., description="Type of business or niche"
    )
    business_name: str = Field(
        ..., description="Name of the business"
    )
    pitch: str = Field(
        ..., description="Generated SMS pitch to evaluate or refine"
    )


@tool(args_schema=SMSInput)
def create_sales_pitch(keywords: str, business_niche: str, business_name: str):
    """We provide website creations services to new businesses. This will craft an excellent business pitch using these:"""

    f"""business_name: {business_name},
    business_keywords: {keywords},
    business_niche: {business_niche}
    """
    message = [
        (
            "system",
            "You are a marketing expert who writes highly persuasive and concise  pitches "
            "that convince businesses they need a website to grow, as we sell website development services."
        ),
        (
            "user",
            f"""We are reaching out to:business_name: {business_name}, business_niche: ({business_niche}, related_keywords:{keywords}).

You are an expert sales copywriter specializing in WhatsApp outreach for web development services.

Your task is to write a persuasive WhatsApp message promoting OUR web development services to a business owner.

The message must focus entirely on how our web development services help businesses:

* Build a professional online presence
* Get more customers
* Increase sales
* Improve credibility
* Generate more leads
* Grow online faster

IMPORTANT RULES:

* ONLY talk about our web development services.
* NEVER describe the client’s business, products, or niche.
* NEVER talk about what the client sells.
* Keep the tone professional, conversational, and persuasive like a real WhatsApp outreach message.
* Include a strong call-to-action such as:

  * “Reply YES”
  * “Book a free consultation”
  * “Contact us today”
  * “Let’s discuss your website”

Avoid:

* Emojis
* Markdown
* Labels
* Robotic wording
* Generic filler text

Return ONLY the final WhatsApp message text."""

        )
    ]

    print("craft_pitch called")
    response = llm.invoke(message)
    return response.content


@tool(args_schema=PitchVerify)
def rate_score_pitch(keywords: str, business_niche: str, business_name: str, pitch: str):
    """ This will score the business pitch and will output a number out of 10. Rate the last pitch from 1 to 10 (10 = perfect."""

    print("Improving Sales Pitch")
    message = [
        (
            "system",
            "You are a strict marketing evaluator. You only return a numeric rating."
        ),
        (
            "user",
            f"""Business Name: {business_name}
    Niche: {business_niche}
    Keywords: {keywords}

    SMS Pitch:
        {pitch}

     You are a strict marketing evaluator. You only return a numeric rating.

Evaluate how well the SMS pitch promotes website creation services.

Scoring criteria:
- Higher score if the message clearly emphasizes how our website services benefit the client (visibility, customers, sales).
- Lower score if the message focuses only on describing the client’s business without highlighting our services.
- Penalize lack of clear value proposition or missing call-to-action.

Return only a single numeric score from 1 to 10. Do not return explanations, text, or any additional output."""
        )
    ]

    scoring_llm = ChatMistralAI(
        model_name="mistral-small-2603",
        api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.1  # Low temp for consistent ratings
    )

    response = scoring_llm.invoke(message)
    return response.content

@tool
def get_business_details():
    """Use this function to obtain bussiness information if not already provided
    from the user run it only once"""
    business_niche = input("Please enter Buiness Niche: ")
    business_name = input("Please enter Business Name: ")
    business_keywords = input("Please enter Business related Keywords separated by comma: ").strip(" ").split(",")
    phone_number = input("Please enter Business Number ")
    return business_keywords, business_niche, business_name, phone_number


pitch_business_agent = create_agent(
    model=llm,
    tools=[create_sales_pitch, rate_score_pitch],
    # not taking business details it must ask us about business details when not provided.
    system_prompt="""You are a sales assistant with access to two tools:

            1. create_sales_pitch

            * Generate a persuasive WhatsApp message promoting OUR web development services.

            2. rate_score_pitch

            * Rate the generated pitch from 1 to 10.

            WORKFLOW:

            3. Generate a pitch using create_sales_pitch.
            4. Rate it using rate_score_pitch.
            5. If score >= 7 → return final pitch.
            6. If score < 7 → regenerate and re-rate.
            7. Retry up to 6 times maximum.

            PITCH RULES:

            * Focus ONLY on our web development services.
            * Explain benefits like more customers, credibility, online growth, and increased sales.
            * Never describe the client's business or products.
            * No emojis, markdown, or robotic wording.
            * Include a strong CTA like:
            "Reply YES"
            "Contact us today"
            "Let's discuss your website"
            Return only the final pitch.""" )

current_time = now.strftime("%H:%M:%S")
print("Current Time:", current_time)

@tool
def sales_pitch_agent(request: str) -> str:
    """
    Use this when the user wants us to create a sales pitch for a business.
    """
    result = pitch_business_agent.invoke({
    "messages": [
    ("user", f"{request}")
    ]
    })

    final_message = result["messages"][ - 1]
    print(final_message.text)
    return final_message


@tool
def send_sms(message: str, phone_number: str):
    """Sends a WhatsApp message to the given phone number."""
    if messanger._driver is None:
        start_bot()
    send_message_to_client(phone_number, message)
    return "Message Sent Successfully"


def qr_to_ascii(msg, phone, size=1):
    """Convert a WhatsApp message link to an ASCII QR code.

    Args:
        msg: Message to pre-fill in WhatsApp.
        phone: Full phone number with country code (e.g., "+1234567890").
        size: Module scaling (default 1). Larger = bigger ASCII.

    Returns:
        Multi-line string with '#' for dark cells and spaces for light cells.
    """
    wa_url = f"https://wa.me/{phone}?text={quote(msg)}"
    qr = qrcode.QRCode(box_size=size, border=1)
    qr.add_data(wa_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert('L')
    ascii_str = ""
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            ascii_str += '#' if img.getpixel((x, y)) < 128 else ' '
        ascii_str += '\n'
    return ascii_str

# print(qr_to_ascii("Hello", "1234567890", size=1))

@tool
def communication_agent(message: str, phone_number: str) -> str:
    """Use this to send an SMS."""

    print("message to communication agent", message)
    comms_agent = create_agent(
        model=llm,
        tools=[send_sms],
        system_prompt="""You are a helpful agent that can send sms """)
    sms_result = comms_agent.invoke({
        "messages": [
            ("user", f"Send this SMS: {message} to {phone_number}")
        ]
    })
    return sms_result["messages"][- 1].content

SUPERVISOR_PROMPT = """
You are a helpful personal assistant that can:

1. Generate sales pitches from business details
2. Send SMS/WhatsApp messages using generated pitches

Required business details:

1. phone_number (str) – recipient's phone number

2. business_name (str)

3. business_niche (str)

4. keywords (list[str]) - keywords related to the business

Available tools:

1. get_business_details – ONLY call this if the user has NOT provided all required details

2. sales_pitch_agent – generates a sales pitch from complete business details

3. communication_agent – sends an SMS/WhatsApp message using the generated pitch

CRITICAL RULES:

1. If the user's message already contains business_name, business_niche, and keywords → DO NOT call get_business_details. 
Call sales_pitch_agent immediately.

2. If the user asks to send a pitch, but the pitch hasn't been generated yet → generate it first (call sales_pitch_agent), 
then call communication_agent.

3. Before calling communication_agent, check the generated pitch for any of these phrases (case-insensitive):

        "apologize" / "apologies"

        "multiple attempts"

        "sorry"

        If found → DO NOT send the message.

Workflow in plain steps:

Check for required details

        All present → go to step 2.

        Any missing → call get_business_details → wait for user input → then step 2.
        To Generate pitch → call sales_pitch_agent.

        Multiple actions (e.g., generate + send) → execute tools in sequence automatically.

Response style:
Be concise. Do not repeat instructions back to the user unless asked.
"""

supervisor_agent = create_agent(
    model=supervisior_llm,
    # model=llm,
    tools=[sales_pitch_agent, communication_agent, get_business_details],
    system_prompt=SUPERVISOR_PROMPT,
)

print("Enter Your Query:\n")
query= input()
# query = "Hi! business name is Ahmed Photograpy, keywords are pictures, , wedding_shoot, modeling_shoot," \
# "niche is fashion, phone_number is 923315525062"
# result = extract_structured_output(query, UserRequest)
ai_response= supervisor_agent.invoke({"messages": [{"role": "user", "content": query}]})
print(ai_response['messages'][1].content)

# message_2 = create_sales_pitch.invoke({
#     "keywords": ["eggs", "donuts", "bread"],
#     "business_niche": "Bakery",
#     "business_name": "JS Bakers"
# })
