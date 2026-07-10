FROM python:3.12-slim

WORKDIR /app

# Update OS packages to address known vulnerabilities, install CA certs,
# and clean apt caches to keep the image small.
RUN apt-get update \
	&& apt-get upgrade -y \
	&& apt-get install -y --no-install-recommends ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

# Ensure pip is up-to-date and install dependencies without caching
RUN pip install --no-cache-dir --upgrade pip \
	&& pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY main.py ./

COPY utils/ ./utils/

CMD [ "uv", "run", "main.py", "prod" ]