FROM postgres:17.2

RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-server-dev-all \
    git \
    && git clone https://github.com/citusdata/pg_cron.git \
    && cd pg_cron \
    && make && make install \
    && cd .. \
    && rm -rf pg_cron \
    && apt-get clean
    

RUN echo "shared_preload_libraries = 'pg_cron'" >> /usr/share/postgresql/postgresql.conf.sample

COPY ./init-cron.sh /docker-entrypoint-initdb.d/init-cron.sh

CMD ["postgres"]