# -*- coding: utf-8 -*-

import oss2
import argparse
import time
import os

parser = argparse.ArgumentParser(
    description='Backup an Aliyun OSS bucket to local machine and qiniu')
parser.add_argument('bucket', help='the bucket to be backuped')
parser.add_argument('dst', help='the local backup folder')
parser.add_argument('aliKey', help='the access key id of ali OSS')
parser.add_argument('aliSecret', help='the access key secret of ali OSS')
parser.add_argument('--qi-key', '-k', help='the access key of QiNiu')
parser.add_argument('--qi-secret', '-s', help='the secret key of QiNiu')
args = parser.parse_args()

feature_name = 'ali%s-%s' % (time.strftime("%m.%d"), args.bucket)
basedir = os.path.join(args.dst, feature_name)
endpoint = 'http://oss-cn-beijing.aliyuncs.com'
qiniuBucket = 'oss-backup'

from contextlib import contextmanager
@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def save_file(bkt, rootdir, obj):
    curdir = os.path.join(rootdir, os.path.dirname(obj))
    filename = os.path.basename(obj)
    print('save %s to %s' % (filename, curdir))
    if not os.path.exists(curdir): os.makedirs(curdir)
    with cd(curdir):
        bkt.get_object_to_file(obj, filename)


def sync2qiniu(filename, bkt, key, secret):
    import qiniu
    q = qiniu.Auth(key, secret)
    token = q.upload_token(bkt, filename, 3600)
    print('Send %s to qiniu ...' % filename)
    ret, info = qiniu.put_file(token, filename, filename)
    if (ret['key'] == filename) and (ret['hash'] == qiniu.etag(filename)):
        print('upload successful')

if __name__ == "__main__":
    auth = oss2.Auth(args.aliKey, args.aliSecret)
    service = oss2.Service(auth, endpoint)
    bucket = oss2.Bucket(auth, endpoint, args.bucket)

    for object_info in oss2.ObjectIterator(bucket):
        save_file(bucket, basedir, object_info.key)

    archFile = feature_name + '.tar.gz'
    import subprocess
    subprocess.call('tar zcf %s %s' % (archFile, feature_name),
            shell=True, cwd=args.dst)

    if (args.qi_key is None) or (args.qi_secret is None):
        print('backup successful')
        import sys
        sys.exit(0)
    with cd(args.dst):
        sync2qiniu(archFile, qiniuBucket, args.qi_key, args.qi_secret)
