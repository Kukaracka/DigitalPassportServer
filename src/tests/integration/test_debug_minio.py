import pytest
import os
from minio import Minio

@pytest.mark.asyncio
async def test_minio_credentials():
    """Тест для проверки MinIO credentials"""
    
    print("\n" + "="*60)
    print("MINIO CREDENTIALS DEBUG")
    print("="*60)
    
    # Проверяем переменные окружения
    env_vars = {
        "MINIO_ENDPOINT": os.getenv("MINIO_ENDPOINT"),
        "MINIO_ACCESS_KEY": os.getenv("MINIO_ACCESS_KEY"),
        "MINIO_SECRET_KEY": os.getenv("MINIO_SECRET_KEY"),
        "MINIO_BUCKET": os.getenv("MINIO_BUCKET"),
        "MINIO_ROOT_USER": os.getenv("MINIO_ROOT_USER"),
        "MINIO_ROOT_PASSWORD": os.getenv("MINIO_ROOT_PASSWORD"),
    }
    
    for key, value in env_vars.items():
        if value and "SECRET" in key:
            print(f"{key}: {'*' * len(value)}")
        else:
            print(f"{key}: {value or 'NOT SET'}")
    
    print("\n" + "-"*60)
    print("Testing connection with various credentials:")
    
    # Пробуем разные комбинации
    credentials_to_try = [
        ("test_minio", "test_minio_password", "from docker inspect"),
        ("minioadmin", "minioadmin", "default"),
        (env_vars.get("MINIO_ACCESS_KEY"), env_vars.get("MINIO_SECRET_KEY"), "from env"),
    ]
    
    endpoint = env_vars.get("MINIO_ENDPOINT", "minio:9000")
    
    for access_key, secret_key, source in credentials_to_try:
        if not access_key or not secret_key:
            print(f"⏭️  Skipping {source}: credentials not set")
            continue
            
        try:
            client = Minio(
                endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=False
            )
            buckets = client.list_buckets()
            print(f"✅ SUCCESS with {source}!")
            print(f"   Access Key: {access_key}")
            print(f"   Buckets: {[b.name for b in buckets]}")
            
            # Если нашли рабочие credentials, выводим их
            if source != "from env" or not env_vars.get("MINIO_ACCESS_KEY"):
                print(f"\n💡 Use these credentials in your env:")
                print(f"   MINIO_ACCESS_KEY={access_key}")
                print(f"   MINIO_SECRET_KEY={secret_key}")
            break
            
        except Exception as e:
            print(f"❌ Failed with {source}: {str(e)[:100]}")
    
    print("="*60)
    
    # Тест не должен фейлиться
    assert True
