# Aiogram3 bot template project

Simple bot that draws watermarks on user images. WIP.
All services in single git repository, monorepository. That's for compact view. We assume that in real job you have git repo per service. 

# Features:
- Aiogram3
- Aiogram-Dialog
- PostgreSQL
- I18n based on Fluent (Fluentogram)
- Bot and worker separated using NATS
- Configs through Dynaconf and Pydantic
- Logging with structlog

# Usage

## Run locally
- git clone https://github.com/Arustinal/aiogram-gdk-course-example
- `cd aiogram-gdk-course-example`
- fill `secrets.toml.example` and rename to `.secrets.toml`, for Linux `mv secrets.toml.example .secrets.toml`
- also set environment variables as described in readme files of services
- download font into img-converter and rename to `font.otf`
- run `docker-compose --profile=infrastructure up`, profiles in `docker-compose.yaml` file

## Bot
- Works in private chats
- `/start`
- `/get_user`

# In case of problems
- go to `Issues` and describe the problem
- go to telegram chat [link](https://t.me/aiogram_stepik_course)
