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

    # Check if the event has "Records" key
    if "Records" in event and isinstance(event["Records"], list) and len(event["Records"]) > 0:
        record = event["Records"][0]

        # Check if the record has "s3" key
        if "s3" in record and "bucket" in record["s3"] and "name" in record["s3"]["bucket"] and "object" in record["s3"]:
        # Extract relevant information from the S3 event
            bucket = record["s3"]["bucket"]["name"]
            key = record["s3"]["object"]["key"]

            # Dynamically extract video file name from the key
            print(f"key-->{key}")
            video_file_name = key.split("/")[-1]
            print(f"video_file_name->{video_file_name}")
            file_name, extension = video_file_name.rsplit('.', 1)
            # Define job parameters for MediaConvert
            job_params = {
                "Queue": "arn:aws:mediaconvert:us-east-2:ACCOUND_ID:queues/Default",
                "UserMetadata": {
                "thumbnail": "true"
                },
                "Role": "arn:aws:iam::ACCOUND_ID:role/autoclipper-thumbnail-MediaConvertRole",
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
                                    "Destination": f"s3://autoclipper-output/thumbnails/"
                                }
                            },
                            "Outputs": [
                                {
                                    "VideoDescription": {
                                        "Width": 50,
                                        "ScalingBehavior": "DEFAULT",
                                        "Height": 50,
                                        "CodecSettings": {
                                            "Codec": "FRAME_CAPTURE",
                                            "FrameCaptureSettings": {
                                                "FramerateNumerator": 1,
                                                "FramerateDenominator": 1,
                                                "MaxCaptures": 1,
                                                "Quality": 80
                                            }
                                        }
                                    },
                                    "ContainerSettings": {
                                        "Container": "RAW"
                                    },
                                    "Extension": "jpg",
                                    "NameModifier": f"-thumbnail-{file_name}" # Use video file name without extension
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
                                "NameModifier": f"-fullvideo-{file_name}" # Use video file name without extension
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
        else:
            print("Invalid 's3' key structure in the event")
    else:
        print("Invalid event structure")
        
    return {"statusCode": 400, "body": "Bad Request"}