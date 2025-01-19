"""Asynchronous OpenAI API client for parallel GPT-4 chat embeddings.

This module provides functionality to make parallel calls to OpenAI's GPT-4 
chat completion and embedding APIs. It includes rate limiting and proper error 

Example:
    >>> sys_prompt = "You are a helpful assistant."
    >>> messages = ["Hello, how are you?", "What is 2+2?"]
    >>> completions = asyncio.run(get_completion_list(
             sys_prompt, messages, max_parallel=5))
"""

import asyncio
import aiohttp
import time
import cProfile
import pstats
from typing import List, Optional, Any
from pathlib import Path
from openai import AsyncOpenAI

# Load API key from config file
API_KEY_PATH = Path("data/openAI_key.txt")
OPENAI_API_KEY = API_KEY_PATH.read_text().strip()

# Configure API client and headers
client = AsyncOpenAI(api_key=OPENAI_API_KEY)
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
}


class ProgressTracker:
    """Tracks progress of API calls."""

    def __init__(self, total: int):
        """Initialize progress tracker.

        Args:
            total: Total number of expected API calls
        """
        self.total = total
        self.current = 0

    def increment(self) -> None:
        """Increment the count of completed calls."""
        self.current += 1

    def __str__(self) -> str:
        return f"Completed {self.current}/{self.total} calls"


async def get_completion(
    system_prompt: str,
    user_prompt: str,
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
    progress: ProgressTracker
) -> dict:
    """Make a single GPT chat completion API call.

    Args:
        system_prompt: System message for chat context
        user_prompt: User message to get completion for
        session: Aiohttp client session
        semaphore: Rate limiting semaphore
        progress: Progress tracking object

    Returns:
        API response data as dictionary
    """
    async with semaphore:
        # Rate limiting delay
        await asyncio.sleep(1)

        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }
        ) as response:
            data = await response.json()
            progress.increment()
            return data


async def get_completion_list(
    system_prompt: str,
    content_list: List[str],
    max_parallel_calls: int
) -> List[dict]:
    """Get chat completions for multiple prompts in parallel.

    Args:
        system_prompt: System message for all completions
        content_list: List of user prompts to get completions for
        max_parallel_calls: Maximum concurrent API calls

    Returns:
        List of API response data
    """
    semaphore = asyncio.Semaphore(value=max_parallel_calls)
    progress = ProgressTracker(len(content_list))

    async with aiohttp.ClientSession() as session:
        tasks = [
            get_completion(
                system_prompt,
                content,
                session,
                semaphore,
                progress
            )
            for content in content_list
        ]
        return await asyncio.gather(*tasks)


async def get_embedding_async(
    text: str,
    model: str,
    semaphore: asyncio.Semaphore
) -> Optional[List[float]]:
    """Get embeddings for a single text.

    Args:
        text: Input text to get embedding for
        model: Name of embedding model to use
        semaphore: Rate limiting semaphore

    Returns:
        Embedding vector or None if request times out
    """
    async with semaphore:
        try:
            response = await asyncio.wait_for(
                client.embeddings.create(
                    input=text,
                    model=model
                ),
                timeout=10
            )
            return response.data[0].embedding
        except asyncio.TimeoutError:
            return None


async def get_embedding_list(
    content_list: List[str],
    max_parallel_calls: int
) -> List[Optional[List[float]]]:
    """Get embeddings for multiple texts in parallel.

    Args:
        content_list: List of texts to get embeddings for
        max_parallel_calls: Maximum concurrent API calls

    Returns:
        List of embedding vectors (None for failed requests)
    """
    semaphore = asyncio.Semaphore(max_parallel_calls)
    tasks = [
        get_embedding_async(
            content,
            model="text-embedding-ada-002",
            semaphore=semaphore
        )
        for content in content_list
    ]
    return await asyncio.gather(*tasks)
