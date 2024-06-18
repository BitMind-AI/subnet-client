from cryptography.hazmat.primitives import serialization
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import base64
import logging
import requests

app = FastAPI()
app_port = 8000

validator_ip = '127.0.0.1'
validator_proxy_port = 47926

# Load the private key from a file
with open("private_key.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

# Load the public key from a file
with open("public_key.pem", "rb") as f:
    public_key = serialization.load_pem_public_key(f.read())


def get_public_key():
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    encoded_public_key = base64.b64encode(public_key_bytes).decode('utf-8')
    return encoded_public_key


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
        message = b"bitmindaigeneratedimagedetectionsubnet"
        
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


@app.get("/miner_performance")
async def miner_performance():
    try:
        # Construct the URL for forwarding the request
        forward_url = f"http://{validator_ip}:{validator_proxy_port}/miner_performance"
        print(forward_url)

        # Forward the request to the last client
        data = {}
        data['authorization'] = get_public_key()

        response = requests.get(forward_url, json=data)
        predictions = response.json()
        print('validator response', predictions)

        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )
    except Exception as e:
        logger.error(f"Failed to forward request: {e}")
        raise HTTPException(status_code=500, detail="Failed to forward the request")


@app.post("/forward_image")
async def forward_image(request: ImageRequest):
    try:
        # Construct the URL for forwarding the request
        forward_url = f"http://{validator_ip}:{validator_proxy_port}/validator_proxy"
        print(forward_url)

        # Forward the request to the last client
        data = request.dict()
        data['authorization'] = get_public_key()

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
    uvicorn.run(app, host="0.0.0.0", port=app_port)
