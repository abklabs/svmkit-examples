# Running Solana Bench TPS on SVMKit Network

This guide demonstrates how to install and run `solana-bench-tps` on a SVMKit network for benchmarking transaction processing capabilities. Benchmarking is essential for validators and cluster operators to evaluate their cluster's performance.

## Overview

This guide covers:
1. Setting up the required environment
2. Building the Solana benchmarking tool
3. Running benchmark tests with various configurations
4. Interpreting benchmark results

## Step-by-Step Implementation

### Step 1: Set Up Environment

First, ensure you have a properly configured environment:

```bash
# Update system packages
sudo apt-get update
sudo apt-get install -y git libssl-dev libudev-dev pkg-config zlib1g-dev llvm clang cmake make libprotobuf-dev protobuf-compiler libclang-dev
```

### Step 2: Install Rust and Clone the Repository

Install Rust and clone the Agave repository:

```bash
# Install Rust
curl https://sh.rustup.rs -sSf | sh
source $HOME/.cargo/env

# Verify installation
rustup --version

# Install nightly and components
rustup install nightly
rustup component add rustfmt

# Clone Agave repository
git clone https://github.com/anza-xyz/agave.git
cd agave
```

### Step 3: Build the Benchmark Tool

Build the benchmark tool:

```bash
# Build solana-bench-tps in release mode
cargo build --release --bin solana-bench-tps

# Verify the binary was created
ls -la target/release/solana-bench-tps
```

### Step 4: Prepare Validator Key

Ensure you have a validator keypair to use for the benchmark. If using an existing SVMKit validator, locate your validator keypair file (usually `validator-keypair.json`).

### Step 5: Run Basic Benchmark

Run a basic benchmark against your local SVMKit node:

```bash
~/agave/target/release/solana-bench-tps \
  --authority /home/sol/validator-keypair.json \
  -u http://localhost:8899 \
  --duration 30 \
  --tx-count 10 \
  --threads 2
```

Parameters explained:
- `--authority`: Path to validator keypair that will sign transactions
- `-u`: URL of the SVMKit network RPC endpoint
- `--duration`: Length of the test in seconds
- `--tx-count`: Total number of transactions to generate
- `--threads`: Number of threads to use for sending transactions

### Step 6: Advanced Benchmark with RPC Client

For more accurate results that better simulate real-world conditions, use the RPC client mode:

```bash
~/agave/target/release/solana-bench-tps \
  --authority /home/sol/validator-keypair.json \
  -u http://localhost:8899 \
  --duration 30 \
  --tx-count 1000 \
  --threads 2 \
  --use-rpc-client
```

The `--use-rpc-client` flag ensures transactions are sent through the node's RPC interface, which better represents typical client behavior.

## Benchmark Configuration Options

Customize your benchmarks with these additional options:

### Performance Tuning

```bash
~/agave/target/release/solana-bench-tps \
  --authority /home/sol/validator-keypair.json \
  -u http://localhost:8899 \
  --duration 60 \
  --tx-count 5000 \
  --threads 4 \
  --sustained
```

The `--sustained` flag maintains a constant rate of transactions rather than sending them all at once.

### Network Configuration Testing

For testing different network configurations:

```bash
~/agave/target/release/solana-bench-tps \
  --authority /home/sol/validator-keypair.json \
  -u http://localhost:8899 \
  --duration 120 \
  --tx-count 10000 \
  --threads 8 \
  --compute-unit-price 100 \
  --lamports-per-signature 5000
```

## Interpreting Results

After running a benchmark, you'll see output similar to:

```
Confirmed 975 transactions | Finalized 952 transactions
Average TPS: 32.5 over 30 seconds
Maximum TPS: 45.2
Minimum TPS: 21.8
Average confirmation time: 1.35s
Maximum confirmation time: 2.89s
Minimum confirmation time: 0.65s
Average finalization time: 4.21s
```

Key metrics to evaluate:
- **Average TPS**: Transactions processed per second (higher is better)
- **Confirmation time**: Time until transactions are confirmed (lower is better)
- **Finalization time**: Time until transactions are finalized (lower is better)

## Troubleshooting

Common issues and solutions:

1. **RPC connection errors**:
   - Verify the correct RPC endpoint URL
   - Check network connectivity
   - Ensure the node is running and synchronized

2. **Transaction failures**:
   - Ensure the authority keypair has sufficient balance
   - Reduce transaction count or rate if node is overwhelmed
   - Check node logs for error messages

3. **Low TPS results**:
   - Try increasing threads
   - Verify hardware specifications meet requirements
   - Check for network congestion or resource contention

## Conclusion

By following this guide, you've learned how to install and run `solana-bench-tps` to benchmark your SVMKit network. These benchmarks provide valuable insights into your network's performance and can help identify optimization opportunities.

For more comprehensive testing, consider running multiple benchmarks with different parameters and comparing the results. Regularly benchmarking your network ensures optimal performance for validators and users.