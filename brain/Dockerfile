# rover-brain MCP server as a container: Streamable HTTP on :8000 at /mcp.
# All hosts, keys and passwords come from the environment (a k8s Secret),
# never from the image. Build from the repo root:
#   docker build -f brain/Dockerfile -t rover-brain .
FROM python:3.12-slim
WORKDIR /app
COPY brain/requirements.txt brain/requirements.txt
RUN pip install --no-cache-dir -r brain/requirements.txt
COPY brain/ brain/
RUN useradd -r -u 10001 brain && rm -rf brain/.venv brain/__pycache__
USER 10001
ENV BRAIN_TRANSPORT=http BRAIN_HOST=0.0.0.0 BRAIN_PORT=8000 PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["python", "-m", "brain.server"]
