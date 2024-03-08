# we will use GPT4 to obtain embeddings for the text data
# we will also use CLIP (biggest model) to obtain embeddings for the image data

# TODO: use the biggest CLIP model later. start with smaller (& finetune it)
# TODO: think on how to finetune BLIP (but this is optional )

"""
                        Dimensions    Max tokens
text-embedding-ada-002	    1536	        8191
text-embedding-3-small	    1536	        8191
text-embedding-3-large	    3072	        8191
"""


from openai import OpenAI

# read key from a txt file
OPENAI_API_KEY = open("data/openAI_key.txt", "r").read()

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
}

client = OpenAI(api_key=OPENAI_API_KEY)


def get_embeddings(text: str, model: str) -> dict:
    """
    Get the embeddings of a given text using a given model.

    Args:
        text (str): The text to obtain the embeddings from.
        model (str): The model to use to obtain the embeddings.

    Returns:
        dict: The embeddings of the given text.
    """
    response = client.embeddings.create(
        input=text,
        model=model
    )

    return response.data[0].embedding


# example usecase
if __name__ == "__main__":

    response = client.embeddings.create(
        input="Your text string goes here",
        model="text-embedding-3-small"
    )

    print(response.data[0].embedding)


# okay, learn about finetuning GPT4... and learn about the dimensions/max size
# of your model and prize... you already did that homework...
# some qualitative graphs. See that indeed embeddings divide the data in sectors.
# check percentage of patents that exceed the tokens...


# https://stackoverflow.com/questions/74907244/how-can-i-use-batch-embeddings-using-openais-api
