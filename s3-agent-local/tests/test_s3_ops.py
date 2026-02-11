"""
Unit tests for S3 operations
Uses moto to mock AWS S3 without actual AWS costs
"""
import pytest
import boto3
from moto import mock_s3


@mock_s3
def test_list_objects():
    """Test listing S3 objects (scan_folder operation)"""
    # Setup
    s3 = boto3.client('s3', region_name='us-west-2')
    s3.create_bucket(
        Bucket='test-bucket',
        CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
    )
    s3.put_object(Bucket='test-bucket', Key='file1.txt', Body=b'content1')
    s3.put_object(Bucket='test-bucket', Key='file2.txt', Body=b'content2')
    s3.put_object(Bucket='test-bucket', Key='docs/file3.txt', Body=b'content3')

    # Test
    response = s3.list_objects_v2(Bucket='test-bucket')

    # Verify
    assert 'Contents' in response
    assert len(response['Contents']) == 3
    keys = [obj['Key'] for obj in response['Contents']]
    assert 'file1.txt' in keys
    assert 'file2.txt' in keys
    assert 'docs/file3.txt' in keys


@mock_s3
def test_list_with_prefix():
    """Test listing with prefix (folder simulation)"""
    s3 = boto3.client('s3', region_name='us-west-2')
    s3.create_bucket(
        Bucket='test-bucket',
        CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
    )
    s3.put_object(Bucket='test-bucket', Key='docs/report.pdf', Body=b'pdf content')
    s3.put_object(Bucket='test-bucket', Key='docs/data.csv', Body=b'csv content')
    s3.put_object(Bucket='test-bucket', Key='images/photo.jpg', Body=b'jpg content')

    # Test with prefix
    response = s3.list_objects_v2(Bucket='test-bucket', Prefix='docs/')

    assert len(response['Contents']) == 2
    assert all('docs/' in obj['Key'] for obj in response['Contents'])


@mock_s3
def test_get_object():
    """Test getting object content (read_file operation)"""
    s3 = boto3.client('s3', region_name='us-west-2')
    s3.create_bucket(
        Bucket='test-bucket',
        CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
    )

    test_content = b'Hello, S3!'
    s3.put_object(Bucket='test-bucket', Key='test.txt', Body=test_content)

    # Test
    response = s3.get_object(Bucket='test-bucket', Key='test.txt')
    content = response['Body'].read()

    assert content == test_content


@mock_s3
def test_get_object_with_range():
    """Test preview_file operation with Range header"""
    s3 = boto3.client('s3', region_name='us-west-2')
    s3.create_bucket(
        Bucket='test-bucket',
        CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
    )

    test_content = b'0123456789' * 100  # 1000 bytes
    s3.put_object(Bucket='test-bucket', Key='large.txt', Body=test_content)

    # Test - get only first 100 bytes
    response = s3.get_object(
        Bucket='test-bucket',
        Key='large.txt',
        Range='bytes=0-99'
    )
    content = response['Body'].read()

    assert len(content) == 100
    assert content == test_content[:100]


@mock_s3
def test_head_object():
    """Test getting object metadata without downloading content"""
    s3 = boto3.client('s3', region_name='us-west-2')
    s3.create_bucket(
        Bucket='test-bucket',
        CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
    )

    test_content = b'Test content for metadata'
    s3.put_object(
        Bucket='test-bucket',
        Key='test.txt',
        Body=test_content,
        ContentType='text/plain'
    )

    # Test
    response = s3.head_object(Bucket='test-bucket', Key='test.txt')

    assert response['ContentLength'] == len(test_content)
    assert response['ContentType'] == 'text/plain'


@mock_s3
def test_put_object():
    """Test uploading object to S3"""
    s3 = boto3.client('s3', region_name='us-west-2')
    s3.create_bucket(
        Bucket='test-bucket',
        CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
    )

    # Test
    s3.put_object(
        Bucket='test-bucket',
        Key='uploads/newfile.txt',
        Body=b'New content',
        ContentType='text/plain'
    )

    # Verify
    response = s3.get_object(Bucket='test-bucket', Key='uploads/newfile.txt')
    content = response['Body'].read()
    assert content == b'New content'


@mock_s3
def test_pagination():
    """Test pagination for large result sets"""
    s3 = boto3.client('s3', region_name='us-west-2')
    s3.create_bucket(
        Bucket='test-bucket',
        CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
    )

    # Create many objects
    for i in range(150):
        s3.put_object(Bucket='test-bucket', Key=f'file{i}.txt', Body=b'content')

    # Test pagination
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket='test-bucket')

    all_objects = []
    for page in pages:
        all_objects.extend(page.get('Contents', []))

    assert len(all_objects) == 150


@mock_s3
def test_delete_object():
    """Test deleting object from S3"""
    s3 = boto3.client('s3', region_name='us-west-2')
    s3.create_bucket(
        Bucket='test-bucket',
        CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
    )
    s3.put_object(Bucket='test-bucket', Key='to-delete.txt', Body=b'delete me')

    # Test
    s3.delete_object(Bucket='test-bucket', Key='to-delete.txt')

    # Verify deleted
    response = s3.list_objects_v2(Bucket='test-bucket')
    assert 'Contents' not in response or len(response.get('Contents', [])) == 0


@mock_s3
def test_file_not_found_error():
    """Test error handling for non-existent file"""
    s3 = boto3.client('s3', region_name='us-west-2')
    s3.create_bucket(
        Bucket='test-bucket',
        CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
    )

    # Test
    from botocore.exceptions import ClientError
    with pytest.raises(ClientError) as exc_info:
        s3.get_object(Bucket='test-bucket', Key='nonexistent.txt')

    assert exc_info.value.response['Error']['Code'] == 'NoSuchKey'


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, '-v'])
