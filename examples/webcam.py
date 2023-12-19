import os
import cv2
import uuid

import gradio as gr
import numpy as np

import webcamgpt

from openai import OpenAI
client = OpenAI(api_key='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')

MARKDOWN = """
# webcamGPT with audio input (whisper-1 TextToAudio model)

This is a demo of webcamGPT, a tool that allows you to chat with video using GPT-4 given a prompt converted from audio (Portuguese) 
"""

connector = webcamgpt.OpenAIConnector()


def save_image_to_drive(image: np.ndarray) -> str:
    image_filename = f"{uuid.uuid4()}.jpeg"
    image_directory = "data"
    os.makedirs(image_directory, exist_ok=True)
    image_path = os.path.join(image_directory, image_filename)
    cv2.imwrite(image_path, image)
    return image_path


def respond(image: np.ndarray, prompt: str, chat_history):
    image = np.fliplr(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    image_path = save_image_to_drive(image)
    response = connector.simple_prompt(image=image, prompt=prompt)
    chat_history.append(((image_path,), None))
    chat_history.append((prompt, response))
    return "", chat_history


with gr.Blocks() as demo:

    # TextToAudio model
    audio_file= open("/media/gustavo/Gustavo2/random-tests/prompt-evals/webcamGPT/input/descreva_cena_v2.mp3", "rb")
    transcript = client.audio.translations.create(
      model="whisper-1", 
      file=audio_file
    )


    gr.Markdown(MARKDOWN)
    with gr.Row():
        webcam = gr.Image(source="webcam", streaming=True)
        with gr.Column():
            chatbot = gr.Chatbot(height=500)
            word = gr.Markdown(transcript.text)
            message = gr.Textbox()
            message.value = word.value
            clear_button = gr.ClearButton([message, chatbot])

    message.submit(respond, [webcam, message, chatbot], [message, chatbot])

demo.launch(debug=False, show_error=True)
