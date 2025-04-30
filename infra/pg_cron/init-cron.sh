#!/bin/bash

psql -U $POSTGRES_USER -d $POSTGRES_DB -c "CREATE EXTENSION IF NOT EXISTS pg_cron;"

psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
    "SELECT cron.schedule('0 0 * * *', \$\$DELETE FROM refresh_tokens WHERE expired_at < NOW();\$\$);"
