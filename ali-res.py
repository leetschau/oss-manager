# -*- coding: utf-8 -*-

import oss2
import argparse
import time
import os
from contextlib import contextmanager

parser = argparse.ArgumentParser(
    description='Restore an Aliyun OSS bucket from local machine')
parser.add_argument('source',
        help='the local backup folder, make sure it exists')
parser.add_argument('bucket',
        help='the bucket to be restored, make sure it exists')
parser.add_argument('key',
        help='the access key id of the bucket to be restored')
parser.add_argument('secret',
        help='the access key secret of the bucket to be restored')
args = parser.parse_args()

endpoint = 'http://oss-cn-beijing.aliyuncs.com'
access_key_id, access_key_secret = (args.key, args.secret)


def upload_file(bkt, basedir, filename):
    key = filename.split(basedir)[1][1:]
    print('uploading %s to %s' % (filename, key))
    bkt.put_object_from_file(key, filename)


if __name__ == "__main__":
    auth = oss2.Auth(access_key_id, access_key_secret)
    service = oss2.Service(auth, endpoint)
    bucket = oss2.Bucket(auth, endpoint, args.bucket)
    for root, dirs, files in os.walk(args.source):
        for af in files:
            upload_file(bucket, args.source, os.path.join(root, af))

