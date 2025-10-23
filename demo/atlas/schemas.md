# Atlas Logical Model (Demo)

**Database:** `seatrace_demo`

## Collections

### vessels
Stores vessel metadata for demo fleets (bluewave, pelagic, northstar)

```json
{
  "_id": ObjectId,
  "vessel_id": "bl-001",
  "name": "bluewave-v0",
  "flag": "US",
  "gear": "LL",
  "mmsi": 100000001,
  "org": "bluewave"
}
```

### catches
Catch records with landed weight and timestamps

```json
{
  "_id": ObjectId,
  "vessel_id": "bl-001",
  "org": "bluewave",
  "species": "Tuna",
  "landed_kg": 3500,
  "landed_ts": ISODate("2025-10-15T08:30:00Z"),
  "trip_id": "uuid-string"
}
```

### em_events
Electronic Monitoring events (ingest + AI processing minutes)

```json
{
  "_id": ObjectId,
  "org": "bluewave",
  "vessel_id": "bl-001",
  "ts": ISODate("2025-10-15T02:30:00Z"),
  "minutes": 1200,
  "kind": "ingest",
  "trip_id": "uuid-string"
}
```

### er_reports
Electronic Reporting submissions (compliance tracking)

```json
{
  "_id": ObjectId,
  "org": "bluewave",
  "trip_id": "uuid-string",
  "submitted_ts": ISODate("2025-10-15T10:30:00Z"),
  "status": "submitted"
}
```

### usage_ledger (optional)
Mirror of EMR usage for historical queries

```json
{
  "_id": ObjectId,
  "org": "bluewave",
  "period": "202510",
  "meter": "ingest_min",
  "value": 45000
}
```

### commons_fund_snapshots
Monthly snapshots of Commons Fund coverage

```json
{
  "_id": ObjectId,
  "period": "2025-10",
  "coverage_pct": 112.5,
  "opex_usd": 85000,
  "marketside_xfer_usd": 12000
}
```

## Indexes

```javascript
// catches
db.catches.createIndex({ org: 1, landed_ts: -1 })
db.catches.createIndex({ trip_id: 1 })

// em_events
db.em_events.createIndex({ org: 1, ts: -1 })
db.em_events.createIndex({ trip_id: 1 })

// er_reports
db.er_reports.createIndex({ org: 1, submitted_ts: -1 })
db.er_reports.createIndex({ trip_id: 1 })
```

## KPI Queries

### ER Coverage % (Last 30 Days)
```javascript
// Total trips with catches
const totalTrips = db.catches.distinct("trip_id", {
  landed_ts: { $gte: new Date(Date.now() - 30*24*60*60*1000) }
}).length

// Trips with ER submissions
const submittedTrips = db.er_reports.distinct("trip_id", {
  submitted_ts: { $gte: new Date(Date.now() - 30*24*60*60*1000) }
}).length

const coverage = (submittedTrips / totalTrips * 100).toFixed(1)
```

### Median Catch→Report Latency
```javascript
db.catches.aggregate([
  {
    $lookup: {
      from: "er_reports",
      localField: "trip_id",
      foreignField: "trip_id",
      as: "report"
    }
  },
  { $unwind: "$report" },
  {
    $project: {
      latency_hours: {
        $divide: [
          { $subtract: ["$report.submitted_ts", "$landed_ts"] },
          3600000
        ]
      }
    }
  },
  {
    $group: {
      _id: null,
      median_latency: { $median: { input: "$latency_hours", method: "approximate" } }
    }
  }
])
```

### Cost Per Tonne (Run-Rate)
```javascript
// Aggregate EMR usage for current month
const emrUsage = db.em_events.aggregate([
  { $match: { ts: { $gte: new Date("2025-10-01") } } },
  {
    $group: {
      _id: { org: "$org", kind: "$kind" },
      total_minutes: { $sum: "$minutes" }
    }
  }
])

// Calculate pricing (use EMR pricing tiers from private repo)
// Then divide by total catch weight
const totalCatchKg = db.catches.aggregate([
  { $match: { landed_ts: { $gte: new Date("2025-10-01") } } },
  { $group: { _id: null, total_kg: { $sum: "$landed_kg" } } }
])

const costPerTonne = emrEstimateUSD / (totalCatchKg / 1000)
```
