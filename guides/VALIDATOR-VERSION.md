# Identify and Update Validator Version

This guide walks you through determining your validator’s current version and updating it to the latest release.

> **Note:** This guide is tailored for the Agave validator. System service names may vary depending on the specific flavor and variant.

1. Check the Installed Validator Version

To check the currently installed version of the validator, run:

```
sudo apt info svmkit-agave-validator
```

Example output:

```
Package: svmkit-agave-validator
Version: 1.18.26-1
Priority: optional
Maintainer: Engineering <engineering@abklabs.com>
Installed-Size: 120 MB
Provides: svmkit-validator
Depends: libc6 (>= 2.34), libstdc++6 (>= 12)
Conflicts: svmkit-validator
Replaces: svmkit-validator
Homepage: https://anza.xyz/
Vcs-Browser: https://github.com/anza-xyz/agave
Vcs-Git: https://github.com/anza-xyz/agave
Download-Size: 32.6 MB
APT-Sources: https://apt.abklabs.com/svmkit dev/main amd64 Packages
Description: Blockchain, Rebuilt for Scale
```

The Version field shows the currently installed version (e.g., 1.18.26-1).

2. Check for Available Updates

To determine the latest available version:

sudo apt list svmkit-agave-validator

Example output:

Listing... Done
svmkit-agave-validator/dev 2.2.0-1 amd64 [upgradable from: 1.18.26-1]
N: There are 24 additional versions. Please use the '-a' switch to see them.

If an upgrade is available, it will be indicated as [upgradable from: <current version>].

To see all available versions:

```
sudo apt list -a svmkit-agave-validator
```

3. Update the Validator

If an update is available, upgrade to the latest version.

Option 1: Directly Update via APT

sudo apt update && sudo apt install svmkit-agave-validator

This will download and install the latest version from the repository.

Option 2 (recommended): Update via Pulumi

If you manage your validator using Pulumi, update the version in the configuration and apply the changes.

Modify the validator component to specify the new version:

```typescrpt
new svmkit.validator.Agave("validator", {
    connection,
    version: "2.2.0-1",
    environment: {},
    keyPairs: {
        identity: validatorKey.json,
        voteAccount: voteAccountKey.json,
    },
    flags: {},
}, {
    dependsOn: [instance],
});
```

Apply the changes:

```
pulumi up
```

This will install the updated validator version and restart the validator automatically.

4. Verify the Update

After updating, confirm that the validator is running the new version:

```
sudo apt info svmkit-agave-validator
```

Ensure the Version field matches the expected update.

Additionally, check the validator process:

```
systemctl status svmkit-agave-validator
```

If the validator is not running, restart it:

```
sudo systemctl restart svmkit-agave-validator
```

5. Confirm Validator Participation

After updating, ensure your validator is actively participating in the network: 1. Check voting status:

Check synchronization:

```
solana catchup --our-localhost
```
