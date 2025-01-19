"""Process USPTO patent text data into embeddings using OpenAI models.

This script takes a DataFrame with USPTO patent data and generates embeddings
for the text fields using OpenAI's embedding models. Since some texts exceed 
the token limit for a single request, they are split into segments.

Key parameters:
- Max Tokens Per Request (MTPR): 8191 tokens
- Segments are processed sequentially using segment_idx:
  - segment_idx=0: First 8191 tokens
  - segment_idx=1: Next 8191 tokens, etc.

The script uses asyncio for parallel processing, creating batches up to the
rate limits (tokens/requests per minute) before making API calls.

Available OpenAI Models:
- text-embedding-ada-002:    1536 dimensions, 8191 max tokens
- text-embedding-3-small:    1536 dimensions, 8191 max tokens  
- text-embedding-3-large:    3072 dimensions, 8191 max tokens
"""

import time
import os
from typing import List

import pandas as pd
import asyncio

from gpt4_parallel_processing import get_embedding_list
from process_patent_xml import TEXT_COLUMNS, EMBEDDING_MODEL

# API Rate Limits
TOKENS_PER_MINUTE = int(1e6)
REQUESTS_PER_MINUTE = 400  # Conservative limit for reliability
MAX_TOKENS_PER_REQUEST = 8191


def from_sub_df_get_embeddings(
    text_column: str,
    df: pd.DataFrame,
    segment_idx: int
) -> List[List[float]]:
    """Retrieve embeddings for a specific text column in a DataFrame.

    Args:
        text_column: Name of the text column (abstract, claims, description)
        df: DataFrame containing the text data
        segment_idx: Index tracking which segment of text is being processed
            (0 = first 8191 tokens, 1 = next 8191 tokens, etc.)

    Returns:
        List of embedding vectors for the text column
    """
    embeddings = []
    batch = []
    batch_tokens = 0
    batch_requests = 0
    last_request_time = time.time()

    def check_wait(last_request_time: float) -> None:
        """Check if rate limiting requires a wait period.

        Args:
            last_request_time: Timestamp of last API request

        Ensures at least 60 seconds between batches to stay within rate limits.
        """
        time_since_last = time.time() - last_request_time
        if time_since_last < 60:
            time.sleep(60 - time_since_last)

    for _, row in df.iterrows():
        num_tokens = row[f"{text_column}_tokens"]
        text = row[text_column]

        # Extract relevant segment of text
        start_idx = segment_idx * MAX_TOKENS_PER_REQUEST
        end_idx = min(len(text), (segment_idx + 1) * MAX_TOKENS_PER_REQUEST)
        text_segment = text[start_idx:end_idx]

        # Process batch if limits reached
        if (batch_tokens + num_tokens >= TOKENS_PER_MINUTE or
                batch_requests + 1 >= REQUESTS_PER_MINUTE):

            check_wait(last_request_time)
            batch_embeddings = asyncio.run(
                get_embedding_list(
                    batch, max_parallel_calls=REQUESTS_PER_MINUTE)
            )
            last_request_time = time.time()

            embeddings.extend(batch_embeddings)
            batch = []
            batch_tokens = 0
            batch_requests = 0

        batch.append(text_segment)
        batch_tokens += num_tokens
        batch_requests += 1

    # Process final batch
    if batch:
        check_wait(last_request_time)
        batch_embeddings = asyncio.run(
            get_embedding_list(batch, max_parallel_calls=REQUESTS_PER_MINUTE)
        )
        embeddings.extend(batch_embeddings)

    # Combine with existing embeddings
    existing_embeddings = df[f"{text_column}_embeddings"].tolist()
    for i, existing in enumerate(existing_embeddings):
        existing.append(embeddings[i])

    return existing_embeddings


def main():
    """Main execution function."""
    # Load DataFrame
    folder_year = (
        r"C:\Users\Roberto\Documents\GitHub_repositories\USPTO\data"
        r"\fake_2005_folder"
    )
    df = pd.read_parquet(os.path.join(folder_year, "dataframe.parquet"))

    # Initialize embedding columns
    for column in TEXT_COLUMNS:
        df[f"{column}_embeddings"] = df[column].apply(lambda _: [])

    # Process each text column
    for column in TEXT_COLUMNS:
        print(f"Processing {column}")
        segment_idx = 0
        sub_df = df

        while len(sub_df) > 0:
            embeddings = from_sub_df_get_embeddings(
                column, sub_df, segment_idx)
            df[f"{column}_embeddings"] = embeddings

            segment_idx += 1
            sub_df = df[df[f"{column}_tokens"] >
                        segment_idx * MAX_TOKENS_PER_REQUEST]

    # Save results
    df.to_parquet("data/df_with_embeddings.parquet", index=False)
    print("DataFrame saved successfully")


if __name__ == "__main__":
    main()
