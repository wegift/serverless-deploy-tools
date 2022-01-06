# serverless-sts-creds

sts-creds.py is a wrapper script that provides AWS credentials as shell ENV variables. It us
to be used with serverless deployment tools (SAM CLI or CDK) within a CI/CD environment. 

## Dependencies

Python3 and boto3.

## Configuration

sts-creds.py expects the following IAM user API credentials to be available as ENV variables:

- ``AWS_ACCESS_KEY_ID_PROD``
- ``AWS_SECRET_ACCESS_KEY_PROD``
- ``AWS_ACCESS_KEY_ID_SANDBOX``
- ``AWS_SECRET_ACCESS_KEY_SANDBOX``

It's only hardcoded to prod or sandbox but could be easily modified to support more environments.

sts-creds.py also expects the following pipeline execution roles ARNs to be available as ENV variables:

- ``AWS_PIPELINE_EXEC_ROLE_PROD``
- ``AWS_PIPELINE_EXEC_ROLE_SANDBOX``

Example: ``PIPELINE_EXEC_ROLE_PROD=arn:aws:iam::111122223333:role/pipeline-deployment``

These roles need to be pre-configured with tools like Terraform (or Cloudformation). Example JSON, compatible
with both SAM and CDK:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": "arn:aws:iam::111122223333:role/pipeline-cloudformation-execution-role"
        },
        {
            "Sid": "",
            "Effect": "Allow",
            "Action": [
                "cloudformation:GetTemplateSummary",
                "cloudformation:GetTemplate",
                "cloudformation:ExecuteChangeSet",
                "cloudformation:DescribeStacks",
                "cloudformation:DescribeStackResource",
                "cloudformation:DescribeStackEvents",
                "cloudformation:DescribeChangeSet",
                "cloudformation:DeleteStack",
                "cloudformation:DeleteChangeSet",
                "cloudformation:CreateChangeSet"
            ],
            "Resource": "*"
        },
        {
            "Sid": "",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject*",
                "s3:List*",
                "s3:GetObject*",
                "s3:GetEncryptionConfiguration",
                "s3:GetBucket*",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::my-lambdas/*",
                "arn:aws:s3:::my-lambdas",
                "arn:aws:s3:::cdktoolkit-stagingbucket-something/*",
                "arn:aws:s3:::cdktoolkit-stagingbucket-something",
            ]
        }
    ]
}
```

We also need pass a role to Cloudformation to assume for execution as a service. Sample JSON for
pipeline-cloudformation-execution-role:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Action": "*",
            "Resource": "*"
        }
    ]
}
```

This role is passed to the Cloudformation service via SAM CLI or CDK (``--role-arn``).

## Usage

Before calling ``cdk|sam deploy``:

```shell
pip install git+https://github.com/wegift/serverless-sts-creds.git
eval sts-creds.py {env}
```
where {env} is either prod or sandbox.

and then...

```shell
sam deploy
      --parameter-overrides "ParameterKey=Environment,ParameterValue=$env"
      --role-arn $role
      --no-confirm-changeset

```

```shell
cdk deploy --require-approval never --role-arn $role
```