# PostgreSQL Backup

Docker image that dumps/restores a Postgres database to/from an AWS S3
bucket.

## Required environment variables

- `DB_HOST`: Postgres hostname
- `DB_PASS`: Postgres password
- `DB_USER`: Postgres username
- `DB_NAME`: Name of database
- `S3_BUCKET`: AWS S3 bucket name
- `S3_KEY`: AWS S3 key name for the output object

## Optional environment variables

- `COMPRESSED`: Store a compressed gzip backup
- `S3_PREFIX`: AWS S3 key prefix for the output object (optional)
  * If this is used, the output filename will be timestamped after the prefix
  * This option and `S3_KEY` are mutually exclusive

## Restoring a backup

This image can also be run as a one off task to restore one of the
backups. To do this run the container with the command: `restore`.

The following environment variables are required:

- `DB_HOST`: Postgres hostname
- `DB_PASS`: Postgres password
- `DB_USER`: Postgres username
- `DB_NAME`: Name of database
- `S3_BUCKET`: AWS S3 bucket name
- `S3_KEY`: AWS S3 key name for the input object
- `COMPRESSED`: Restore a compressed gzip backup