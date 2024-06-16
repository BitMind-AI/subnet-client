from cryptography.hazmat.primitives import serialization
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import base64
import logging
import requests
import random

app = FastAPI()

# Load the private key from a file
with open("private_key.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

# Load the public key from a file
with open("public_key.pem", "rb") as f:
    public_key = serialization.load_pem_public_key(f.read())

# Define the request body schema
class MessageRequest(BaseModel):
    postfix: str
    uid: int

# Define the request body schema for /forward_image
class ImageRequest(BaseModel):
    image: str

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Exception handler for request validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.post("/get_credentials")
async def get_credentials(request: MessageRequest, client_request: Request):
    try:
        # Get the message from the request
        message = b"This is a secure message"
        
        # Sign the message with the private key
        signature = private_key.sign(message)
        encoded_signature = base64.b64encode(signature).decode('utf-8')

        data = {
            "message": message,
            "signature": encoded_signature
        }
        return data
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/checkimage")
async def spoof_response(request: ImageRequest):
    try:
        # Generate spoof response
        boolean_response = random.choice([True, False])
        float_list = [random.uniform(0, 1) for _ in range(10)]
        
        return JSONResponse(
            status_code=200,
            content={
                'ai-generated': boolean_response,
                'predictions': float_list
            }
        )
    except Exception as e:
        logger.error(f"Failed to generate spoof response: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate spoof response")


@app.post("/forward_image")
async def forward_image(request: ImageRequest):
    try:
        # Construct the URL for forwarding the request
        ip = '44.201.142.122'
        port = 47923
        forward_url = f"http://{ip}:{port}/validator_proxy"
        
        # Forward the request to the last client
        data = request.dict()

        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        encoded_public_key = base64.b64encode(public_key_bytes).decode('utf-8')

        data['authorization'] = encoded_public_key
        print(forward_url)
        response = requests.post(forward_url, json=data)
        predictions = response.json()
        print('validator response', predictions)
        
        prediction = 1 if len([p for p in predictions if p > 0.5]) >= (len(predictions) / 2) else 0
        return JSONResponse(
            status_code=response.status_code,
            content={
                'miner_predictions': response.json(),
                'prediction': prediction
            }
        )
    except Exception as e:
        logger.error(f"Failed to forward request: {e}")
        raise HTTPException(status_code=500, detail="Failed to forward the request")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=47927)
