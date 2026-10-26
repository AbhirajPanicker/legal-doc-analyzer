"""
ELI5 (Explain Like I'm 5) Service
Translates complex legal jargon, Latin terms, and dense contract clauses
into plain English with relatable real-life analogies and negotiation tips.
"""
from __future__ import annotations
import json
from config import settings

PRESET_JARGON_DATABASE = {
    "indemnification": {
        "term": "Indemnification (Hold Harmless)",
        "category": "Liability & Financial Risk",
        "plain_english": "If someone sues us because of a mistake or mess you made, you have to hire our lawyers and pay for all damages out of your own pocket.",
        "real_life_analogy": "Imagine you borrow your friend's bicycle, accidentally crash it into a neighbor's expensive sports car, and the neighbor sues your friend. Indemnification means YOU pay for the car repair and lawyer fees, not your friend.",
        "why_it_matters": "It transfers catastrophic lawsuit risk from one company to the other.",
        "hidden_trap": "Watch out for 'unilateral' (one-way) indemnities where you protect them, but they never protect you. Always demand a mutual clause and a dollar cap."
    },
    "force_majeure": {
        "term": "Force Majeure (Act of God)",
        "category": "Contract Performance",
        "plain_english": "An 'uncontrollable disaster' clause. If an earthquake, war, hurricane, or pandemic prevents either party from doing their job, nobody gets sued for missing deadlines.",
        "real_life_analogy": "You promised to deliver a birthday cake by 2 PM, but a sudden hurricane floods all roads in the city. You cannot be blamed or fined for being late.",
        "why_it_matters": "Protects honest businesses from bankruptcy when impossible external disasters strike.",
        "hidden_trap": ""
    },
    "severability": {
        "term": "Severability",
        "category": "Contract Structure",
        "plain_english": "If a judge decides that one single rule in this 50-page contract is illegal or invalid, that bad rule gets thrown away while the rest of the contract stays alive.",
        "real_life_analogy": "If you buy a box of 12 eggs and one egg is cracked, you throw away only the bad egg instead of tossing the entire carton into the garbage.",
        "why_it_matters": "Prevents the entire business deal from collapsing over one technical flaw or outdated local statute.",
        "hidden_trap": "Usually safe and standard; make sure it does not sever the core payment or service obligations."
    },
    "liquidated_damages": {
        "term": "Liquidated Damages",
        "category": "Penalties & Breaches",
        "plain_english": "A pre-agreed fine. Both parties agree in advance: 'If you delay delivery or break this rule, you owe exactly $500 per day' so nobody has to spend months in court calculating losses.",
        "real_life_analogy": "A library charging a fixed 50-cent fine for every day a book is late, instead of calculating how much money the library lost while the book was sitting on your shelf.",
        "why_it_matters": "Provides certainty and avoids expensive court arguments about how much money was actually lost.",
        "hidden_trap": "Make sure the daily fine is reasonable. Courts strike down liquidated damages if they are punitive penalties rather than genuine loss estimates."
    },
    "limitation_of_liability": {
        "term": "Limitation of Liability (Liability Cap)",
        "category": "Financial Protection",
        "plain_english": "A financial ceiling. It says: 'No matter how badly things go wrong, the maximum total money you can sue me for is capped at the fees paid in the last 12 months.'",
        "real_life_analogy": "Buying insurance on a package. If the post office loses your box, their maximum payout is capped at $100, even if you put a diamond ring inside without declaring it.",
        "why_it_matters": "Without this cap, a minor $1,000 software glitch could bankrupt you with a multi-million-dollar lawsuit.",
        "hidden_trap": "Never agree to unlimited liability. Ensure the cap is mutual (applies equally to both sides)."
    },
    "subrogation": {
        "term": "Subrogation (Waiver of Subrogation)",
        "category": "Insurance & Claims",
        "plain_english": "Stepping into someone else's shoes. If your insurance company pays for your damage, they get the legal right to chase the person who caused it to get their money back.",
        "real_life_analogy": "Your neighbor accidentally breaks your window. Your insurance company replaces your glass, and then your insurance company sends the bill to your neighbor to get reimbursed.",
        "why_it_matters": "A 'Waiver of Subrogation' prevents insurance companies from suing the other party after an accident.",
        "hidden_trap": "Check with your insurance broker before waiving subrogation rights, or your insurance policy could be voided."
    },
    "joint_and_several_liability": {
        "term": "Joint and Several Liability",
        "category": "Legal Exposure",
        "plain_english": "All for one and one for all. If you and a partner sign a contract together and your partner vanishes, the landlord or vendor can legally force YOU to pay 100% of the entire bill.",
        "real_life_analogy": "Three friends go out for dinner and split the $300 bill. Two friends run away without paying. The restaurant forces the remaining friend to pay the full $300 alone.",
        "why_it_matters": "Extremely dangerous when co-signing leases or vendor contracts with third parties.",
        "hidden_trap": "Avoid 'several liability' whenever possible. Insist that each party is only liable for their own proportional share."
    },
    "governing_law": {
        "term": "Governing Law & Jurisdiction",
        "category": "Dispute Resolution",
        "plain_english": "Specifies which state's laws rule the contract and which city's courthouse you must travel to if an argument ends up before a judge.",
        "real_life_analogy": "Playing a soccer match under FIFA rules vs. street rules, and deciding whether the game is played on your home turf or in the opponent's city 2,000 miles away.",
        "why_it_matters": "If you are in California and agree to 'London, England courts', defending a lawsuit will cost you massive travel and overseas lawyer bills.",
        "hidden_trap": "Never agree to a foreign jurisdiction unless you have an active legal presence there."
    },
    "non_disclosure": {
        "term": "Non-Disclosure / Confidentiality",
        "category": "Intellectual Property",
        "plain_english": "A pinky-promise with legal teeth. You agree never to reveal trade secrets, customer lists, financial data, or unpublished software code to anyone outside the deal.",
        "real_life_analogy": "A chef sharing their secret cookie recipe with you so you can bake together, on the strict condition that you cannot sell the recipe or post it on Instagram.",
        "why_it_matters": "Protects the proprietary core of your business from being stolen by competitors or ex-employees.",
        "hidden_trap": "Look out for non-disclosure obligations that last 'forever' (perpetual). A standard 2 to 3-year term is usually customary."
    },
    "termination_for_convenience": {
        "term": "Termination for Convenience",
        "category": "Exit Rights",
        "plain_english": "The right to cancel the contract anytime you want, for any reason or no reason at all, just by giving written notice (e.g. 30 days ahead).",
        "real_life_analogy": "Cancelling your gym membership or Netflix subscription at the end of the month without having to prove the gym or service did anything wrong.",
        "why_it_matters": "Gives you freedom to walk away if market conditions change or you find a better partner.",
        "hidden_trap": "Ensure this right is mutual! If a client can drop you on 1 day's notice after you invested months of upfront work, you will lose significant money."
    }
}

