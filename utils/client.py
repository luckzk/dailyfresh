from fdfs_client.client import Fdfs_client

client = Fdfs_client('/etc/fdfs/client.conf')
ret = client.upload_by_fileame('test')
print(ret)