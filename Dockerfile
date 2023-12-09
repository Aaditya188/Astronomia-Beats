FROM python:3.10-slim

WORKDIR /app

COPY . .

ARG HEROKU_DB
ENV HEROKU_DB=$HEROKU_DB

# config env vars
ENV BOT_TOKEN=YOUR_TOKEN_GOES_HERE
ENV SPOTIFY_ID=
ENV SPOTIFY_SECRET=
ENV BOT_PREFIX=$
ENV ENABLE_SLASH_COMMANDS=False
ENV MENTION_AS_PREFIX=True
ENV VC_TIMEOUT=600
ENV VC_TIMEOUT_DEFAULT=True
ENV ALLOW_VC_TIMEOUT_EDIT=True
ENV MAX_SONG_PRELOAD=5
ENV MAX_HISTORY_LENGTH=10
ENV MAX_TRACKNAME_HISTORY_LENGTH=15
ENV DATABASE_URL=sqlite:///settings.db
ENV ENABLE_BUTTON_PLUGIN=True
ENV EMBED_COLOR=0x4DD4D0
ENV SUPPORTED_EXTENSIONS="('.webm', '.mp4', '.mp3', '.avi', '.wav', '.m4v', '.ogg', '.mov')"
ENV COOKIE_PATH=config/cookies/cookies.txt
ENV GLOBAL_DISABLE_AUTOJOIN_VC=False

RUN pip --no-cache-dir install -r requirements.txt \
    && apt-get update \
    && apt-get install --no-install-recommends ffmpeg -y

CMD ["python", "run.py"]
