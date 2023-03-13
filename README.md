# Englishify

This is a weekend project that utilizes Chat-GPT to help non-native English speakers enhance their writing abilities. It simply asks ChatGPT to rewrite their text using a selection of dialects and use cases. 

It's the code behind the website https://englishify.uk.

## Run

```
OPENAI_API_KEY=YOUR_KEY SENTRY_SDK_URL=YOUR_URL poetry run uvicorn app:app --port 8080 --reload
```
