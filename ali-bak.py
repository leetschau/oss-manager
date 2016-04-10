# -*- coding: utf-8 -*-

import oss2
import argparse
import time
import os
from contextlib import contextmanager

parser = argparse.ArgumentParser(
    description='Backup an Aliyun OSS bucket on local machine')
parser.add_argument('bucket', help='the bucket to be backuped')
parser.add_argument('dst', help='the local backup folder')
parser.add_argument('key',
        help='the access key id of the bucket to be backuped')
parser.add_argument('secret',
        help='the access key secret of the bucket to be backuped')
args = parser.parse_args()

basedir = os.path.join(args.dst,
              'ali%s-%s' % (time.strftime("%m.%d"), args.bucket))
endpoint = 'http://oss-cn-beijing.aliyuncs.com'
access_key_id, access_key_secret = (args.key, args.secret)

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def save_file(bkt, rootdir, key):
    curdir = os.path.join(rootdir, os.path.dirname(key))
    filename = os.path.basename(key)
    print('save %s to %s' % (filename, curdir))
    if not os.path.exists(curdir): os.makedirs(curdir)
    with cd(curdir):
        bkt.get_object_to_file(key, filename)


if __name__ == "__main__":
    auth = oss2.Auth(access_key_id, access_key_secret)
    service = oss2.Service(auth, endpoint)
    bucket = oss2.Bucket(auth, endpoint, args.bucket)

    for object_info in oss2.ObjectIterator(bucket):
        save_file(bucket, basedir, object_info.key)

