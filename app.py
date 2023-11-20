from contextlib import asynccontextmanager
import logging
from enum import Enum
from fastapi.responses import StreamingResponse

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException

from openai import APIError, AuthenticationError, OpenAI

from pydantic import BaseModel
from pydantic import BaseSettings

import sentry_sdk
from sentry_sdk import capture_message

logging.basicConfig()
logger = logging.getLogger("englishify")
logger.setLevel(logging.INFO)


class Settings(BaseSettings):
    sentry_sdk_url: str


class Formality(str, Enum):
    VERY = "very"
    EMAIL = "email"
    GENERIC = "generic"
    CASUAL = "casual"


class Dialect(str, Enum):
    AMERICAN = "american"
    BRITISH = "british"
    AUSTRALIAN = "australian"
    GENERIC = "generic"


DIALECT_STRING = {
    Dialect.AMERICAN: "an american",
    Dialect.BRITISH: "a british",
    Dialect.AUSTRALIAN: "an australian",
    Dialect.GENERIC: "an english",
}

FORMAL_PROMPT = {
    Formality.CASUAL: "I would like you to rewrite it in the style of a very casual message by {dialect} speaker to its friend",
    Formality.EMAIL: "I would like you to rewrite it slightly in the style of a business email written by {dialect} speaker to a colleague.",
    Formality.VERY: "I would like you to rewrite it as if it was a letter to a powerful monarch written by {dialect} speaker",
    Formality.GENERIC: "I would like you to rewrite it slightly in the style of {dialect} speaker in a business context.",
}

MAX_LENGTH = 4096


@asynccontextmanager
async def lifespan(application: FastAPI):
    settings = Settings()
    application.state.settings = settings

    sentry_sdk.init(
        settings.sentry_sdk_url,
        traces_sample_rate=1.0,
    )

    application.state.client = OpenAI()
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
    if len(prompt.prompt) > MAX_LENGTH:
        raise HTTPException(status_code=400, detail=f"Prompt too long (max {MAX_LENGTH} chars)")
    logger.info("Received request, forwarding it to OpenAI")
    openai: OpenAI = app.state.client

    try:
        stream = openai.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                    "role": "system",
                    "content": "I will write a text written by a non-native english speaker. "
                    + FORMAL_PROMPT[prompt.formal].format(dialect=DIALECT_STRING[prompt.dialect]),
                },
                {"role": "user", "content": prompt.prompt},
            ],
            temperature=prompt.temperature,
            stream=True,
        )
    except AuthenticationError as e:
        logger.exception("Invalid API key")
        raise HTTPException(status_code=500, detail="Something went wrong with the authentication to OpenAI. Please retry later.")
    except APIError as e:
        logger.exception("Unknown OpenAI Error")
        raise HTTPException(status_code=500, detail=e.message)

    def steam_response():
        """Forward the chunks to the client, one per line"""
        for part in stream: yield part.choices[0].model_dump_json() + "\n"

    logger.info("Received response, streaming it to the client")

    return StreamingResponse(steam_response())


app.mount("/", StaticFiles(html=True, directory="static"), name="static")
