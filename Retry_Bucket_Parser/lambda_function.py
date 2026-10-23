
import boto3
import csv
import json
import logging
from datetime import datetime
import re


def lambda_handler(event, context):
    # Create a resource for S3
    S3 = boto3.resource('s3')

    # Get the SQS message body
    message_body = event["Records"][0]["body"]

    # Decode the SNS envelope and extract its Message field
    try:
        notification = json.loads(message_body)
        message = notification.get("Message", message_body)
    except (json.JSONDecodeError, AttributeError):
        message = message_body

    # Extract bucket name and file name
    values = re.search(
        r"The bucket:\s*['\"]?([^,'\"\s]+)['\"]?\s*,\s*"
        r"The File:\s*['\"]?([^,'\"\s]+)",
        message,
        re.IGNORECASE
    )

    if not values:
        raise ValueError(
            f"Failed to extract bucket name and object key from message: {message}"
        )

    bucket_name, object_key = values.groups()

    print(f"Bucket: {bucket_name}")
    print(f"File: {object_key}")

    # Define the name of the S3 bucket where invalid files will be moved
    error_bucket_name = 'dct-billing-error-298436524774-us-east-1-an'

    # Define the name of the bucket where processed files will be put
    processed_bucket = 'dct-billing-processed-298436524774-us-east-1-an'

    # Get the object from the bucket, convert bytes to a string,
    # and split the string into lines
    s3_obj = S3.Object(bucket_name, object_key)
    obj_data = s3_obj.get()['Body'].read().decode('utf-8').splitlines()

    # Set the error flag to false
    error_found = False

    # Define valid product lines and currencies
    valid_products = ['Dairy', 'Meat', 'Bakery']
    valid_currencies = ['USD', 'MXN', 'CAD']

    # Parse the CSV file and check for errors
    for row in csv.reader(obj_data[1:], delimiter=','):

        # Extract product line, date, currency, and bill amount
        product_line = row[4]
        date = row[6]
        currency = row[7]
        Bill_Amount = float(row[8])

        # Check whether the date format is valid
        try:
            datetime.strptime(date, '%y-%m-%d')
        except ValueError:
            print(f"Date Parameter for row {row[0]}: Incorrect date format {date}.")
            error_found = True
            break

        # Check whether the product line is valid
        if product_line not in valid_products:
            error_found = True
            print(
                f"Product line is invalid in row {row[0]}: "
                f"not supported product: {product_line}"
            )
            break

        # Check whether the currency is valid
        if currency not in valid_currencies:
            error_found = True
            print(
                f"Currency is invalid in row {row[0]}: "
                f"not supported currency: {currency}"
            )

        # Check whether the bill amount is negative
        if Bill_Amount < 0:
            error_found = True
            print(
                f"Bill Amount is invalid in row {row[0]}: "
                f"not supported Bill Amount: {Bill_Amount}"
            )

    # If an error is found, copy the file to the error bucket
    # and delete it from the original bucket
    if error_found:
        copy_source = {
            'Bucket': bucket_name,
            'Key': object_key
        }

        try:
            S3.meta.client.copy(
                copy_source, error_bucket_name, object_key
            )
            print(
                f"The object {object_key} has errors and was transferred "
                f"to {error_bucket_name}"
            )

            S3.Object(bucket_name, object_key).delete()
            print(
                f"The object {object_key} in bucket {bucket_name} is being deleted"
            )

        except Exception as e:
            print(f"Action failed because of {str(e)}")

    # If there are no errors, move the file to the processed bucket
    else:
        copy_source = {
            'Bucket': bucket_name,
            'Key': object_key
        }

        try:
            S3.meta.client.copy(
                copy_source, processed_bucket, object_key
            )
            print(
                f"The object {object_key} is transferred to {processed_bucket}"
            )

            S3.Object(bucket_name, object_key).delete()
            print(
                f"The object {object_key} in bucket {bucket_name} is being deleted"
            )

        except Exception as e:
            print(f"Action failed because of {str(e)}")