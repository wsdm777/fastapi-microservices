FROM base

COPY . .

RUN chmod +x /app/entrypoint.sh

RUN poetry install --with user-auth

ENTRYPOINT ["/app/entrypoint.sh"]