# AWS setup and verification

## 1. Install and authenticate

Install AWS CLI v2 from the official AWS installer, then use one of these secure methods:

```powershell
aws configure sso
# or
aws configure --profile smartenergy
```

The project never stores access keys in source files. Do not put keys in `.env`, Git, or chat messages.

## 2. Select a bucket

Use an existing S3 bucket in the selected region or create one in the AWS console. S3 bucket names are globally unique. Set the bucket and region in a local `.env` file based on `.env.example`:

```text
AWS_REGION=ap-south-1
S3_BUCKET=your-unique-bucket-name
S3_PREFIX=smart-energy-analytics
```

## 3. Verify the real round trip

From the repository root:

```powershell
py scripts\cloud_check.py --bucket your-unique-bucket-name
```

This verifies the AWS caller identity, bucket access, upload of the demo raw file, and object visibility. It does not claim Spark ran in AWS.

## 4. Run the project workflow

```powershell
py scripts\sync_s3.py upload --bucket your-unique-bucket-name
py scripts\run_pipeline.py
```

The current pipeline performs local processing. A cloud Spark run requires a configured AWS-compatible Spark environment such as EMR or Glue, with its cost and IAM permissions documented separately.

