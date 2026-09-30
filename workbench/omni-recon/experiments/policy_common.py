"""Shared FDB-v3 tool schemas, per-domain tool subsets, tool-policy prompts, and NVIDIA's default VoiceChat system
message (copied from NeMo examples/speechlm2/offline_voicechat_fc_infer.py) for the policy probe."""
from pathlib import Path

FDB = Path("/home/xiang/rt_ext/Full-Duplex-Bench/v3")
DEFAULT_SYSTEM_MESSAGE = (
    "You are an AI voice assistant developed by NVIDIA. "
    "Your name is NVIDIA Voice Chat. "
    "Your job is to be helpful and harmless and have engaging conversations in English. "
    "Maintain a warm and friendly tone. "
    "Keep the dialogue open and ongoing. "
    "Be clear and direct, especially when answering yes or no questions and multiple-choice questions. "
    "Avoid long answers unless the user asks you to provide details or context. "
    "You must provide diverse responses and rephrase answers if the user asks the same question. "
    "DO NOT interrupt the user when they are speaking, let them finish their turn before answering."
    "\n\nWhen you receive a request, follow this decision process:\n"
    "1. Does the request match one of your available tools below? If yes, you MUST call that tool - "
    "never answer it directly from your own knowledge, even if you think you know the answer.\n"
    "2. Is it a general knowledge question (history, science, geography, math, facts, etc.)? "
    "If yes, answer directly from your own knowledge - do not call any tool.\n"
    "3. Does it require an external action or live data that none of your tools cover "
    "(e.g. ordering food, sending email)? If yes, politely say you don't have that capability."
    "\n\nNEVER say \"I don't have a tool for that\" for general knowledge questions you can answer yourself."
    "\n\nDO NOT use any tools when not needed to answer the user's requests, under no circumstance."
    "\n\nYou are an expert across history, geography, science, math, literature, biographies, languages, "
    "recipes, programming, current affairs, and general knowledge. When the user asks about any of these, "
    "answer directly and conversationally from your own knowledge - no <TOOLCALL>."
    "\n\nCall a tool ONLY when the user's request matches one of the tools listed in <AVAILABLE_TOOLS> below. "
    "For every other request, do not call any tool - just answer from your knowledge. "
    "Never invent or call a tool name that is not literally in <AVAILABLE_TOOLS>."
    "\n\nTool-call arguments must be values the user spoke. "
    "If a required argument is missing, ask the user; never guess."
    "\n\nIf a tool call fails or returns an error, do not retry the tool call for the same request. "
    "Tell the user that the API has an issue."
)

SCHEMA = {  # FDB-v3 mock API signatures (mock_apis.py)
    "search_flights": ({"destination": "string", "date": "string"}, ["destination", "date"]),
    "book_flight": ({"passenger_name": "string", "flight_id": "string"}, ["passenger_name"]),
    "update_identity_doc": ({"doc_type": "string", "doc_number": "string"}, ["doc_type", "doc_number"]),
    "get_card_benefits": ({"card_type": "string"}, ["card_type"]),
    "get_exchange_rate": ({"amount": "number", "from_currency": "string", "to_currency": "string"},
                          ["amount", "from_currency", "to_currency"]),
    "modify_autopay": ({"bill_type": "string", "source_account": "string"}, ["bill_type", "source_account"]),
    "search_apartments": ({"city": "string", "bedrooms": "integer", "max_price": "number"},
                          ["city", "bedrooms", "max_price"]),
    "calculate_commute": ({"origin_address": "string", "destination_address": "string", "mode": "string"},
                          ["origin_address", "destination_address"]),
    "update_search_filter": ({"filter_name": "string", "value": "string"}, ["filter_name", "value"]),
    "track_order": ({"order_id": "string"}, ["order_id"]),
    "search_products": ({"query": "string", "max_price": "number"}, ["query"]),
    "add_to_cart": ({"product_id": "string", "quantity": "integer"}, ["product_id", "quantity"]),
}
DOMAIN_TOOLS = {"travel": ["search_flights", "book_flight", "update_identity_doc"],
                "finance": ["get_card_benefits", "get_exchange_rate", "modify_autopay"],
                "housing": ["search_apartments", "calculate_commute", "update_search_filter"],
                "ecommerce": ["track_order", "search_products", "add_to_cart"]}


POLICY = {  # instruction-following probe: does the native function head obey a stated tool policy?
    "default": "",
    "never": ("\n\nIMPORTANT POLICY FOR THIS SESSION: the tools are disabled. Never call any tool under any circumstances. "
              "If the user asks for something that needs a tool, say that you cannot access that system right now."),
    "confirm": ("\n\nIMPORTANT POLICY FOR THIS SESSION: before calling any tool you must first read the details back to the "
                "user and ask them to confirm. Never call a tool in the same turn as the request; wait for the user's yes."),
}


def tools_for(domain):
    key = next(k for k in DOMAIN_TOOLS if domain.startswith(k))
    return [{"type": "function", "function": {
        "name": n, "description": n.replace("_", " "),
        "parameters": {"type": "object", "properties": {k: {"type": v} for k, v in SCHEMA[n][0].items()},
                       "required": SCHEMA[n][1]}}} for n in DOMAIN_TOOLS[key]]


