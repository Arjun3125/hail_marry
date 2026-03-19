import pathlib
import re

file_path = pathlib.Path('backend/src/interfaces/rest_api/ai/workflows.py')
code = file_path.read_text(encoding='utf-8')

SCHEMAS = """from pydantic import BaseModel, Field
from typing import List, Optional

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct: str
    citation: Optional[str] = None

class QuizOutput(BaseModel):
    questions: List[QuizQuestion]

class ConceptMapNode(BaseModel):
    id: str
    label: str

class ConceptMapEdge(BaseModel):
    from_node: str = Field(alias="from")
    to_node: str = Field(alias="to")
    label: str

class ConceptMapOutput(BaseModel):
    nodes: List[ConceptMapNode]
    edges: List[ConceptMapEdge]

class MindmapNode(BaseModel):
    label: str
    children: Optional[List['MindmapNode']] = None

class Flashcard(BaseModel):
    front: str
    back: str

class FlashcardOutput(BaseModel):
    cards: List[Flashcard]

class AudioLine(BaseModel):
    speaker: str
    text: str

class AudioOutput(BaseModel):
    dialogue: List[AudioLine]
    title: str
    duration_estimate: str

class VideoSlide(BaseModel):
    title: str
    bullets: List[str]
    narration: str

class VideoOutput(BaseModel):
    slides: List[VideoSlide]
    presentation_title: str
    total_slides: int

# Mode to schema mapping
SCHEMA_MAP = {
    "quiz": QuizOutput,
    "concept_map": ConceptMapOutput,
    "mindmap": MindmapNode,
    "flashcards": FlashcardOutput,
}
"""

code = code.replace('import json', f'import json\n{SCHEMAS}')

# Patch execute_text_query
old_execute = """    try:
        data = await llm.generate(
            prompt,
            model=settings.llm.model,
            temperature=settings.llm.temperature,
            num_predict=LENGTH_TOKENS.get(request.response_length, settings.llm.max_new_tokens),
        )"""

new_execute = """    try:
        if mode in SCHEMA_MAP:
            data = await llm.generate_structured(
                prompt,
                schema=SCHEMA_MAP[mode],
                model=settings.llm.model,
                temperature=settings.llm.temperature,
            )
            data["response"] = json.dumps(data["response"]) # Keep downstream pipeline intact
        else:
            data = await llm.generate(
                prompt,
                model=settings.llm.model,
                temperature=settings.llm.temperature,
                num_predict=LENGTH_TOKENS.get(request.response_length, settings.llm.max_new_tokens),
            )"""
code = code.replace(old_execute, new_execute)

# Patch audio
old_audio = """    try:
        data = await llm.generate(prompt, model=settings.llm.model, temperature=0.7, num_predict=2000)
    except httpx.ConnectError as exc:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama") from exc
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="AI request timed out") from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail="AI service error") from exc

    raw = data.get("response", "")
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(raw[start:end])
    except json.JSONDecodeError:
        pass"""

new_audio = """    try:
        data = await llm.generate_structured(prompt, schema=AudioOutput, model=settings.llm.model, temperature=0.7)
    except httpx.ConnectError as exc:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama") from exc
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="AI request timed out") from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail="AI service error") from exc

    return data.get("response", {})"""
code = code.replace(old_audio, new_audio)

# Patch video
old_video = """    try:
        data = await llm.generate(prompt, model=settings.llm.model, temperature=0.4, num_predict=2000)
    except httpx.ConnectError as exc:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama") from exc
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="AI request timed out") from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail="AI service error") from exc

    raw = data.get("response", "")
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(raw[start:end])
    except json.JSONDecodeError:
        pass"""

new_video = """    try:
        data = await llm.generate_structured(prompt, schema=VideoOutput, model=settings.llm.model, temperature=0.4)
    except httpx.ConnectError as exc:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama") from exc
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="AI request timed out") from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail="AI service error") from exc

    return data.get("response", {})"""
code = code.replace(old_video, new_video)

file_path.write_text(code, encoding='utf-8')
print("Patched workflows.py")
