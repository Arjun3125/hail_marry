"""Signal extraction service for analyzing student messages."""

from __future__ import annotations

import re
from typing import List

from ..models.signals import ExtractedSignal


# Signal extraction patterns
SIGNAL_PATTERNS = {
    "negative_self_talk": {
        "patterns": [
            r"i'?m (stupid|dumb|useless|idiot|fail)",
            r"i am (stupid|dumb|useless|idiot|fail)",
            r"i (can'?t|cannot|never) (do|understand|get)",
            r"i'?m not (smart|good|capable)",
            r"i (hate|dislike) (math|science|studies?|school)",
            r"i'?m (bad|worst|terrible) at",
        ],
        "value": "detected",
        "confidence": 0.8,
    },
    "career_aspiration": {
        "patterns": [
            r"i want to be (a|an) (doctor|engineer|teacher|scientist|artist|writer)",
            r"i'?ll become a",
            r"my dream (job|career) is",
            r"i want to study (medicine|engineering|arts|science)",
        ],
        "value": "extracted_from_text",  # Will be replaced with actual extraction
        "confidence": 0.7,
    },
    "parental_pressure": {
        "patterns": [
            r"my (mom|mum|mother|dad|father|papa|mummy|daddy) (says|wants|told|asked|forces?)",
            r"my parents (want|expect|force|push)",
            r"ghar mein pressure hai",
            r"ghar pe pressure",
        ],
        "value": "detected",
        "confidence": 0.75,
    },
    "social_comparison": {
        "patterns": [
            r"my friend\(?s?\)? got",
            r"everyone \(?else\)? ?understand",
            r"my classmates?",
            r"baaki sab",
            r"all my friends",
            r"topper ne",
            r"rank mein",
        ],
        "value": "detected",
        "confidence": 0.7,
    },
    "learning_style_hint": {
        "patterns": {
            "visual": [
                r"show me", r"can you draw", r"diagram", r"picture", r"visual",
                r"chart", r"graph", r"mind map"
            ],
            "example": [
                r"give me an example", r"example de", r"real.?life example",
                r"example chahiye", r"with example"
            ],
            "stepbystep": [
                r"step by step", r"stepwise", r"one by one", r"sequentially",
                r"how to do", r"how do i do", r"kaise karte hain"
            ],
        },
        "confidence": 0.65,
    },
    "deadline_stress": {
        "patterns": [
            r"exam \(?is\)? \(?\|on\)? \(?tomorrow|aaj|kal|day after\)",
            r"test \(?is\)? \(?\|on\)? \(?tomorrow|aaj|kal\)",
            r"kal exam hai", r"parso exam", r"abhi padna hai",
            r"last minute", r"raat bhar", r"all night"
        ],
        "value": "detected",
        "confidence": 0.8,
    },
    "teacher_relationship": {
        "patterns": [
            r"my teacher \(?doesn'?t|does not|never\) explain",
            r"teacher samjhata nahi", r"sir ache se nahi batate",
            r"teacher \(?is bad|is worst|is useless\)",
            r"class mein samajh nahi aata"
        ],
        "value": "teacher_gap_detected",
        "confidence": 0.7,
    },
    "competitive_motivation": {
        "patterns": [
            r"rank", r"topper", r"first in class", r"beat", r"better than",
            r"class mein sabse", r"leaderboard"
        ],
        "value": "detected",
        "confidence": 0.6,
    },
    "curiosity": {
        "patterns": [
            r"why does", r"how does .* work", r"what happens if",
            r"kyun hota hai", r"kaise hota hai", r"interesting",
            r"i want to know more", r"tell me more about",
            r"aur batao"
        ],
        "value": "detected",
        "confidence": 0.7,
    },
    "resilience": {
        "patterns": [
            r"let me try again", r"i'?ll try harder", r"next time",
            r"phir se try karta hoon", r"dobara karenge",
            r"i won'?t give up", r"i'?ll get it"
        ],
        "value": "detected",
        "confidence": 0.75,
    },
}


def extract_signals_from_text(text: str) -> List[ExtractedSignal]:
    """
    Run all rule patterns against the text.
    Return list of matched ExtractedSignal objects.
    A single text can match multiple signal types.
    For learning_style_hint, only keep the first match to avoid duplicates.
    """
    signals = []
    text_lower = text.lower()

    for signal_type, config in SIGNAL_PATTERNS.items():
        if signal_type == "learning_style_hint":
            # Special handling for learning style hints
            for style, patterns in config["patterns"].items():
                for pattern in patterns:
                    if re.search(pattern, text_lower, re.IGNORECASE):
                        signals.append(ExtractedSignal(
                            signal_type=signal_type,
                            signal_value=style,
                            confidence_score=config["confidence"],
                            extraction_method="rule_based"
                        ))
                        break  # Only one style per text
                if any(sig.signal_type == signal_type for sig in signals):
                    break  # Already found one
        else:
            # Regular pattern matching
            for pattern in config["patterns"]:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    value = config["value"]
                    if signal_type == "career_aspiration" and value == "extracted_from_text":
                        # Extract the actual aspiration text
                        match = re.search(pattern, text_lower, re.IGNORECASE)
                        if match:
                            # Try to extract the aspiration from the match
                            value = text.strip()
                    signals.append(ExtractedSignal(
                        signal_type=signal_type,
                        signal_value=value,
                        confidence_score=config["confidence"],
                        extraction_method="rule_based"
                    ))
                    break  # Only one match per signal type

    return signals


def detect_emotional_state(text: str) -> str:
    """
    Returns one of: positive | neutral | anxious | frustrated | disengaged
    Uses keyword matching only. Called on every student message turn.
    """
    text_lower = text.lower()

    positive_patterns = [
        "great", "thanks", "understood", "got it", "clear hai",
        "samajh gaya", "amazing", "nice", "good", "bahut accha"
    ]
    anxious_patterns = [
        "nervous", "scared", "worried", "tension", "stress",
        "ghabra", "darr", "fail ho jaunga", "kya hoga", "deadline", "exam kal hai"
    ]
    frustrated_patterns = [
        "hate", "useless", "boring", "bakwaas", "kuch nahi aata",
        "samajh nahi", "irritating", "stupid subject", "i give up", "hopeless"
    ]
    disengaged_patterns = [
        "ok", "k", "fine", "whatever", "dont care",
        "nahi karna", "baad mein", "later"
    ]

    # Count matches for each category
    positive_count = sum(1 for p in positive_patterns if p in text_lower)
    anxious_count = sum(1 for p in anxious_patterns if p in text_lower)
    frustrated_count = sum(1 for p in frustrated_patterns if p in text_lower)
    disengaged_count = sum(1 for p in disengaged_patterns if p in text_lower)

    # Determine dominant emotion
    counts = [
        ("positive", positive_count),
        ("anxious", anxious_count),
        ("frustrated", frustrated_count),
        ("disengaged", disengaged_count)
    ]
    max_emotion = max(counts, key=lambda x: x[1])

    # If no patterns matched, return neutral
    if max_emotion[1] == 0:
        return "neutral"

    return max_emotion[0]
