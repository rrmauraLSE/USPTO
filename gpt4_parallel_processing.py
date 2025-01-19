# this code calls OpenAI and obtains a response.
# It is designed so that it can be called multiple times in parallel.
# There are two functions:
#    get_completion_list: calls GPT4
#    get_embedding_list: obtaining embeddings.


import asyncio
import aiohttp
from openai import OpenAI, AsyncOpenAI
import time
import cProfile
import pstats
# from obtain_embeddings import get_embeddings

# read key from a txt file
OPENAI_API_KEY = open("data/openAI_key.txt", "r").read()

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
}

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# progress class. Keeps track of how many calls have been made.
# TODO: Do I need this? can I get rid of this class?


class ProgressLog:
    def __init__(self, total):
        self.total = total
        self.current = 0

    def increment(self):
        self.current = self.current + 1

    def __repr__(self):
        return f"Done runs {self.current}/{self.total}"


# CHATGPT code
async def get_completion(sys_promt, prompt, session, semaphore, progress_log):
    async with semaphore:

        await asyncio.sleep(1)

        async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json={
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": sys_promt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }) as response:
            data = await response.json()
            progress_log.increment()
            return data


async def get_completion_list(sys_prompt, content_list, max_parallel_calls):
    semaphore = asyncio.Semaphore(value=max_parallel_calls)
    progress_log = ProgressLog(len(content_list))

    async with aiohttp.ClientSession() as session:
        tasks = [get_completion(sys_prompt, content, session,
                                semaphore, progress_log) for content in content_list]
        completions = await asyncio.gather(*tasks)
        return completions


async def get_embeddings_async(text: str, model: str, semaphore: asyncio.Semaphore) -> dict:
    async with semaphore:
        try:
            response = await asyncio.wait_for(client.embeddings.create(
                input=text,
                model=model
            ), timeout=10)

            # return response['data'][0]['embedding']
            return response.data[0].embedding
        except asyncio.TimeoutError:
            return None


async def get_embedding_list(content_list, max_parallel_calls):

    semaphore = asyncio.Semaphore(max_parallel_calls)

    tasks = [get_embeddings_async(content, model="text-embedding-ada-002", semaphore=semaphore)
             for content in content_list]
    embeddings = await asyncio.gather(*tasks)
    return embeddings


if __name__ == "__main__":
    # example 1
    if False:
        sys_prompt = "You are a helpful assistant."
        content_list = ["I need to find a way to make my code run faster."]
        completions = asyncio.run(
            get_completion_list(sys_prompt, content_list, 1))
        print(completions)
        print("Done!")

    # example 2
    if True:
        with cProfile.Profile() as pr:

            for i in range(2):
                start_time = time.time()

                # TODO: i think the limit is 500 requests per min
                content_list = ["hello world!"] * 20
                embeddings = asyncio.run(get_embedding_list(
                    content_list, max_parallel_calls=500))

                end_time = time.time()
                execution_time = end_time - start_time
                print("Execution time:", execution_time, "seconds")
                print("number of embeddings:", len(embeddings))
                print("number of None values: ", embeddings.count(None))

            results = pstats.Stats(pr).strip_dirs().sort_stats('cumulative')
            # save results to a file profile_results
            results.dump_stats('profile_results')
            # print the results to the console
            results.print_stats()
