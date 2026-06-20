"""Central LLM client — wraps OpenAI ChatCompletion with retry logic."""
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def chat(system: str, user: str, max_tokens: int = 4096) -> str:
    resp = await get_client().chat.completions.create(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    )
    return resp.choices[0].message.content or ""


async def stream(system: str, user: str):
    """Yield text chunks from a streaming ChatCompletion."""
    async with await get_client().chat.completions.create(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        stream=True,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    ) as resp:
        async for chunk in resp:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
