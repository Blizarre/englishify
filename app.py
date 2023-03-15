from contextlib import asynccontextmanager
import logging
from enum import Enum

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException

import aiohttp
from pydantic import BaseModel
from pydantic import BaseSettings

import sentry_sdk
from sentry_sdk import capture_message

logging.basicConfig()
logger = logging.getLogger("englishify")
logger.setLevel(logging.INFO)


class Settings(BaseSettings):
    openai_api_key: str
    sentry_sdk_url: str


class Formality(str, Enum):
    VERY = "very"
    WORK = "work"
    GENERIC = "generic"
    CASUAL = "casual"


class Dialect(str, Enum):
    AMERICAN = "american"
    BRITISH = "british"
    AUSTRALIAN = "australian"


FORMAL_PROMPT = {
    Formality.CASUAL: "I would like you to rewrite it in the style of a very casual message by a {dialect} to its friend",
    Formality.WORK: "I would like you to rewrite it slightly in the style of a business email written by a native {dialect} to a colleague.",
    Formality.VERY: "I would like you to rewrite it as if it was a letter to a powerful monarch written by a {dialect}",
    Formality.GENERIC: "I would like you to rewrite it slightly in the style of a native {dialect} in a business context.",
}

MAX_LEMGTH = 4096

@asynccontextmanager
async def lifespan(application: FastAPI):
    settings = Settings()
    application.state.settings = settings

    sentry_sdk.init(
        settings.sentry_sdk_url,
        traces_sample_rate=1.0,
    )

    async with aiohttp.ClientSession() as session:
        application.state.aiohttp = session
        yield

app = FastAPI(title="englishify", lifespan=lifespan)

class Prompt(BaseModel):
    prompt: str
    temperature: float
    formal: Formality
    dialect: Dialect


class Response(BaseModel):
    response: str


@app.post("/englishify")
async def englishify(prompt: Prompt) -> Response:
    if len(prompt.prompt) > MAX_LEMGTH:
        raise HTTPException(status_code=400, detail=f"Prompt too long (max {MAX_LEMGTH} chars)")

    # https://platform.openai.com/docs/api-reference/completions/create
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "I will write a text written by a non-native english speaker. "
                + FORMAL_PROMPT[prompt.formal].format(dialect=prompt.dialect)
            },
            {"role": "user", "content": prompt.prompt},
        ],
        "temperature": prompt.temperature,
    }
    logger.debug("Sending payload %s", payload)
    async with app.state.aiohttp.post(
        "https://api.openai.com/v1/chat/completions",
        json=payload,
        headers={
            "Authorization": f"Bearer {app.state.settings.openai_api_key}",
        },
        timeout=30,
    ) as response:
        response_data = await response.json()

        if error := response_data.get("error"):
            logger.warning("Error message from OpenAPI: %s (code %d)", error["message"], response.status)
            capture_message(error["message"])
            raise HTTPException(status_code=500, detail=error["message"])

        response.raise_for_status()

        return Response(response=response_data["choices"][0]["message"]["content"])


app.mount("/", StaticFiles(html=True, directory="static"), name="static")
