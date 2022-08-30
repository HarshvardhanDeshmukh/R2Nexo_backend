# Superuser Credentials
- username: admin
- password: iceman63

## Setup database
Run below commands in postgresql
```
CREATE DATABASE r2_db;

\c r2_db;

CREATE USER r2 WITH PASSWORD 'r2123456';

ALTER ROLE r2 SET client_encoding TO 'utf8';
ALTER ROLE r2 SET default_transaction_isolation TO 'read committed';
ALTER ROLE r2 SET timezone TO 'Asia/Kolkata';

GRANT ALL PRIVILEGES ON DATABASE r2_db TO r2;
```