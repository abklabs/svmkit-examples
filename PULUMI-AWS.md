# PULUMI setup with AWS

Pulumi is an Infrastructure as Code (IaC) platform that allows you to define, deploy, and manage cloud infrastructure using familiar programming languages. This guide will walk you through using Pulumi in AWS CloudShell with a Amazon Simple Storage Service (S3) backend, to store state files on cloud.

## Setup

1. Open and configure [AWS CloudShell](https://aws.amazon.com/cloudshell/) to follow the deployment process:

- On the navigation bar, [choose the CloudShell icon](https://docs.aws.amazon.com/cloudshell/latest/userguide/getting-started.html#launch-region-shell).

- Add a new user with larger storage quota to perform smooth installation:

```bash
sudo useradd -m -G cloudshell-user bcuser
```
- Configure sudo for the new user:

```bash
sudo visudo -f /etc/sudoers.d/bcuser
```
- Add the following text to allow sudo without password for the new user:

```bash
bcuser ALL=(ALL) NOPASSWD: ALL
```
- Hit `Ctrl+x`, `y`, and `Enter`

2. Install `pulumi` in your AWS CloudShell environment ([Official docs to install Pulumi on AWS](https://www.pulumi.com/docs/iac/get-started/aws/)]

```bash
sudo su bcuser
cd
curl -fsSL https://get.pulumi.com | sh
source ~/.bashrc 
pulumi version
```

- You should see something like this:
```
v3.140.0
```

3. Create a new S3 bucket to store your Pulumi configuration:

```bash
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws s3 mb s3://pulumi-config-$AWS_ACCOUNT_ID-$AWS_REGION
```

4. Configure your pulumi to use the new S3 bucket:

```bash
pulumi login s3://pulumi-config-$AWS_ACCOUNT_ID-$AWS_REGION
```

5. Set the passphrase into an new environment variable for this session:

```bash
export PULUMI_CONFIG_PASSPHRASE=<your_passphrase>
```

6. (Optional) Install Solana CLI if you'd like to run `token-demo` script

- Set the Solana version

```bash
export SOLANA_VERSION=1.18.26
```

- Download binaries and set up the PATH variable
```bash
sudo yum install -y bzip2
cd
curl -sSfL https://github.com/solana-labs/solana/releases/download/v$SOLANA_VERSION/solana-release-x86_64-unknown-linux-gnu.tar.bz2 -o solana.tar.bz2
tar --bzip2 -xf solana.tar.bz2
cd solana-release/
export PATH=$PWD/bin:$PATH
solana --version
```

- You should see something like this:

```bash
solana-cli 1.18.26 (src:d9f20e95; feat:3241752014, client:SolanaLabs)
```

7. Clone this repository and change directory to the AWS blueprint:

```bash
cd
git clone https://github.com/abklabs/svmkit-examples.git
cd svmkit-examples/aws-network-spe-py/
```

8. Continue from **Step 1** in [Solana Permissioned Environment Inside an AWS VPC](aws-network-spe-py/README.md)

## Tear down

1. Delete all created AWS resources

```bash
pulumi down
```

- Select `yes`

2. Clear and delete the S3 bucket used for Pulumi configuration

```bash
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws s3 rm s3://pulumi-config-$AWS_ACCOUNT_ID-$AWS_REGION --recursive
aws s3 rb s3://pulumi-config-$AWS_ACCOUNT_ID-$AWS_REGION
```

3. To delete the currently open AWS CloudShell environment, in top-right corner choose **Actions** > **Delete**
