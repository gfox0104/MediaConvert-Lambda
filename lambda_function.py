#Python
# # Import necessary libraries
import boto3
import json
from datetime import datetime

# # Create S3 and MediaConvert clients
s3 = boto3.client("s3")
mediaconvert = boto3.client("mediaconvert")

# Lambda function handler
def lambda_handler(event, context):
    print("Received event:")
    print(json.dumps(event))

    print(f"data[bucket]->")
    print(event["bucket"])

    # Extract relevant information from the S3 event
    bucket = event["bucket"]
    key = event["key"]
    extension = event["extension"]
    screen_index = event["screen_index"]

    # Define job parameters for MediaConvert
    job_params = {
        "Queue": "arn:aws:mediaconvert:us-east-2:605793766297:queues/Default",
        "UserMetadata": {
        "thumbnail": "true"
        },
        "Role": "arn:aws:iam::605793766297:role/autoclipper-thumbnail-MediaConvertRole",
        "Settings": {
            "Inputs": [{
            "FileInput": f"s3://{bucket}/{key}"
            }],
            "OutputGroups": [
                {
                    "Name": "File Group",
                    "OutputGroupSettings": {
                    "Type": "FILE_GROUP_SETTINGS",
                    "FileGroupSettings": {
                            "Destination": f"s3://autoclipper/thumbnails/"
                        }
                    },
                    "Outputs": [
                        {
                            "VideoDescription": {
                                "Width": 300,
                                "ScalingBehavior": "DEFAULT",
                                "Height": 300,
                                "CodecSettings": {
                                    "Codec": "FRAME_CAPTURE",
                                    "FrameCaptureSettings": {
                                        "FramerateNumerator": 1,
                                        "FramerateDenominator": 1,
                                        "MaxCaptures": screen_index,
                                        "Quality": 80
                                    }
                                }
                            },
                            "ContainerSettings": {
                                "Container": "RAW"
                            },
                            "Extension": extension,
                            "NameModifier": f"-thumbnail" # Use video file name without extension
                        },
                        {
                            "VideoDescription": {
                                "Width": 1920, # Adjust as needed
                                "ScalingBehavior": "DEFAULT",
                                "Height": 1080, # Adjust as needed
                                "CodecSettings": {
                                    "Codec": "H_264",
                                    "H264Settings": {
                                        "Bitrate": 5000000,
                                        "FramerateControl": "INITIALIZE_FROM_SOURCE",
                                        "RateControlMode": "CBR",
                                        "CodecProfile": "MAIN",
                                        "GopSize": 30, # Adjust as needed
                                        "NumberBFramesBetweenReferenceFrames": 2,
                                        "Syntax": "DEFAULT"
                                    }
                                }
                            },
                        "ContainerSettings": {
                            "Container": "MP4"
                        },
                        "Extension": "mp4",
                        "NameModifier": f"-fullvideo" # Use video file name without extension
                        }
                    ]
                }
            ]
        }
    }

    try:
        # Create a MediaConvert job
        response = mediaconvert.create_job(**job_params)
        print(response)

        # Convert datetime to a string representation
        response["Timestamp"] = datetime.utcnow().isoformat()
        return json.loads(json.dumps(response, default=str))
    except Exception as e:
        print(f"Error: {e}")
        raise e
        
    return {"statusCode": 400, "body": "Bad Request"}