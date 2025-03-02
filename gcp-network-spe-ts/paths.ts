import * as svmkit from "@svmkit/pulumi-svmkit";

// Base paths
export const basePaths = svmkit.paths.getDefaultPathsOutput().apply(
  (p): svmkit.types.input.paths.PathsArgs => ({
    accountsPath: p.accountsPath,
    ledgerPath: p.ledgerPath,
    logPath: undefined, // let systemd handle logging
    systemdPath: p.systemdPath,
    validatorIdentityKeypairPath: p.validatorIdentityKeypairPath,
    validatorVoteAccountKeypairPath: p.validatorVoteAccountKeypairPath,
  })
);

// Genesis paths
export const genesisPaths = svmkit.paths.getDefaultGenesisPathsOutput({ basePaths }).apply(
  (p): svmkit.types.input.genesis.GenesisPathsArgs => ({
    accountsPath: p.accountsPath,
    ledgerPath: p.ledgerPath,
    logPath: p.logPath,
    systemdPath: p.systemdPath,
    validatorIdentityKeypairPath: p.validatorIdentityKeypairPath,
    validatorVoteAccountKeypairPath: p.validatorVoteAccountKeypairPath,
    primordialAccountsPath: p.primordialAccountsPath,
    solanaSplCachePath: p.solanaSplCachePath,
    validatorAccountsPath: p.validatorAccountsPath,
  })
);

// Faucet paths
export const faucetPaths = svmkit.paths.getDefaultFaucetPathsOutput({ basePaths }).apply(
  (p): svmkit.types.input.faucet.FaucetPathsArgs => ({
    accountsPath: p.accountsPath,
    ledgerPath: p.ledgerPath,
    logPath: p.logPath,
    systemdPath: p.systemdPath,
    validatorIdentityKeypairPath: p.validatorIdentityKeypairPath,
    validatorVoteAccountKeypairPath: p.validatorVoteAccountKeypairPath,
    keypairPath: p.keypairPath,
    runBinPath: p.runBinPath,
  })
);

// Tuner paths
export const tunerPaths = svmkit.paths.getDefaultTunerPathsOutput({ basePaths }).apply(
  (p): svmkit.types.input.tuner.TunerPathsArgs => ({
    accountsPath: p.accountsPath,
    ledgerPath: p.ledgerPath,
    logPath: p.logPath,
    systemdPath: p.systemdPath,
    validatorIdentityKeypairPath: p.validatorIdentityKeypairPath,
    validatorVoteAccountKeypairPath: p.validatorVoteAccountKeypairPath,
    tunerLogPath: p.tunerLogPath,
    sysctlConfPath: p.sysctlConfPath,
    runBinPath: p.runBinPath,
  })
);

// Agave paths
export const agavePaths = svmkit.paths.getDefaultAgavePathsOutput({ basePaths }).apply(
  (p): svmkit.types.input.agave.AgavePathsArgs => ({
    accountsPath: p.accountsPath,
    ledgerPath: p.ledgerPath,
    logPath: p.logPath,
    systemdPath: p.systemdPath,
    validatorIdentityKeypairPath: p.validatorIdentityKeypairPath,
    validatorVoteAccountKeypairPath: p.validatorVoteAccountKeypairPath,
    runBinPath: p.runBinPath,
    stopBinPath: p.stopBinPath,
    checkBinPath: p.checkBinPath,
  })
);
