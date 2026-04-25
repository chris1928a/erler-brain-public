"""System status handler."""
import os


async def handle_status() -> str:
    import boto3
    bucket = os.environ.get("BRAIN_BUCKET", "")

    # Check S3
    try:
        s3 = boto3.client("s3", region_name="eu-central-1")
        s3.list_objects_v2(Bucket=bucket, MaxKeys=1)
        s3_status = "✅ Online"
    except Exception:
        s3_status = "❌ Offline"

    # Check DynamoDB
    try:
        ddb = boto3.resource("dynamodb", region_name="eu-central-1")
        table = ddb.Table(os.environ.get("SESSION_TABLE", "erler-brain-sessions"))
        table.table_status
        ddb_status = "✅ Online"
    except Exception:
        ddb_status = "❌ Offline"

    return f"""🧠 *Erler Brain v3 Status*

*Services:*
• S3 Brain Bucket: {s3_status}
• DynamoDB Sessions: {ddb_status}
• Telegram: ✅ Running
• Gemini API: {'✅' if os.environ.get('GEMINI_API_KEY') else '❌'}
• Claude API: {'✅' if os.environ.get('ANTHROPIC_API_KEY') else '❌'}
• Evolution API: {'✅' if os.environ.get('EVOLUTION_API_URL') else '⚠️ Not configured'}

*Config:*
• Brain Bucket: {bucket}
• Region: eu-central-1"""
