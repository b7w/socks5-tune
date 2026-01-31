FROM redgate/flyway:12.0-alpine

COPY src/migrations/*.sql /flyway/sql/
COPY src/migrations/flyway.conf /flyway/conf/
