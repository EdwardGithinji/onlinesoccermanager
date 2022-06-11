# HOSTING LOCALLY
The designated database is postgres
To set up database to be used, first make sure postgres is install and then go to the psql shell.
After accessing psql shell, do the following:

```bash
CREATE DATABASE yourdatabasename;
CREATE USER youruser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE yourdatabasename TO youruser;
```

If postgis and citext extensions are not default to your postgres template you might also have to do the following:

```bash
\c yourdatabasename;
CREATE EXTENSION POSTGIS;
CREATE EXTENSION CITEXT;
```

Create a ```.env``` file at the root of this project, and in it, define the following:

    DB_NAME - [Compulsory] Db name on PostgreSQL

    DB_USER - [Compulsory] User of PostreSQL db with admin permissions

    DB_PASSWORD - [Compulsory] DB User's password

    DB_HOST - [Compulsory] HOST where PostgreSQL db is located


**Note** replace every ```your...``` with the actual names you used or intend to use.