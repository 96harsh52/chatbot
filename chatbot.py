import openai
import pandas as pd
import tiktoken
import ast
import os
import time
from IPython import display
from scipy import spatial
# from sqlalchemy.util import asyncio

# models
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"  # Update to the latest available model
# new
from openai import OpenAI

os.environ["OPENAI_API_KEY"] = "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"
# Initialize OpenAI client
client = OpenAI()
# Set your OpenAI API key
# openai.api_key = "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"

# ... (rest of your code remains the same)

def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))



def strings_ranked_by_relatedness(
        query: str,
        df: pd.DataFrame,
        relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
        top_n: int = 100
) -> tuple[list[str], list[float]]:
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    query_embedding_response = client.embeddings.create(
        input=[query], model=EMBEDDING_MODEL
    )
    # print(query_embedding_response)
    query_embedding = query_embedding_response.data[0].embedding
    # print(query_embedding)

    strings_and_relatednesses = [
        (row["text"], relatedness_fn(query_embedding, row["embedding"]))
        for i, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)
    return strings[:top_n], relatednesses[:top_n]

def query_message(
        query: str,
        website_name: str,
        df: pd.DataFrame,
        model: str,
        token_budget: int
) -> str:
    """Return a message for GPT, with relevant source texts pulled from a dataframe."""
    strings, relatednesses = strings_ranked_by_relatedness(query, df)
    introduction = f"""
    You are a helpful assistant who is friendly and smart, 32-year-old female.
    Follow these guidelines while answering:
    1) Give a detailed and valid response.
    2) If you have no idea at all what the user is asking, then say 'Sorry, I can't answer that question right now. I'll study more so I can answer.
    5) Give as detailed a response as possible.
    6) Prefer answering using a document.
    7) If you have the correct link, then provide a proper HTML link; do not hallucinate any URLs or links.
    8) Do not respond with hallucinations.
    9) If the answer is too long, try to answer in points.

    Use the below for {website_name} answer the subsequent question. If the answer cannot be found in the document,
    write I am sorry, but I dont have the information youre looking for at the moment. However, our dedicated support team 
    would be delighted to assist you further. Please feel free to reach out to https://www.{website_name}com/contact-us/ for personalized assistance. Thank you for your understanding."""
    question = f"\n\nQuestion: {query}"
    message = introduction
    for string in strings:
        next_article = f'\n\nwebsite Data:\n"""\n{string}\n"""'
        if (
                num_tokens(message + next_article + question, model=model)
                > token_budget
        ):
            break
        else:
            message += next_article
    return message + question

from typing import Generator

async def ask(query: str,
        website_name: str,
        model: str = GPT_MODEL,
        token_budget: int = 4096 - 500,
        print_message: bool = False) -> Generator[str, None, None]:

    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    embeddings_path = f"D:\\CG-Vks\\chatbot_1\\embedding\\www.{website_name}.com_embedded.csv"

    df = pd.read_csv(embeddings_path)
    df['embedding'] = df['embedding'].apply(ast.literal_eval)
    message = query_message(query, website_name, df, model=model, token_budget=token_budget)
    if print_message:
        print(message)

    content_here = f"You answer questions about {website_name}."

    messages = [
        {"role": "system", "content": content_here},
        {"role": "user", "content": message},
    ]
    # completion_reason = None
    # response = ""
    # while not completion_reason or completion_reason == "length":
    #     openai_stream = client.chat.completions.create(
    #         model=model,
    #         messages=messages,
    #         temperature=0.0,
    #         stream=True,
    #     )
        # for chunk in openai_stream:
        #     if chunk.choices[0].delta.content is not None:
        #         yield chunk.choices[0].delta.content
        #         time.sleep(0.25)
        # for line in openai_stream:
        #     completion_reason = line["choices"][0]["finish_reason"]
        #     if "content" in line["choices"][0].delta:
        #         current_response = line["choices"][0].delta.content
        #         print(current_response)
        #         yield current_response
        #         time.sleep(0.25)


    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )
    #
    #
    #
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content





# ask("what is cost of website?","geeks5g")
