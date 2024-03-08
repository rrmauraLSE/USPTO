# this code calls GPT4 and obtains a response.
# It is designed so that it can be called multiple times in parallel.


import asyncio
import aiohttp

# read key from a txt file
OPENAI_API_KEY = open("data/openAI_key.txt", "r").read()

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
}


class ProgressLog:
    def __init__(self, total):
        self.total = total
        self.current = 0

    def increment(self):
        self.current = self.current + 1

    def __repr__(self):
        return f"Done runs {self.current}/{self.total}"


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

if __name__ == "__main__":
    # example usecase

    sys_prompt = "You are a helpful assistant."
    content_list = ["I need to find a way to make my code run faster."]
    completions = asyncio.run(get_completion_list(sys_prompt, content_list, 1))
    print(completions)
    print("Done!")
