from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
app = FastAPI()

class DNSRecordUpdateRequest(BaseModel):
    access_key: str
    secret_key: str
    region: str
    hosted_zone_id: str
    record_name: str
    record_type: str
    record_value: str
    ttl: int
  
def update_route53_record(access_key, secret_key, region, hosted_zone_id, record_name, record_type, record_value, ttl):
    try:
        client = boto3.client(
            'route53',
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )

        response = client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': record_name,
                            'Type': record_type,
                            'TTL': ttl,
                            'ResourceRecords': [{'Value': record_value}],
                        }
                    }
                ]
            }
        )
        return response
    except NoCredentialsError:
        raise HTTPException(status_code=400, detail="Invalid AWS credentials")
    except PartialCredentialsError:
        raise HTTPException(status_code=400, detail="Partial AWS credentials provided")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating DNS record: {str(e)}")

@app.post("/update-record/")
def update_record(request: DNSRecordUpdateRequest):
    try:
        response = update_route53_record(
            request.access_key,
            request.secret_key,
            request.region,
            request.hosted_zone_id,
            request.record_name,
            request.record_type,
            request.record_value,
            request.ttl
        )
        return {"status": "success", "response": response}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
