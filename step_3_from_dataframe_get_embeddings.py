# TODO description of the program

"""
This program takes the dataframe created from USPTO data and transforms the 
text data into embeddings using OpenAI's models. some texts are too long to be
processed in one request, so we are going to split them into smaller parts.

On every request, there is a max number of tokens that can be processed. 
Max Tokens Per Request (MTPR) is 8191.

First we will obtain the embeddings of the first 8191 tokens of all texts,
then the next 8191 and so on. The parameter "segment_idx" will keep
track of which part of the text we are processing. "segment_idx = 0"
means we are processing the first 8191 tokens, "segment_idx = 1" means 
we are processing the next 8191 tokens, and so on.

To speed up things, we will use asyncio to make requests in parallel. We will
create batches until we achieve the max number of tokens per minute or the max 
max number of requests per minute. Then we will make the requests and start
again. 

Models from OpenAI        Dimensions    Max tokens
text-embedding-ada-002	    1536	        8191
text-embedding-3-small	    1536	        8191
text-embedding-3-large	    3072	        8191
"""

import time
import pandas as pd
import asyncio
import os
from step_2_call_GPT4_Chat_in_parallel import get_embedding_list
from step_1_create_dataframe import TXT_COLUMNS, MODEL

TXT_COLUMNS = ["abstract"]  # TODO: delete this line
print("WARNING: only processing abstracts")  # TODO: delete this line

# tokens per minute
TPM = 1e6
# requests per min
# TODO: why not 500? in my experiments, 400 gave consistent results.
RPM = 400
# max tokens per request
MTPR = 8191


def from_sub_df_get_embeddings(txt_col: str, df: pd.DataFrame, k: int) -> list:
    """
    Retrieve embeddings for a specific text column in a DataFrame.

    Args:
        txt_col (str): The name of the text column 
                        (abstract, claims, description).
        df (pd.DataFrame): The DataFrame containing the text data.
        k (int): keeps track of which part of the text we are processing. k = 0
                means we are processing the first 8191 tokens, k = 1 means we
                are processing the next 8191 tokens, and so on.

    Returns:
        list: The list of embeddings for the text column.
    """

    embeddings = []

    batch = []
    batch_tokens = 0
    batch_requests = 0
    last_request_time = time.time()

    def check_wait(last_request_time: float):
        return
        # TODO: delete this line
        # """Check if we need to wait and wait if necessary."""
        # time_since_last_request = time.time() - last_request_time
        # if time_since_last_request < 60:
        #     time.sleep(60 - time_since_last_request)

    for i, row in df.iterrows():
        n_tokens = row[f"{txt_col}_tokens"]
        txt = row[txt_col]
        # cut the text
        txt = txt[k*MTPR: min(len(txt), (k+1)*MTPR)]

        # check if we need to make a request
        if batch_tokens + n_tokens >= TPM or batch_requests + 1 >= RPM:
            # check if we need to wait and wait if necessary
            check_wait(last_request_time)

            batch_embed = asyncio.run(
                get_embedding_list(batch, max_parallel_calls=RPM))
            last_request_time = time.time()

            embeddings.extend(batch_embed)
            batch = []
            batch_tokens = 0
            batch_requests = 0

        batch.append(txt)
        batch_tokens += n_tokens
        batch_requests += 1

    # last batch
    check_wait(last_request_time)
    batch_embed = asyncio.run(
        get_embedding_list(batch, max_parallel_calls=RPM))
    embeddings.extend(batch_embed)

    # extend the embeddings for long texts
    old_embeddings = df[f"{txt_col}_embeddings"].tolist()
    for i, old_e in enumerate(old_embeddings):
        old_e.append(embeddings[i])

    return old_embeddings


if __name__ == "__main__":

    # we are sequentially going to get the embeddings from the text.
    # First the first MTPR=8191 tokens, then the next MTPR=8191 tokens, and so on.
    # We are doing this for abstract, claims, description, and title

    # open dataframe
    folder_year = r"C:\Users\Roberto\Documents\GitHub Repositories\USPTO\data\fake_2005_folder"
    df = pd.read_parquet(os.path.join(folder_year, "dataframe.parquet"))

    # TODO: delete this line!
    df = df.head(1000)

    # create column with empty lists
    for txt_col in TXT_COLUMNS:
        df[f"{txt_col}_embeddings"] = df[txt_col].apply(lambda x: [])

    # keeps track of which part of the text we are processing
    segment_idx = 0

    for col in TXT_COLUMNS:
        print(f"Processing {col}")

        sub_df = df

        while len(sub_df) > 0:
            embeddings = from_sub_df_get_embeddings(col, sub_df, segment_idx)
            df[f"{col}_embeddings"] = embeddings

            segment_idx += 1
            sub_df = df[df[f"{col}_tokens"] > segment_idx*MTPR]

    # save the dataframe
    df.to_parquet("data/df_with_embeddings.parquet", index=False)
    print("Dataframe saved")
