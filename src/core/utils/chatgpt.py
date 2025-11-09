"""This module is used to interact with OpenAI API"""

import os
import openai

openai.api_key = os.environ.get("OPENAI_API_KEY", "")
MODEL_NAME = "gpt-4-0613"


def get_completion(prompt, model=MODEL_NAME, temperature=0):
    """Get prompt template name and response from OpenAI API."""
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(  # pylint: disable=no-member
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]
