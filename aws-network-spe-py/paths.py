import pulumi

from typing import cast, Dict, Any

import pulumi_svmkit as svmkit

base_paths = svmkit.paths.get_default_paths_output().apply(lambda p: cast(svmkit.paths.PathsDict, {
    "accountsPath": p.accounts_path,
    "ledgerPath": p.ledger_path,
    "logPath": None, # let systemd journal handle logging
    "systemdPath": p.systemd_path,
    "validatorIdentityKeypairPath": p.validator_identity_keypair_path,
    "validatorVoteAccountKeypairPath": p.validator_vote_account_keypair_path,
}))

genesis_paths = svmkit.paths.get_default_genesis_paths_output(base_paths=base_paths).apply(lambda p: cast(svmkit.genesis.GenesisPathsArgsDict, {
    "accountsPath": p.accounts_path,
    "ledgerPath": p.ledger_path,
    "logPath": p.log_path,
    "systemdPath": p.systemd_path,
    "validatorIdentityKeypairPath": p.validator_identity_keypair_path,
    "validatorVoteAccountKeypairPath": p.validator_vote_account_keypair_path,
    "primordialAccountsPath": p.primordial_accounts_path,
    "solanaSplCachePath": p.solana_spl_cache_path,
    "validatorAccountsPath": p.validator_accounts_path,
}))

faucet_paths = svmkit.paths.get_default_faucet_paths_output(base_paths=base_paths).apply(lambda p: cast(svmkit.faucet.FaucetPathsArgsDict, {
    "accountsPath": p.accounts_path,
    "ledgerPath": p.ledger_path,
    "logPath": p.log_path,
    "systemdPath": p.systemd_path,
    "validatorIdentityKeypairPath": p.validator_identity_keypair_path,
    "validatorVoteAccountKeypairPath": p.validator_vote_account_keypair_path,
    "keypairPath": p.keypair_path,
    "runBinPath": p.run_bin_path,
}))

explorer_paths = svmkit.paths.get_default_explorer_paths_output(base_paths=base_paths).apply(lambda p: cast(svmkit.explorer.ExplorerPathsArgsDict, {
    "accountsPath": p.accounts_path,
    "ledgerPath": p.ledger_path,
    "logPath": p.log_path,
    "systemdPath": p.systemd_path,
    "validatorIdentityKeypairPath": p.validator_identity_keypair_path,
    "validatorVoteAccountKeypairPath": p.validator_vote_account_keypair_path,
    "installPath": p.install_path,
    "runBinPath": p.run_bin_path,
}))

watchtower_paths = svmkit.paths.get_default_watchtower_paths_output(base_paths=base_paths).apply(lambda p: cast(svmkit.watchtower.WatchtowerPathsArgsDict, {
    "accountsPath": p.accounts_path,
    "ledgerPath": p.ledger_path,
    "logPath": p.log_path,
    "systemdPath": p.systemd_path,
    "validatorIdentityKeypairPath": p.validator_identity_keypair_path,
    "validatorVoteAccountKeypairPath": p.validator_vote_account_keypair_path,
    "runBinPath": p.run_bin_path,
}))

tuner_paths = svmkit.paths.get_default_tuner_paths_output(base_paths=base_paths).apply(lambda p: cast(svmkit.tuner.TunerPathsArgsDict, {
    "accountsPath": p.accounts_path,
    "ledgerPath": p.ledger_path,
    "logPath": p.log_path,
    "systemdPath": p.systemd_path,
    "validatorIdentityKeypairPath": p.validator_identity_keypair_path,
    "validatorVoteAccountKeypairPath": p.validator_vote_account_keypair_path,
    "tunerLogPath": p.tuner_log_path,
    "sysctlConfPath": p.sysctl_conf_path,
    "runBinPath": p.run_bin_path,
}))

agave_paths = svmkit.paths.get_default_agave_paths_output(base_paths=base_paths).apply(lambda p: cast(svmkit.agave.AgavePathsArgsDict, {
    "accountsPath": p.accounts_path,
    "ledgerPath": p.ledger_path,
    "logPath": p.log_path,
    "systemdPath": p.systemd_path,
    "validatorIdentityKeypairPath": p.validator_identity_keypair_path,
    "validatorVoteAccountKeypairPath": p.validator_vote_account_keypair_path,
    "runBinPath": p.run_bin_path,
    "stopBinPath": p.stop_bin_path,
    "checkBinPath": p.check_bin_path,
}))

paths = {
    "base": base_paths,
    "genesis": genesis_paths,
    "faucet": faucet_paths,
    "explorer": explorer_paths,
    "watchtower": watchtower_paths,
    "tuner": tuner_paths,
    "agave": agave_paths,
}

pulumi.export("paths", paths)
