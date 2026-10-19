FROM python:3.12-slim
RUN pip install --no-cache-dir httpx huggingface_hub
RUN useradd -m -u 1000 user
USER user
WORKDIR /home/user/app
COPY --chown=user . .
ENV HOST=0.0.0.0 PORT=7860
CMD ["python", "daneval/arena.py"]
