# Serves the jass players of examples/service/player_service.py over REST.
#
#   docker build -t jass-bot .
#   docker run -p 8888:8888 jass-bot
#   curl http://localhost:8888/random
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY setup.py README.md ./
COPY jass ./jass
RUN pip install '.[service]' gunicorn

COPY examples/service ./service

# trained models; the package is installed into site-packages, so tell it where they are
COPY models ./models
ENV JASS_TRUMP_MODEL=/app/models/trump_linear.npz

RUN useradd --create-home --uid 1000 jass
USER jass

EXPOSE 8888

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8888/random', timeout=4)"

# the agents keep no shared state, so several workers are fine
CMD ["gunicorn", "--chdir", "service", "--bind", "0.0.0.0:8888", "--workers", "2", "--access-logfile", "-", "player_service:create_app()"]
