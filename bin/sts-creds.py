#!/usr/bin/env python
# Script to get role session for pipeline-deployment from env variables in Gitlab CI/CD
# It is to be called before sam-cli using: eval `sts-deploy-creds.py <env>` where env = prod or sandbox

import os
import sys
import boto3

if not os.getenv("AWS_REGION"):
    AWS_REGION = "eu-west-1"
else:
    AWS_REGION = os.getenv("AWS_REGION")

PIPELINE_EXEC_ROLE = {
    "prod": "arn:aws:iam::798139289016:role/pipeline-deployment",
    "sandbox": "arn:aws:iam::671446661642:role/pipeline-deployment",
}


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
        role = PIPELINE_EXEC_ROLE[aws_account]
        role_creds = sts.assume_role(
            RoleArn=role, RoleSessionName="pipeline-deployment"
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
