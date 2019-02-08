#!/usr/bin/python

import os
import sys
import argparse
import datetime
import subprocess
import gzip
import logging
import tempfile

import boto3


logging_root = logging.getLogger()
logging_root.setLevel(logging.getLevelName(os.getenv('LOGLEVEL', 'INFO')))

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('{asctime} {name} [{levelname}] {message}', style='{'))

logging_root.addHandler(handler)


def get_database_dump(compress, host, port, database, user, password):
    proc_environment = os.environ.copy()
    proc_environment['PG_PASSWORD'] = password

    output = subprocess.check_output(
        ['pg_dump', '-E', 'utf-8', '-w', '-O', '-h', host, '-U', user, '-p', str(port), database],
        stderr=sys.stdout, env=proc_environment
    )

    if compress:
        output = gzip.compress(output)

    return output


def do_backup(compressed, s3_bucket, s3_key, host, port, database, user, password):
    logger = logging.getLogger('backup')

    logger.info('starting backup')
    dump = get_database_dump(compressed, host, port, database, user, password)
    logger.info('finished backup, size: {0} bytes'.format(len(dump)))

    logger.info('starting upload to s3://{bucket}/{key}'.format(bucket=s3_bucket, key=s3_key))
    s3 = boto3.client('s3')
    s3.put_object(
        Body=dump,
        Bucket=s3_bucket,
        Key=s3_key
    )

    logger.info('finished upload')
    logger.info('finished backup')


def get_sql_from_s3(compressed, s3_bucket, s3_key):
    logger = logging.getLogger('download')
    logger.info('getting file from s3')

    s3 = boto3.client('s3')
    response = s3.get_object(
        Bucket=s3_bucket,
        Key=s3_key
    )

    body = response['Body'].read()
    logger.info('received file from s3, length: {}'.format(len(body)))

    if compressed:
        body = gzip.decompress(body)

    return body.decode('utf-8')


def run_sql_file(sql_file_path, host, port, user, password, database):
    proc_environment = os.environ.copy()
    proc_environment['PG_PASSWORD'] = password

    subprocess.check_call(
        ['psql', '-q', '-d', database, '-f', sql_file_path, '-h', host, '-U', user, '-p', str(port)],
        env=proc_environment
    )


def do_restore(compressed, s3_bucket, s3_key, host, port, database, user, password):
    logger = logging.getLogger('restore')

    logger.info('starting restore')
    sql_contents = get_sql_from_s3(compressed, s3_bucket, s3_key)

    sql_file_fd, sql_file_path = tempfile.mkstemp()

    sql_file = os.fdopen(sql_file_fd, mode='wb')
    sql_file.write(sql_contents.encode('utf-8'))
    sql_file.close()

    logger.info('running psql')
    try:
        run_sql_file(sql_file_path, host, port, user, password, database)
    except:
        raise
    finally:
        os.unlink(sql_file_path)

    logger.info('finished restore')


def main():
    parser = argparse.ArgumentParser(description='Backup or restore a postgres database to s3')

    op_group = parser.add_mutually_exclusive_group(required=True)
    op_group.add_argument('-b', '--backup', action='store_true')
    op_group.add_argument('-r', '--restore', action='store_true')

    key_group = parser.add_mutually_exclusive_group(required=True)
    key_group.add_argument('--s3-key', type=str, help='full s3 object key path for the dump')
    key_group.add_argument('--s3-prefix', type=str, help='s3 object key prefix for the dump. key will be obtained by '
                                                         'the date and time')

    parser.add_argument('--compressed', action='store_true', help='use compressed dump (.gz)')
    parser.add_argument('--s3-bucket', type=str, required=True, help='output bucket for the dump')
    parser.add_argument('--host', type=str, required=True, help='host to connect to')
    parser.add_argument('--database', type=str, required=False, help='database name')
    parser.add_argument('--port', type=int, default=5432, help='port to connect to')
    parser.add_argument('--user', type=str, required=True, help='user name to use for the operation')
    parser.add_argument('--password', type=str, required=False,
                        help='password for the database, please prefer using the DB_PASSWORD '
                        'environment variable over this switch')

    args = parser.parse_args()

    password = os.getenv('DB_PASSWORD') or args.password
    if password is None:
        print('missing connection password, use --password or the DB_PASSWORD environment variable', file=sys.stderr)
        sys.exit(1)

    args.password = password

    operation = None
    if args.backup:
        operation = do_backup
    elif args.restore:
        operation = do_restore

    if args.s3_prefix:
        if args.restore:
            print('cannot use --restore and --s3-prefix')
            sys.exit(1)

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        args.s3_key = args.s3_prefix + timestamp + ('.sql.gz' if args.compressed else '.sql')

    logger = logging.getLogger('main')
    logger.info('starting operation')

    try:
        operation(args.compressed, args.s3_bucket, args.s3_key, args.host, args.port, args.database, args.user, args.password)
    except Exception:
        logger.exception('stopped')
    else:
        logger.info('finished with success')


if __name__ == "__main__":
    main()
