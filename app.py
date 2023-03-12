from contextlib import asynccontextmanager
import logging
from enum import Enum

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

import aiohttp
from pydantic import BaseModel
from pydantic import BaseSettings

logging.basicConfig()
logger = logging.getLogger("englishify")
logger.setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(application: FastAPI):
    async with aiohttp.ClientSession() as session:
        application.state.aiohttp = session
        yield


class Settings(BaseSettings):
    openai_api_key: str


app = FastAPI(title="englishify", lifespan=lifespan)
settings = Settings()


class Formality(str, Enum):
    VERY = "very"
    WORK = "work"
    GENERIC = "generic"
    CASUAL = "casual"


FORMAL_PROMPT = {
    Formality.CASUAL: "Like you would talk to your best friend",
    Formality.WORK: "Like you would write on a work email to a colleague",
    Formality.VERY: "Like you would write on a letter to a monarch",
    Formality.GENERIC: "",
}


class Prompt(BaseModel):
    prompt: str
    temperature: float
    formal: Formality


class Response(BaseModel):
    response: str


@app.post(
    "/englishify",
)
async def englishify(prompt: Prompt) -> Response:
    # https://platform.openai.com/docs/api-reference/completions/create
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "I will write a text written by a non-native english speaker."
                + f"I would like you to rewrite slightly it in the style of a native British speaker, {FORMAL_PROMPT[prompt.formal]}.",
            },
            {"role": "user", "content": prompt.prompt},
        ],
        "temperature": prompt.temperature,
    }
    logger.info("Sending payload %s", payload)
    async with app.state.aiohttp.post(
        "https://api.openai.com/v1/chat/completions",
        json=payload,
        headers={
            "Authorization": f"Bearer {settings.openai_api_key}",
        },
        timeout=30,
    ) as response:
        response_data = await response.json()

        if error := response_data.get("error"):
            logger.warning("Error message from OpenAPI: %s", error["message"])

        response.raise_for_status()

        return Response(response=response_data["choices"][0]["message"]["content"])


app.mount("/", StaticFiles(html=True, directory="static"), name="static")