_ELI5_PROMPT = """You are a master at explaining complex legal doctrines in crystal-clear, friendly, plain English (ELI5 - Explain Like I'm 5 / Non-Lawyer Founder Mode).

Analyze the following legal clause or term:
\"\"\"{clause}\"\"\"

Produce a valid JSON object with EXACTLY these fields:
{{
  "term": "clean title of the legal doctrine or clause",
  "category": "category (e.g. Liability, Exit Rights, Payment, IP)",
  "plain_english": "2-3 sentences explaining exactly what this means in simple everyday words without legal jargon",
  "real_life_analogy": "a vivid, relatable real-world metaphor (e.g. borrowing a car, splitting a dinner bill, renting an apartment)",
  "why_it_matters": "1-2 sentences on why this exists in the contract",
  "hidden_trap": "1-2 sentences on what dangerous words to watch out for and how to negotiate it safely"
}}

Output ONLY the JSON object. No markdown fences, no preamble.
"""

def decode_legal_jargon(text: str) -> dict:
    """
    Decodes a term or arbitrary contract clause into ELI5 plain English.
    Uses preset database for instant response or invokes LLM for custom text.
    """
    clean_text = text.strip()
    key = clean_text.lower().replace(" ", "_").replace("-", "_")

    # Check for direct database match
    for k, data in PRESET_JARGON_DATABASE.items():
        if k in key or key in k:
            return data

    # Check for keyword triggers in preset database
    trigger_map = {
        "indemn": "indemnification",
        "hold harmless": "indemnification",
        "act of god": "force_majeure",
        "force majeure": "force_majeure",
        "severab": "severability",
        "liquidated damage": "liquidated_damages",
        "limitation of liability": "limitation_of_liability",
        "liability cap": "limitation_of_liability",
        "subrogat": "subrogation",
        "joint and several": "joint_and_several_liability",
        "governing law": "governing_law",
        "jurisdiction": "governing_law",
        "confidential": "non_disclosure",
        "non-disclosure": "non_disclosure",
        "nda": "non_disclosure",
        "termination for convenience": "termination_for_convenience",
    }
    for trig, target in trigger_map.items():
        if trig in clean_text.lower():
            res = PRESET_JARGON_DATABASE[target].copy()
            res["snippet_matched"] = clean_text[:120]
            return res

    # If LLM is configured, use dynamic LLM translation
    if settings.llm_configured:
        try:
            if settings.LLM_PROVIDER == "openai":
                from langchain_openai import ChatOpenAI
                from langchain.schema import HumanMessage
                llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0.1)
            elif settings.LLM_PROVIDER == "groq":
                from langchain_groq import ChatGroq
                from langchain.schema import HumanMessage
                llm = ChatGroq(model=settings.GROQ_MODEL, api_key=settings.GROQ_API_KEY, temperature=0.1, max_retries=1)
            else:
                from langchain_google_genai import ChatGoogleGenerativeAI
                from langchain.schema import HumanMessage
                llm = ChatGoogleGenerativeAI(model=settings.GOOGLE_MODEL, google_api_key=settings.GOOGLE_API_KEY, temperature=0.1, max_retries=1)

            prompt = _ELI5_PROMPT.format(clause=clean_text[:2000])
            resp = llm.invoke([HumanMessage(content=prompt)])
            raw = resp.content if hasattr(resp, "content") else str(resp)

            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("```", 2)[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.rsplit("```", 1)[0].strip()

            return json.loads(raw)
        except Exception as exc:
            print(f"[ELI5 Service] Dynamic translation error: {exc}. Using fallback.")

    # Generic Offline Heuristic Fallback
    return {
        "term": clean_text[:60] + ("..." if len(clean_text) > 60 else ""),
        "category": "Contract Provision",
        "plain_english": "This provision sets rules for who is responsible if things go wrong, how payments or milestones are verified, or when the contract can be cancelled.",
        "real_life_analogy": "Like signing a warranty when you buy a smartphone: it explains what is covered, what breaks the deal, and what you get if the device fails.",
        "why_it_matters": "It establishes enforceable promises so neither party can change their mind later without consequences.",
        "hidden_trap": "Look out for vague words like 'promptly', 'sole discretion', or 'unlimited', which favor the other party."
    }

def get_preset_terms() -> list[dict]:
    """Returns list of popular legal terms for easy pill selection."""
    return [
        {"id": k, "term": v["term"], "category": v["category"]}
        for k, v in PRESET_JARGON_DATABASE.items()
    ]
