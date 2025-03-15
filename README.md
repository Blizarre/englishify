**Note:** *I archived this project as after a few years the ecosystem has started to catch up and this service is now baked in at all levels of the stack: in your OS, in your browser, in your application, in your glasses even.*

# Englishify

This is a weekend project that utilizes Chat-GPT to help non-native English speakers enhance their writing abilities. It simply asks ChatGPT to rewrite their text using a selection of dialects and use cases.

It's the code behind the website https://englishify.uk.

## Run

```
# Leave SENTRY_SDK_URL empty if you don't plan to use Sentry.
OPENAI_API_KEY=YOUR_KEY SENTRY_SDK_URL= poetry run uvicorn app:app --port 8080 --reload
```
