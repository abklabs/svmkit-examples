# Runner Configuration

Under the hood, `svmkit` uses `apt` and `dpkg` to install and manage software on the remote hosts it interacts with. In order to support development and custom use cases, `svmkit` provides a means to override its software installation behavior using `runnerConfig`.  This datastructure can be passed into any component in `svmkit` that installs software on the remote host.

## `aptLockTimeout`

On the target hosts, only one `apt` or `dpkg` instance may run at a time.  This causes a problem if multiple components are being installed in parallel.  To work around this, `svmkit` maintains a lock which is shared amongst all of its `apt` invocations.  This timeout (in seconds) can be configured as necessary, if the defaults aren't enough.

## `packageConfig`

`packageConfig` allows you to do things like:

- Override versions and/or releases for a given package installed by the component.
- Install a package from a local file instead of using the `svmkit` `apt` repositories.
- Install additional packages not normally included with a component.

NOTE: Only packages which were already being installed by a component, or new packages added to the `additional` list, may be overridden.  This is done to avoid typos in package overrides being silently ignored.

# Example of `runnerConfig`

```typescript
new svmkit.validator.Agave("avalidator", {
  runnerConfig: {
    aptLockTimeout: 200,
    packageConfig: {
      additional: ["anewpackage", "jq"],
      override: [
        {
          name: "svmkit-agave-validator",
          path: "./build/svmkit-agave-validator.deb",
        },
        {
          name: "anewpackage",
          path: "./build/my-new-package.deb",
        },
        {
          name: "jq",
          version: "1.6-2.1",
        },
      ],
    },
  },
});
```
