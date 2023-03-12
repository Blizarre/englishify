from python:3.11

WORKDIR /server

RUN groupadd -r englishify && \
       useradd --no-log-init -r -g englishify englishify && \
       mkdir /youtube_files

RUN pip install poetry && poetry self add poetry-plugin-bundle

COPY pyproject.toml poetry.lock /server/

RUN poetry bundle venv /server/venv/


COPY app.py /server/
COPY static/ /server/static/

USER englishify

EXPOSE 8000

CMD /server/venv/bin/uvicorn app:app --port 8000 --host 0.0.0.0
