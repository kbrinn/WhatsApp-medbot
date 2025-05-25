FROM postgres:15

# Set default environment variables (override in docker-compose or at runtime)
ENV POSTGRES_DB clinicdb
ENV POSTGRES_USER medbot
ENV POSTGRES_PASSWORD medbotpassword

# Copy initialization scripts
COPY init/ /docker-entrypoint-initdb.d/