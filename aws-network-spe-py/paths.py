import pulumi

from typing import cast, Dict, Any

import pulumi_svmkit as svmkit

base_paths = svmkit.paths.get_default_paths_output().apply(lambda p: cast(svmkit.paths.PathsDict, {
    "accountsPath": p.accounts_path,
    "ledgerPath": p.ledger_path,
    "logPath": p.log_path,
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
    "genesisPrimordialAccountsPath": p.genesis_primordial_accounts_path,
    "genesisSolanaSplCachePath": p.genesis_solana_spl_cache_path,
    "genesisValidatorAccountsPath": p.genesis_validator_accounts_path,
}))

faucet_paths = svmkit.paths.get_default_faucet_paths_output(base_paths=base_paths).apply(lambda p: cast(svmkit.faucet.FaucetPathsArgsDict, {
    "accountsPath": p.accounts_path,
    "ledgerPath": p.ledger_path,
    "logPath": p.log_path,
    "systemdPath": p.systemd_path,
    "validatorIdentityKeypairPath": p.validator_identity_keypair_path,
    "validatorVoteAccountKeypairPath": p.validator_vote_account_keypair_path,
    "faucetKeypairPath": p.faucet_keypair_path,
    "faucetRunBinPath": p.faucet_run_bin_path,
}))

explorer_paths = svmkit.paths.get_default_explorer_paths_output(base_paths=base_paths).apply(lambda p: cast(svmkit.explorer.ExplorerPathsArgsDict, {
    "accountsPath": p.accounts_path,
    "ledgerPath": p.ledger_path,
    "logPath": p.log_path,
    "systemdPath": p.systemd_path,
    "validatorIdentityKeypairPath": p.validator_identity_keypair_path,
    "validatorVoteAccountKeypairPath": p.validator_vote_account_keypair_path,
    "explorerInstallPath": p.explorer_install_path,
    "explorerRunBinPath": p.explorer_run_bin_path,
}))

watchtower_paths = svmkit.paths.get_default_watchtower_paths_output(base_paths=base_paths).apply(lambda p: cast(svmkit.watchtower.WatchtowerPathsArgsDict, {
    "accountsPath": p.accounts_path,
    "ledgerPath": p.ledger_path,
    "logPath": p.log_path,
    "systemdPath": p.systemd_path,
    "validatorIdentityKeypairPath": p.validator_identity_keypair_path,
    "validatorVoteAccountKeypairPath": p.validator_vote_account_keypair_path,
    "watchtowerRunBinPath": p.watchtower_run_bin_path,
}))

tuner_paths = svmkit.paths.get_default_tuner_paths_output(base_paths=base_paths).apply(lambda p: cast(svmkit.tuner.TunerPathsArgsDict, {
    "accountsPath": p.accounts_path,
    "ledgerPath": p.ledger_path,
    "logPath": p.log_path,
    "systemdPath": p.systemd_path,
    "validatorIdentityKeypairPath": p.validator_identity_keypair_path,
    "validatorVoteAccountKeypairPath": p.validator_vote_account_keypair_path,
    "tunerLogPath": p.tuner_log_path,
    "tunerConfPath": p.tuner_conf_path,
    "tunerRunBinPath": p.tuner_run_bin_path,
}))

agave_paths = svmkit.paths.get_default_agave_paths_output(base_paths=base_paths).apply(lambda p: cast(svmkit.agave.AgavePathsArgsDict, {
    "accountsPath": p.accounts_path,
    "ledgerPath": p.ledger_path,
    "logPath": p.log_path,
    "systemdPath": p.systemd_path,
    "validatorIdentityKeypairPath": p.validator_identity_keypair_path,
    "validatorVoteAccountKeypairPath": p.validator_vote_account_keypair_path,
    "agaveRunBinPath": p.agave_run_bin_path,
    "agaveStopBinPath": p.agave_stop_bin_path,
    "agaveCheckBinPath": p.agave_check_bin_path,
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
