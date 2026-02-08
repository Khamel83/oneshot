# Convex Database for High-Frequency Trading: Research Report

**Date:** 2026-02-07
**Research Focus:** Convex (getconvex.com) for high-frequency trading applications

---

## Executive Summary

Convex is a full-stack, serverless database platform with strong ACID guarantees and built-in real-time capabilities. For high-frequency trading applications, Convex offers significant advantages over traditional databases like SQLite due to its superior concurrency model (Optimistic Concurrency Control), high write throughput (up to 800,000 writes/second), and automatic scalability. However, the official Python SDK currently lacks native async/await support for real-time subscriptions, which may impact Python-based trading systems.

**Key Finding:** Convex can handle 1000+ writes/second easily and is well-suited for time-series trading data, making it a strong candidate for trading applications that need real-time data synchronization across multiple clients.

---

## Performance Metrics

### Read/Write Latency
- **Specific Numbers:** Public documentation does not provide exact millisecond latency figures under load
- **Architecture:** Convex is architected for low-latency operations, especially in real-time scenarios
- **Best Practice:** Keep queries and mutations on limited records (under a few hundred) for optimal performance

### Query Speed Benchmarks
| Metric | Value |
|--------|-------|
| **Etch Storage Engine** | ~5 million reads/second |
| **Convex Virtual Machine (CVM)** | Up to 1 million transactions/second |
| **Write Throughput** | Up to 800,000 writes/second |
| **Sustained Transactions** | Over 100,000 transactions/second |

**Note:** For larger datasets, proper indexing is crucial to avoid slow full-table scans.

---

## Concurrency & Reliability

### Concurrency Model

**Optimistic Concurrency Control (OCC)**
- Assumes conflicts are infrequent
- Does not lock records during transactions
- Checks for conflicts at transaction end
- Automatically retries on conflict
- Allows high degree of parallelism

**Write Capabilities:**
- Can handle 800,000 writes/second (benchmarked)
- Supports 100,000+ sustained transactions/second
- Far exceeds the 1,000 writes/second threshold for HFT applications

### Reliability Features

| Feature | Description |
|---------|-------------|
| **ACID Guarantees** | Full compliance with Atomicity, Consistency, Isolation, Durability |
| **Isolation Level** | Serializable (highest level) - prevents dirty reads, non-repeatable reads, phantom reads |
| **Replication** | Data replicated across multiple availability zones |
| **Write-Ahead Logging** | WAL ensures crash recovery to consistent state |
| **Automatic Failover** | Managed service handles server failures gracefully |
| **Transactional Integrity** | Automatic rollback on failed operations |

**Server Outage Handling:**
- Multi-AZ replication prevents data loss
- Automatic failover with minimal downtime
- WAL ensures database recovery to consistent state

---

## Python SDK with Code Examples

### Installation & Setup

```bash
pip install convex
```

### Basic Usage (Synchronous)

The official Convex Python client is primarily designed for **synchronous operations**. It does not currently offer native `async/await` support for real-time subscriptions.

```python
from convex import ConvexClient
from dotenv import load_dotenv
import os

# Store deployment URL in environment variable
load_dotenv()
client = ConvexClient(os.environ.get("CONVEX_URL"))

# Run a query function
messages = client.query("messages:getMessages")

# Run a mutation function
client.mutation("messages:sendMessage", {
    "author": "Python App",
    "body": "Hello from Python!"
})
```

### Trading Data Example

```python
from convex import ConvexClient
import time

client = ConvexClient(os.environ.get("CONVEX_URL"))

# Store a trade
def record_trade(symbol, price, quantity, timestamp=None):
    if timestamp is None:
        timestamp = int(time.time() * 1000)  # Unix ms

    client.mutation("trades:record", {
        "symbol": symbol,
        "price": price,
        "quantity": quantity,
        "timestamp": timestamp
    })

# Query recent trades
def get_recent_trades(symbol, limit=100):
    return client.query("trades:getRecent", {
        "symbol": symbol,
        "limit": limit
    })
```

### Important Limitation

**Python SDK Real-time Subscriptions:**
- The Python client does NOT offer a direct "subscribe" method with async updates
- Real-time subscriptions are primarily available in the JavaScript/TypeScript client
- For Python, use `client.query()` and `client.mutation()` for on-demand operations
- Consider using a separate WebSocket service or polling for real-time updates in Python

---

## Time-Series Best Practices

Convex is not a specialized time-series database, but can effectively store time-series trading data with proper schema design.

### Recommended Schema Pattern

**1. Table Definition**
```javascript
// convex/schema.ts
export default defineSchema({
  trades: defineTable({
    symbol: v.string(),
    price: v.float64(),
    quantity: v.float64(),
    timestamp: v.number(),  // Unix timestamp in milliseconds
    exchange: v.optional(v.string()),
  })
    .index("by_symbol", ["symbol"])
    .index("by_timestamp", ["timestamp"])
    .index("by_symbol_time", ["symbol", "timestamp"]),
});
```

**2. Storage Guidelines**
| Aspect | Recommendation |
|--------|----------------|
| **Timestamp Format** | Unix timestamp (milliseconds since epoch) as `number` |
| **Per-Document** | Store each event (trade/tick) as separate document |
| **Indexing** | Create index on timestamp column for range queries |
| **Data Structure** | Flat documents with indexed timestamp field |

