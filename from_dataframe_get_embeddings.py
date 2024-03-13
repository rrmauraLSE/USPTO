# TODO description of the program


import time
import pandas as pd
import asyncio
from call_GPT4_Chat_in_parallel import get_embedding_list

# tokens per minute
TPM = 1e6
# requests per min
# TODO: why not 500? in my experiments, 400 gave consistent results.
RPM = 400
# max tokens per request
MTPR = 8191


def from_df_get_embeddings(txt_col: str, df: pd.DataFrame, k: int) -> list:

    # TODO description of program

    embeddings = []

    batch = []
    batch_tokens = 0
    batch_requests = 0
    last_request_time = time.time()

    def check_wait(last_request_time):
        time_since_last_request = time.time() - last_request_time
        if time_since_last_request < 60:
            time.sleep(60 - time_since_last_request)

    for i, row in df.iterrows():
        tokens = len(row[f"{txt_col}_tokens"])
        txt = row[txt_col]
        # cut the text
        txt = txt[k*MTPR: min(len(txt), (k+1)*MTPR)]

        # check if we need to make a request
        if batch_tokens + tokens >= TPM or batch_requests + 1 >= RPM:
            # do the request, empty the batch and start again

            # check if we need to wait and wait if necessary
            check_wait(last_request_time)

            batch_embed = asyncio.run(
                get_embedding_list(batch, max_calls_per_min=RPM))
            last_request_time = time.time()

            embeddings.extend(batch_embed)
            batch = []
            batch_tokens = 0
            batch_requests = 0

        batch.append(txt)
        batch_tokens += tokens
        batch_requests += 1

    # last batch
    check_wait(last_request_time)
    batch_embed = asyncio.run(get_embedding_list(batch, max_calls_per_min=RPM))
    embeddings.extend(batch_embed)

    # extend the embeddings for long texts
    old_embeddings = df[f"{txt_col}_embeddings"].tolist()
    for i, old_e in enumerate(old_embeddings):
        old_e.append(embeddings[i])

    return old_embeddings


# we are secuentially going to get the embeddings from the text. First the first MTPR=8191 tokens, then the next MTPR=8191 tokens, and so on.
# We are doing this for abstract, claims and description and title
# we are going to use text-embedding-ada-002

for txt_col in ["abstract", "claims", "description", "title"]:
    sub_df = df

    while len(sub_df) > 0:
        k += 1
        sub_df = df[df[f"{txt_col}_tokens"] > k*MTPR]
        embeddings = from_df_get_embeddings(txt_col, sub_df, k)
        df[f"{txt_col}_embeddings"] = embeddings

# save the dataframe
df.to_csv("data/df_with_embeddings.csv", index=False)
print("Dataframe saved")
