import ingescape as igs
import base64
import tkinter as tk
from tkinter import filedialog


# Fonction pour envoyer un message au Whiteboard
def send_message(message):
    try:
        igs.service_call("Whiteboard", "chat", message, "")
        print(f"Message sent: {message}")
    except Exception as e:
        print(f"Failed to send message: {e}")


def add_Text(message, x, y, color):
    try:
        arguments_list = (message, x, y, color)
        elementID = igs.service_call("Whiteboard", "addText", arguments_list, "")
        print(f"add Test: {arguments_list}")
        return elementID
    except Exception as e:
        print(f"Failed to add Text: {e}")


def add_Image(Image, x, y, widh, height):
    try:
        # Lire l'image et l'encoder en Base64
        with open(Image, "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
        arguments_list = (encoded_image, x, y, widh, height)
        elementID = igs.service_call("Whiteboard", "addImage", arguments_list, "")
        # print(f"add Image: {arguments_list}")
        print(f"add Image:")
        print(elementID)
        return elementID
    except Exception as e:
        print(f"Failed to add Image: {e}")


def add_Image_From_URL(Image_URL, x, y):
    try:
        arguments_list = (Image_URL, x, y)
        elementID = igs.service_call("Whiteboard", "addImageFromUrl", arguments_list, "")
        print(f"add Image From URL: {arguments_list}")
        return elementID
    except Exception as e:
        print(f"Failed to add Image From UR: {e}")


def remove_Element(elemntID):
    try:
        succeeded = igs.service_call("Whiteboard", "remove", elemntID, "")
        print(f"remove: {elemntID}")
        return succeeded
    except Exception as e:
        print(f"Failed to remove: {e}")


def hide_Labels():
    try:
        igs.service_call("Whiteboard", "hideLabels", "", "")
        print("hide Labels")
    except Exception as e:
        print(f"Failed to hide labels: {e}")


def translate_element():
    pass


def clearWhitboard():
    try:
        igs.service_call("Whiteboard", "clear", "", "")
    except Exception as e:
        print(f"Failed to clear: {e}")


def select_image_and_add_to_whiteboard(x=100, y=100, width=200, height=200):
    """Open file dialog to select an image and add it to the whiteboard."""
    try:
        # Initialize the file dialog
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        root.attributes('-topmost', True)  # Bring the dialog to the front

        # Open file dialog to select an image
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )

        if file_path:
            print(f"Selected file: {file_path}")
            # Add the selected image to the whiteboard
            with open(file_path, "rb") as img_file:
                encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
            arguments_list = (encoded_image, x, y, width, height)
            elementID = igs.service_call("Whiteboard", "addImage", arguments_list, "")
            print(f"Image added to whiteboard: {elementID}")
        else:
            print("No file selected.")
    except Exception as e:
        print(f"Failed to add image to whiteboard: {e}")

        def add_image(image_path, x, y, width, height):
            try:
                with open(image_path, "rb") as img_file:
                    encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
                args = (encoded_image, x, y, width, height)
                igs.service_call("Whiteboard", "addImage", args, "")
                print(f"Image added: {args}")
            except Exception as e:
                print(f"Failed to add image: {e}")

def hide_labels():
    try:
        igs.service_call("Whiteboard", "hideLabels", "", "")
        print("Labels hidden")
    except Exception as e:
        print(f"Failed to hide labels: {e}")

def show_labels():
    try:
        igs.service_call("Whiteboard", "showLabels", "", "")
        print("Labels shown")
    except Exception as e:
        print(f"Failed to show labels: {e}")