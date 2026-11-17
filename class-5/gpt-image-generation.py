#!/usr/bin/env python3
#
# This script demonstrates how to generate an image using the OpenAI API with 
# the GPT Image Generation model.
#
# %pip install openai==1.64.0

import base64
from openai import OpenAI
from IPython import display

client = OpenAI()

response = client.images.generate(
    model="gpt-image-1.5",
    prompt="a white siamese cat",
    size="1024x1024",
    n=1,
)

image_bytes = base64.b64decode(response.data[0].b64_json)
display.Image(data=image_bytes, width=512)
