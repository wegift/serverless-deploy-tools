#!/usr/bin/env python

import os
import sys
import boto3

if not os.getenv("AWS_REGION"):
    AWS_REGION = "eu-west-1"
else:
    AWS_REGION = os.getenv("AWS_REGION")

def get_pipeline_exec_role(aws_account):
    try:
        if "sandbox" in aws_account:
            return os.environ["AWS_PIPELINE_EXEC_ROLE_SANDBOX"]
        elif "prod" in aws_account:
            return os.environ["AWS_PIPELINE_EXEC_ROLE_PROD"]
        else:
            raise ValueError("Invalid AWS account")
    except KeyError as e:
        raise KeyError("Missing environment variable") from e

def set_iam_user_creds(aws_account):
    if "sandbox" in aws_account:
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID_SANDBOX")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY_SANDBOX")
        return [aws_account, aws_access_key_id, aws_secret_access_key]
    elif "prod" in aws_account:
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID_PROD")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY_PROD")
        return [aws_account, aws_access_key_id, aws_secret_access_key]
    else:
        print("echo Invalid AWS account.")
        exit(1)


def assume_role(iam_user_creds):
    aws_account, aws_access_key_id, aws_secret_access_key = iam_user_creds
    try:
        sts = boto3.client(
            "sts",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=AWS_REGION,
        )
        role_creds = sts.assume_role(
            RoleArn=get_pipeline_exec_role(aws_account), RoleSessionName="pipeline-deployment"
        )
    except Exception as e:
        print("echo '{}'".format(e))
        exit(1)
    print(
        "export AWS_ACCESS_KEY_ID={}".format(role_creds["Credentials"]["AccessKeyId"])
    )
    print(
        "export AWS_SECRET_ACCESS_KEY={}".format(
            role_creds["Credentials"]["SecretAccessKey"]
        )
    )
    print(
        "export AWS_SESSION_TOKEN={}".format(role_creds["Credentials"]["SessionToken"])
    )
    print("export AWS_REGION={}".format(AWS_REGION))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        aws_account = sys.argv[1]
        iam_user_creds = set_iam_user_creds(aws_account)
        assume_role(iam_user_creds)
    else:
        print("echo No AWS account")
        exit(1)
