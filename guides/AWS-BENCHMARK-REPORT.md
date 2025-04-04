# Solana TPS Threshold Report: Instance Requirements Analysis

## Executive Summary

This report provides a detailed analysis of Transactions Per Second (TPS) thresholds and the required AWS instance sizes to facilitate target TPS goals of 100, 1,000, 10,000, and 100,000. Based on comprehensive benchmarking tests across various AWS instance types and node configurations, we present possible hardware requirements for each performance tier.

## Key Findings and Recommendations

| TPS Target | Recommended Instance | vCPUs | Memory | Network | Node Count | Actual TPS Achieved | Max TPS | Storage |
|------------|---------------------|-------|--------|---------|------------|---------------------|---------|---------|
| 100 TPS    | c6i.xlarge          | 4     | 8 GB   | 12.5 Gbps | 3        | 106.70 (avg)        | 108.97  | 500GB accounts, 1TB ledger |
| 1,000 TPS  | c6i.2xlarge         | 8     | 16 GB  | 12.5 Gbps | 3        | 988.82 (avg)        | 1,008.78 | 750GB accounts, 1.5TB ledger |
| 10,000 TPS | c6i.4xlarge         | 16    | 32 GB  | 12.5 Gbps | 3        | 9,483.11 (avg)      | 12,816.68 | 1TB accounts, 2TB ledger |
| 100,000 TPS | c6i.16xlarge       | 64    | 128 GB | 25 Gbps   | 10       | 72,060.38 (avg)     | 117,542.17 | 3TB accounts, 6TB ledger |

## Detailed Test Results

### 100 TPS Performance Tier

**Optimal Configuration**: c6i.xlarge (4 vCPUs, 8 GB RAM) with 3 nodes
**Command Used**:
```bash
solana-bench-tps \
  --client-node-id /home/sol/validator-keypair.json \
  --use-tpu-client \
  --tx-count 100 \
  --duration 60 \
  --url "http://localhost:8899" \
  --num-lamports-per-account 10000
```

**Performance Results**:
- Average TPS: 106.70
- Maximum TPS: 108.97
- Drop Rate: 0.00%

**Resource Utilization**:
- CPU: 37.65% average
- Memory: 24.19% average
- Network Traffic: 595.97 KB/s in, 335.28 KB/s out
- Disk I/O: 16,204.80 KB/s [^1]

**Analysis**: The c6i.xlarge instance easily handled 100 TPS with significant headroom remaining. Resource utilization was moderate, with zero transaction drops, indicating a stable and reliable configuration for this performance tier.

[^1]: The higher disk I/O observed in the c6i.xlarge instance (100 TPS test) compared to the c6i.2xlarge instance (1,000 TPS test) is due to memory management behavior. System metrics show aggressive memory reclamation (295,128 pages stolen per sample) with substantial dirty memory (~109,169 KB average) awaiting disk writes. Limited available memory (only ~107,941 KB) forced the Linux kernel to perform frequent cache flushes to disk, with write activity spikes reaching 58,000 KB/s. The c6i.xlarge operated under memory constraints, requiring more frequent page offloading to disk than the c6i.2xlarge, which had sufficient memory to maintain data in cache.

### 1,000 TPS Performance Tier

**Optimal Configuration**: c6i.2xlarge (8 vCPUs, 16 GB RAM) with 3 nodes
**Command Used**:
```bash
solana-bench-tps \
  --client-node-id /home/sol/validator-keypair.json \
  --use-tpu-client \
  --tx-count 1000 \
  --duration 60 \
  --url "http://localhost:8899" \
  --num-lamports-per-account 10000
```

**Performance Results**:
- Average TPS: 988.82
- Maximum TPS: 1,008.78
- Drop Rate: 0.00%

**Resource Utilization**:
- CPU: 19.01% average
- Memory: 17.80% average
- Network Traffic: 1,088.32 KB/s in, 412.29 KB/s out
- Disk I/O: 6,142.93 KB/s

**Analysis**: The c6i.2xlarge instance demonstrated excellent performance at the 1,000 TPS level with low resource utilization and zero transaction drops. This configuration provides a good balance of cost and performance for applications requiring 1,000 TPS.