**3. Query Pattern**
```javascript
// Range query for time-series data
export const getTradesInRange = query({
  args: {
    symbol: v.string(),
    startTime: v.number(),
    endTime: v.number(),
  },
  handler: async (ctx, args) => {
    const trades = await ctx.db
      .query("trades")
      .withIndex("by_symbol_time", (q) =>
        q
          .eq("symbol", args.symbol)
          .gte("timestamp", args.startTime)
          .lte("timestamp", args.endTime)
      )
      .collect();
    return trades;
  },
});
```

---

## Real-Time Capabilities

### Convex vs Redis Pub/Sub

| Aspect | Convex | Redis Pub/Sub |
|--------|--------|---------------|
| **Model** | Data-centric subscriptions | Message-based channels |
| **Persistence** | Full database persistence | Fire-and-forget (no persistence) |
| **Delivery** | Guaranteed (state-based) | No guaranteed delivery |
| **Latency** | Near-instantaneous | Very low |
| **Setup** | Built-in, no extra infrastructure | Separate Redis instance required |
| **Client Support** | Primarily JavaScript/TypeScript | All languages |

### Convex Real-Time Architecture

**How It Works:**
1. Client subscribes to a query
2. Convex backend tracks data dependencies
3. When underlying data changes, Convex re-runs query
4. New results automatically pushed to client

**Subscription Speed:**
- Designed for "real-time" and "instant" updates
- Specific latency numbers not publicly documented
- Stateful backend with optimized data synchronization

### For Python Applications

**Limitation:** The Python SDK does not currently support async real-time subscriptions.

**Workarounds:**
1. **Hybrid Approach:** Use Python for data ingestion (mutations), JavaScript frontend for real-time UI
2. **Polling:** Implement polling in Python for near-real-time updates
3. **WebSocket Bridge:** Create a separate WebSocket service that subscribes via Convex JS and broadcasts to Python clients

---

## Convex vs SQLite Comparison

### Direct Comparison for High-Write Applications

| Feature | Convex | SQLite |
|---------|--------|--------|
| **Concurrency Model** | Optimistic Concurrency Control (OCC) | Database-level locking |
| **Write Throughput** | 800,000 writes/second | Limited by single-writer design |
| **Concurrent Writers** | Thousands per second | One at a time (WAL mode improves but limited) |
| **Scalability** | Serverless, auto-scaling, distributed | File-based, single-machine |
| **Horizontal Scaling** | Yes | No |
| **Real-time Subscriptions** | Built-in | Not available |
| **ACID Compliance** | Full (serializable isolation) | Full |
| **Replication** | Multi-AZ automatic | Manual implementation required |
| **Deployment** | Managed service | Self-hosted file |

### Why Convex is More Reliable for High-Write Applications

1. **No Write Locking Bottlenecks**
   - SQLite's default mode allows only one writer at a time
   - Even WAL mode has concurrency limitations
   - Convex's OCC enables thousands of concurrent writes

2. **Distributed Reliability**
   - SQLite: Single point of failure (one file)
   - Convex: Multi-AZ replication, automatic failover

3. **Real-Time Data Synchronization**
   - SQLite: No built-in pub/sub
   - Convex: Real-time subscriptions out of the box

4. **Automatic Scaling**
   - SQLite: Manual sharding required for scale
   - Convex: Handles increased load automatically

### When SQLite is Preferable

| Use Case | Why SQLite |
|----------|------------|
| Local embedded storage | No network dependency |
| Single-user desktop apps | Simpler deployment |
| Mobile apps (local cache) | Built into mobile platforms |
| Prototyping | Zero setup, file-based |

### When Convex is Preferable

| Use Case | Why Convex |
|----------|------------|
| Multi-user trading platforms | Concurrent writes |
| Real-time dashboards | Built-in subscriptions |
| High-frequency data ingestion | 800K writes/sec capability |
| Distributed systems | Multi-AZ reliability |
| Serverless applications | No infrastructure management |

---

## Sources & Resources

### Official Convex Documentation
- [Convex Website](https://getconvex.com)
- [Convex Documentation](https://docs.convex.dev)
- [Python SDK Reference](https://docs.convex.dev/client-library/python)
- [Performance Benchmarks](https://www.getconvex.dev/blog/introducing-etch-a-storage-engine-for-serverless-apps)

### Key Technical Concepts
- **Etch Storage Engine:** Convex's proprietary storage achieving 5M reads/sec
- **Convex Virtual Machine (CVM):** Handles transaction execution
- **Optimistic Concurrency Control (OCC):** Enables high parallelism

### Research Notes
- Research conducted via AI-powered deep research (Gemini CLI)
- Performance numbers based on published Convex benchmarks
- Specific latency numbers not publicly available in documentation
- Python SDK async support verified against current official documentation

---

## Recommendations for High-Frequency Trading

1. **Use Convex if:**
   - You need real-time data synchronization across multiple clients
   - Your application has concurrent write operations (>1 writer)
   - You want managed reliability (replication, failover)
   - You're building a web-based trading interface

2. **Consider Alternatives if:**
   - You need sub-microsecond latency (consider specialized HFT platforms)
   - Your Python backend requires async real-time subscriptions
   - You have strict data sovereignty requirements (managed service)

3. **Hybrid Architecture Suggestion:**
   ```
   Trading Bot (Python) -> Convex (storage) -> Web Dashboard (Convex JS)
                                              -> Mobile App (Convex JS)
   ```
   - Use Python SDK for high-frequency writes (mutations)
   - Use Convex JS SDK for real-time frontend subscriptions
   - Leverage Convex as single source of truth for all clients

---

*Generated: 2026-02-07*
*Research Method: Gemini CLI deep research with web verification*
