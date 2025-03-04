import * as svmkit from "@svmkit/pulumi-svmkit";

export const basePaths = svmkit.paths.getDefaultPathsOutput().apply((p): svmkit.types.input.paths.PathsArgs => ({
    accountsPath: p.accountsPath,
    ledgerPath: p.ledgerPath,
    logPath: undefined, // let systemd handle logging
    systemdPath: p.systemdPath,
    validatorIdentityKeypairPath: p.validatorIdentityKeypairPath,
    validatorVoteAccountKeypairPath: p.validatorVoteAccountKeypairPath,
}));

export const tunerPaths = svmkit.paths.getDefaultTunerPathsOutput({basePaths}).apply((p): svmkit.types.input.tuner.TunerPathsArgs => ({
    accountsPath: p.accountsPath,
    ledgerPath: p.ledgerPath,
    logPath: p.logPath,
    systemdPath: p.systemdPath,
    validatorIdentityKeypairPath: p.validatorIdentityKeypairPath,
    validatorVoteAccountKeypairPath: p.validatorVoteAccountKeypairPath,
    tunerLogPath: p.tunerLogPath,
    sysctlConfPath: p.sysctlConfPath,
    runBinPath: p.runBinPath,
}));


export const firedancerPaths = svmkit.paths.getDefaultFiredancerPathsOutput({basePaths}).apply((p): svmkit.types.input.firedancer.FiredancerPathsArgs => ({
    accountsPath: p.accountsPath,
    ledgerPath: p.ledgerPath,
    logPath: p.logPath,
    systemdPath: p.systemdPath,
    validatorIdentityKeypairPath: p.validatorIdentityKeypairPath,
    validatorVoteAccountKeypairPath: p.validatorVoteAccountKeypairPath,
    configPath: p.configPath,
}));
