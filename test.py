import io
import os
import openai
from google.cloud import vision
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import requests
import json

# Set up the Google Cloud Vision client
client = vision.ImageAnnotatorClient()

# Set up the OpenAI API client
openai.api_key = "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"

# Set up the DALL-E API endpoint and API key
endpoint = "https://api.openai.com/v1/images/generations"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer YOUR_DALLE_API_KEY",
}

# Define a function to handle the "Choose Image" button click event
def choose_image():
    # Show a file dialog to choose an image file
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    if not file_path:
        return

    # Load the chosen image file
    with io.open(file_path, 'rb') as image_file:
        content = image_file.read()
    print(f"Image loaded successfully: {file_path}")
    image = vision.Image(content=content)

    # Perform label detection on the image
    response = client.label_detection(image=image)
    labels = response.label_annotations
    print(f"Labels detected: {[label.description for label in labels]}")

    # Extract the labels as a comma-separated string
    label_string = ', '.join([label.description for label in labels])

    # Generate a story about the image using the OpenAI API
    prompt = f"Write a story about this image: {label_string}"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    # Print the generated story
    story = response.choices[0].text.strip()
    print(story)

    # Generate a DALL-E image based on the image and labels
    payload = {
        "model": "image-alpha-001",
        "prompt": f"{label_string}\n\n{story}",
        "num_images": 1,
        "size": "1024x1024",
    }
    response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()
        image_url = result['data'][0]['url']
        print(f"DALL-E image generated: {image_url}")
    else:
        print(f"Error generating DALL-E image: {response.content}")

    # Clear the previous image and text, if any
    label_image.config(image="")
    text.delete("1.0", tk.END)

    # Load the new image and display it in a Label widget
    img = Image.open(file_path)
    img = img.resize((200, 200), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(img)
    label_image.config(image=photo)
    label_image.image = photo

    # Display the labels, story, and DALL-E image in a Text widget
    text.insert("2.0", f"Story:\n{story)
