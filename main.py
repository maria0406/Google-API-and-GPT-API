import io
import os
import openai
from google.cloud import vision
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from dotenv import load_dotenv

load_dotenv()

# Set up the Google Cloud Vision client
client = vision.ImageAnnotatorClient()

# Set up the OpenAI API client
openai.api_key = os.getenv('api_key')

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

    # Clear the previous image and text, if any
    label_image.config(image="")
    text.delete("1.0", tk.END)

    # Load the new image and display it in a Label widget
    img = Image.open(file_path)
    img = img.resize((200, 200), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(img)
    label_image.config(image=photo)
    label_image.image = photo

    # Display the labels and story in a Text widget
    text.insert("2.0", f"Story:\n{story}")

# Create a GUI window and display the "Choose Image" button
root = tk.Tk()
root.title("Image Labeling and Story Generation")
root.geometry("800x600")

button_choose_image = tk.Button(root, text="Choose Image", command=choose_image)
button_choose_image.pack(pady=20)

# Create a frame to display the image, labels, and story
frame = tk.Frame(root)
frame.pack(pady=20)

# Create a Label widget to display the image
label_image = tk.Label(frame)
label_image.pack(side="left")

# Create a Text widget to display the labels and story
text = tk.Text(frame, wrap="word", font=("Times", 12), height=20, width=50)
text.pack(side="right", padx=20)

# Start the GUI main loop and wait for the user to close the window
root.mainloop()
