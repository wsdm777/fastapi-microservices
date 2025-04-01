FROM base

COPY . .

RUN apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

RUN chmod +x /app/entrypoint.sh

RUN poetry install --with user-auth

ENTRYPOINT ["/app/entrypoint.sh"]