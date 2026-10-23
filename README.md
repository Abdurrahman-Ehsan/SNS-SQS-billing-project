# AWS SNS/SQS Billing Processing Project

## Overview

This project demonstrates an AWS-based billing processing workflow using AWS Lambda, Amazon S3, Amazon SNS, and Amazon SQS.

## Components

### 1. Billing Bucket Parser
- Contains the billing-processing Lambda function.
- Includes an `event.json` test event and a `template.yaml` deployment template.

### 2. Retry Bucket Parser
- Contains the retry-processing Lambda function.
- Includes an `event.json` test event and a `template.yaml` deployment template.

### 3. SNS and SQS Hands-On Lab
- Contains sample billing CSV files for bakery, dairy, and meat data.

## AWS Services

- **Amazon S3:** Stores billing files.
- **AWS Lambda:** Executes billing-processing and retry logic.
- **Amazon SNS:** Publishes notifications.
- **Amazon SQS:** Supports message queuing and retry processing.

## Repository Structure

```text
SNS,SQS/
├── Billing_Bucket_Parser/
│   ├── event.json
│   ├── lambda_function.py
│   └── template.yaml
├── Retry_Bucket_Parser/
│   ├── event.json
│   ├── lambda_function.py
│   └── template.yaml
├── SNS_and_SQS_HOL/
│   └── SNS_and_SQS_HOL/
│       └── s3_files/
│           ├── billing_data_bakery_may_2023.csv
│           ├── billing_data_dairy_may_2023.csv
│           └── billing_data_meat_may_2023.csv
└── README.md