# Pulumi

Pulumi is an Infrastructure as Code (IaC) platform that allows you to define, deploy, and manage cloud infrastructure using familiar programming languages. This guide will walk you through using Pulumi with a local backend, which stores state files on your local filesystem.

## Setup

Before using Pulumi, ensure you have:

• The Pulumi CLI installed on your system. Follow the installation instructions at [Pulumi Installation](https://www.pulumi.com/docs/iac/download-install/).

## Workflow

1. Log In to Pulumi

To store state locally, use the --local option when logging in to Pulumi. Run the following command in your terminal:

```bash
pulumi login --local
Enter your passphrase to protect config/secrets:
Re-enter your passphrase to confirm:
Created stack 'workstation'
```

This command sets up Pulumi to save your stack's state files on your local filesystem, usually in the ~/.pulumi directory. This is useful if you choose not to use the Pulumi Service. You will be asked to enter a passphrase to encrypt secrets. This passphrase will be required whenever Pulumi needs to access the stack's state. To avoid being prompted for the passphrase you can set it in advance with:

```bash
export PULUMI_CONFIG_PASSPHRASE="<passphrase>"
```

2. Create a Stack

In Pulumi, a stack represents a unique instance of your infrastructure configuration, such as dev, staging, or production. To create a new stack with local state, run:

```bash
pulumi stack init <stack-name>
```

Replace <stack-name> with a name that identifies the environment, such as dev or production. This command initializes a new stack and stores the state file locally.

You can list all stacks for the current project with:

```bash
pulumi stack ls
```

3. Configure a stack

Once your stack is created, configure environment-specific settings. Pulumi uses configuration settings to manage details for each stack, such as region and credentials.

a. Set your AWS region (replace <region> with the desired AWS region, such as us-west-2):

```bash
pulumi config set aws:region <region>
```

b. To view all configuration settings for the current stack:

```bash
pulumi config
```

For more details on configuring Pulumi for AWS, refer to the [Pulumi AWS Provider Configuration](https://github.com/pulumi/pulumi-aws?tab=readme-ov-file#configuration).

4. Preview and Deploy

Once your code and configuration are set up, you can preview and deploy your changes.

a. Preview the changes Pulumi will make to your cloud infrastructure:

```bash
pulumi preview
```

This command shows the proposed changes without actually applying them.

b. Deploy the changes to your infrastructure:

```bash
pulumi up
```

Pulumi will apply the changes and output the results, including resource creation, updates, or deletions.

5. Destroy a stack

To destroy your stack and clean up resources:

```bash
pulumi destroy
```

## FAQ

1. Can I choose where to store my Pulumi state?
   Absolutely. Pulumi allows you to store state in various blob storage providers. For details on available backends and configuration options, see the [State Backends documentation](https://www.pulumi.com/docs/iac/concepts/state-and-backends/).

2. Can I use a custom provider for managing secrets?
   Yes, Pulumi supports several popular secret management providers. For more information on available options, refer to the [Secrets Provider documentation](https://www.pulumi.com/docs/iac/cli/commands/pulumi_stack_change-secrets-provider/).