### 10,000 TPS Performance Tier

**Optimal Configuration**: c6i.4xlarge (16 vCPUs, 32 GB RAM) with 3 nodes
**Command Used**:
```bash
solana-bench-tps \
  --client-node-id /home/sol/validator-keypair.json \
  --use-tpu-client \
  --tx-count 10000 \
  --duration 60 \
  --url "http://localhost:8899" \
  --num-lamports-per-account 10000
```

**Performance Results**:
- Average TPS: 9,483.11
- Maximum TPS: 12,816.68
- Drop Rate: 0.01%

**Resource Utilization**:
- CPU: 18.22% average
- Memory: 11.77% average
- Network Traffic: 4,902.45 KB/s in, 1,122.54 KB/s out
- Disk I/O: 45,373.29 KB/s

**Analysis**: The c6i.4xlarge instance approached the 10,000 TPS target with very low resource utilization, achieving 9,483 TPS average and peaks over 12,800 TPS. With a minimal drop rate of 0.01%, this configuration is highly suitable for applications demanding near 10,000 TPS performance.

### 100,000 TPS Performance Tier

**Optimal Configuration**: c6i.16xlarge (64 vCPUs, 128 GB RAM) with 10 nodes
**Command Used**:
```bash
solana-bench-tps \
  --client-node-id /home/sol/validator-keypair.json \
  --use-tpu-client \
  --tx-count 100000 \
  --duration 60 \
  --url "http://localhost:8899" \
  --num-lamports-per-account 10000
```

**Performance Results**:
- Average TPS: 72,060.38
- Maximum TPS: 117,542.17
- Drop Rate: 0.08%

**Resource Utilization**:
- CPU: 30.73% average
- Memory: 14.16% average
- Network Traffic: 64,460.45 KB/s in, 9,924.43 KB/s out
- Disk I/O: 234,303.52 KB/s

**Analysis**: The 10-node setup with c6i.16xlarge instances delivered exceptional performance, achieving over 72,000 TPS on average with peaks above 117,000 TPS. This configuration demonstrated that Solana can approach and even exceed 100,000 TPS with proper hardware sizing. The low drop rate of 0.08% indicates the system maintained good reliability even at this high throughput level.

## Cost Considerations for Production Deployments

| TPS Target | Instance Type   | Node Count | Monthly Cost (Estimated) |
|------------|-----------------|------------|--------------------------|
| 100 TPS    | c6i.xlarge      | 3          | ~$375 (On-Demand)        |
| 1,000 TPS  | c6i.2xlarge     | 3          | ~$750 (On-Demand)        |
| 10,000 TPS | c6i.4xlarge     | 3          | ~$1,500 (On-Demand)      |
| 100,000 TPS | c6i.16xlarge   | 10         | ~$22,000 (On-Demand)     |

*Note: Costs include instance pricing only; additional costs for storage, data transfer, and other AWS services would apply.*

## Conclusion

This benchmarking study demonstrates that Solana can achieve impressive performance levels with proper hardware sizing:

1. **100 TPS Requirements**: Even modest hardware (c6i.xlarge) with 3 nodes can easily sustain this performance level with minimal resource utilization.

2. **1,000 TPS Requirements**: Slightly larger instances (c6i.2xlarge) with 3 nodes provide excellent performance at this tier with low resource consumption.

3. **10,000 TPS Requirements**: Mid-range instances (c6i.4xlarge) with 3 nodes can deliver performance approaching 10,000 TPS with relatively low resource utilization.

4. **100,000 TPS Requirements**: Achieving performance at this tier requires more powerful instances (c6i.16xlarge) and a larger validator set (10 nodes). While the tested configuration averaged over 72,000 TPS with peaks exceeding 117,000 TPS, sustained 100,000 TPS would likely require additional optimizations or nodes.

For production deployments, we recommend selecting the appropriate instance type based on your TPS requirements and adding a 30-50% resource buffer to account for varying network conditions, transaction complexity, and future growth.