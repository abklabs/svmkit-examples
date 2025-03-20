# Running Solana Bench TPS on SVMKit Network

This guide demonstrates how to install and run `solana-bench-tps` on a SVMKit network for benchmarking transaction processing capabilities. Benchmarking is essential for validators and cluster operators to evaluate their cluster's performance.

## Overview

This guide covers:
1. Setting up the required environment
2. Installing the Solana benchmarking tool from apt
3. Running benchmark tests with various configurations
4. Interpreting benchmark results

## Step-by-Step Implementation

### Step 1: Install SVMKit Bench TPS Package

First, add the SVMKit repository and install the bench-tps package:

```bash
# 1. Add the SVMKit repository
echo "deb [trusted=yes] https://apt.abklabs.com/svmkit dev main" | sudo tee /etc/apt/sources.list.d/svmkit.list

# 2. Update repositories
sudo apt update

# 3. Install the solana-bench-tps package
sudo apt install -y svmkit-solana-bench-tps
```

### Step 2: Run Basic Benchmark

Run a basic benchmark against your local SVMKit node:

```bash
solana-bench-tps \
  --client-node-id /home/sol/validator-keypair.json \
  -u http://localhost:8899 \
  --duration 30 \
  --tx-count 10 \
  --threads 2
```

Parameters explained:
- `--client-node-id`: Path to validator keypair that will sign transactions
- `-u` or `--url`: URL of the SVMKit network RPC endpoint
- `--duration`: Length of the test in seconds
- `--tx-count`: Total number of transactions to generate
- `--threads`: Number of threads to use for sending transactions

### Step 3: Advanced Benchmark with TPU Client

For more accurate results that better simulate real-world conditions, use the TPU client mode:

```bash
solana-bench-tps \
  --client-node-id /home/sol/validator-keypair.json \
  --url http://localhost:8899 \
  --duration 60 \
  --tx-count 3500 \
  --use-tpu-client \
  --num-lamports-per-account 10000
```

Parameters explained:
- `--use-tpu-client`: Uses the Transaction Processing Unit client for sending transactions directly to the TPU port, which can achieve higher throughput than RPC
- `--num-lamports-per-account`: Specifies the amount of lamports to fund each test account with (10000 in this case)

## Benchmark Configuration Options

Customize your benchmarks with these additional options:

### Performance Tuning

```bash
solana-bench-tps \
  --client-node-id /home/sol/validator-keypair.json \
  --url http://localhost:8899 \
  --duration 60 \
  --tx-count 5000 \
  --threads 4 \
  --sustained
```

The `--sustained` flag maintains a constant rate of transactions rather than sending them all at once.

### Network Configuration Testing

For testing different network configurations:

```bash
solana-bench-tps \
  --client-node-id /home/sol/validator-keypair.json \
  --url http://localhost:8899 \
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
   - Ensure the client keypair has sufficient balance
   - Reduce transaction count or rate if node is overwhelmed
   - Check node logs for error messages

3. **Low TPS results**:
   - Try increasing threads
   - Verify hardware specifications meet requirements
   - Check for network congestion or resource contention

## Conclusion

By following this guide, you've learned how to install and run `solana-bench-tps` to benchmark your SVMKit network. These benchmarks provide valuable insights into your network's performance and can help identify optimization opportunities.

For more comprehensive testing, consider running multiple benchmarks with different parameters and comparing the results. Regularly benchmarking your network ensures optimal performance for validators and users.

## Recommended Benchmark Command

The following command represents a recommended configuration for benchmarking SVMKit networks:

```bash
solana-bench-tps \
  --client-node-id /home/sol/validator-keypair.json \
  --use-tpu-client \
  --tx-count 3500 \
  --duration 60 \
  --url "http://localhost:8899" \
  --num-lamports-per-account 10000
```

This configuration:
- Uses the TPU client for higher throughput
- Sends 3500 transactions over 60 seconds
- Funds test accounts with 10000 lamports each
- Connects to a local SVMKit node