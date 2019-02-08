=========================
Docker PostgreSQL Backup
=========================

Docker image that dumps a Postgres database and uploads it to an Amazon S3 bucket.

Required environment variables
==============================

* :code:`DB_HOST`: Postgres hostname
* :code:`DB_PASS`: Postgres password
* :code:`DB_USER`: Postgres username
* :code:`DB_NAME`: Name of database
* :code:`S3_PATH`: Amazon S3 path in the format: s3://bucket-name/some/path

Optional environment variables
==============================

* :code:`KEEP_BACKUP_DAYS`: The number of days to keep backups for when pruning old backups

Restoring a backup
==================

This image can also be run as a one off task to restore one of the backups. 
To do this run the container with the command: :code:`/backup/restore.sh [S3-filename]`.

The following environment variables are required:

* :code:`DB_HOST`: Postgres hostname
* :code:`DB_PASS`: Postgres password
* :code:`DB_USER`: Postgres username
* :code:`DB_NAME`: Name of database

