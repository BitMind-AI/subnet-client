from PIL import Image
import base64
from io import BytesIO
import requests

def encode_image_to_base64(image_path):
    # Open the image file
    with Image.open(image_path) as image:
        # Convert the image to a BytesIO object
        image = image.convert('RGB')
        buffered = BytesIO()
        image.save(buffered, format="JPEG")  # You can choose the format you need (PNG, JPEG, etc.)
        
        # Encode the BytesIO object to a base64 string
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return img_str

# Path to your image
image_path = 'golden.jpg'

# Encode the image to base64
encoded_image = encode_image_to_base64(image_path)

# URL of the forward_image route
url = 'http://54.85.203.110:47927/forward_image'

# JSON payload
payload = {
    "image": encoded_image
}

# Send the POST request
response = requests.post(url, json=payload)

# Print the response
print(response.status_code)
print('prediction', response.json())
