import boto3
import csv
import logging
from datetime import datetime


def ThirdPartyAPIEceptionSimulation(Valid_products, bucket_name , object_key):
    try:
        raise Exception('APIFailure: Intl API is currently UnAvailable')
    except Exception as error:
        SNS = boto3.client('sns')
        sns_topic_arn = 'arn:aws:sns:us-east-1:298436524774:Taxes'
        message = f'The API Call to the third party Application for Billing has failed. Error:{error}. The bucket: {bucket_name} , The File: {object_key}'
        SNS.publish(
            TopicArn = sns_topic_arn ,
            Message = message ,
            Subject = "API Call Failure Notification"
            
        )
        print("Error while move file to s3")
        raise error

#create a lambda function which will check the csv file uploaded on a bucket and parse the data from the csv file and check whether the file contet is valid or not and if the file content is invalid then object will be moved to the error bucket and it will be removed from orginal bucket.
def lambda_handler(event, context) :
    #Create a resource for S3
    S3=boto3.resource('s3')

    #Get the bucket name and object key from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    #Define the name of the s3 bucket where the invalid files will be moved
    error_bucket_name = 'dct-billing-error-298436524774-us-east-1-an'


    #Define the name of the bucket where the processed files will be put
    processed_bucket= 'dct-billing-processed-298436524774-us-east-1-an'
    

    #Get the object from the bucket, convert the bytes to string and split the string into lines.
    s3_obj = S3.Object(bucket_name,object_key)
    obj_data = s3_obj.get()['Body'].read().decode('utf-8').splitlines()


    #set the error flag to false, we will turn it to true when we will find an error
    error_found = False


    #define valid product lines and valid currencies
    valid_products = ['Dairy', 'Meat', 'Bakery']
    valid_currencies = ['USD','MXN','CAD']


    #Function to simulate an API unavailabe error
    ThirdPartyAPIEceptionSimulation(valid_products, bucket_name , object_key)


    #parse the csv file and check for errors
    for row in csv.reader(obj_data[1:],delimiter=','):

    #for each line extract the product line, date, currency & bill amount
        product_line = row[4]
        date = row[6]
        currency = row[7]
        Bill_Amount = float(row[8])

    #check whether the date value is valid as per the allowed format
    
        try: 
            datetime.strptime(date,'%y-%m-%d')
        except ValueError:
            print(f"Date Parameter for row{row[0]}: Incorrect date format {date}.")
            error_found = True
            break

    #check whether the product line is from within the allowed items
        if product_line not in valid_products:
            error_found = True
            print(f'Product line is invalid in row {row[0]} : not supported product: {product_line} ')
            break
    #check whether the currency is from within the allowed currencies list
        if currency not in valid_currencies:
            error_found = True
            print(f'Currency is invalid in row {row[0]} : not supported currency: {currency}')

    #check whether the the Bill amount is negative and if yes then turn error_found to true and print the message
        if Bill_Amount < 0:
            error_found = True
            print(f'Bill Amount is invalid in row {row[0]} : not supported Bill Amount: {Bill_Amount}')

#If the error is found in the csv file then. copy the file to error bucket and delete it from the current bucket
    if error_found:
        copy_source = {
            'Bucket': bucket_name ,
            'Key': object_key
            }
        try:
            S3.meta.client.copy(copy_source,error_bucket_name,object_key)
            print(f"The object:{object_key} has error and that why it is transmitted to ")
            S3.Object(bucket_name , object_key).delete()
            print(f"The object:{object_key} in the bucket{bucket_name} is being deleted")
        except Exception as e:
            print(f"action failed because of {str(e)}")

#If there is no error put the file in the processed files bucket
    else:
        copy_source = {
                    'Bucket': bucket_name ,
                    'Key': object_key
                    }
        try:
                    S3.meta.client.copy(copy_source,processed_bucket,object_key)
                    print(f"The object:{object_key} is transmitted to {processed_bucket}")
                    S3.Object(bucket_name , object_key).delete()
                    print(f"The object:{object_key} in the bucket{bucket_name} is being deleted")
        except Exception as e:
                    print(f"action failed because of {str(e)}")   
