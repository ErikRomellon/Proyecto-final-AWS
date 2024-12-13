import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import uuid

# Configuración AWS
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_SESSION_TOKEN = ""
AWS_REGION = ""
AWS_BUCKET_NAME = ""

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=AWS_REGION,
)

def upload_image_to_s3(file_path, bucket_name, object_name=None):
    if object_name is None:
        object_name = str(uuid.uuid4()) + ".jpg"

    try:
        s3_client.upload_file(file_path, bucket_name, object_name, ExtraArgs={"ACL": "public-read", "ContentType": "image/jpeg"})
        print(f"File uploaded successfully. URL: https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{object_name}")
    except FileNotFoundError:
        print("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")
    except PartialCredentialsError:
        print("Incomplete credentials provided")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    file_path = r'C:\Users\mugui\Documents\AWS\Proyecto\sicei-autotest-database\src\test\resources\cat_test.jpg'  # Reemplaza con la ruta a tu imagen
    upload_image_to_s3(file_path, AWS_BUCKET_NAME)