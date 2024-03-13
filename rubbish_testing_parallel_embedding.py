# TODO
#############       DELETE THIS PROGRAM!!!!!!   ####################


# this is just a rubbish testing program
# i am testing the embeddings in parallel
# cannot run it in ipynb

import pickle
from call_GPT4_Chat_in_parallel import get_embedding_list
import asyncio
import time

# it is not calling the things in parallel...

start_time = time.time()

content_list = ["hello world!"] * 1
max_parallel_calls = 500
embeddings = asyncio.run(get_embedding_list(content_list, max_parallel_calls))
# check that last embedding is there
print(embeddings[-1][:3])

end_time = time.time()
execution_time = end_time - start_time
print("Execution time:", execution_time, "seconds")


# save the embeddings so that you can take a look at them later
text_date = time.strftime("%Y_%m_%d__%H_%M_%S", time.localtime())
with open(f"data/embeddings_{text_date}.pkl", "wb") as f:
    pickle.dump(embeddings, f)

# why is it taking so long? it took like a min to run
    # Execution time: 278.2138969898224 seconds
#

    # does it make sense to worry? way more than a minute...
# [-0.018405795097351074, -0.03710053488612175, 0.01765453815460205]
# Execution time: 1707.4047582149506 seconds

    # confirm that you can call in parallel two texts with 6000 tokens each.
