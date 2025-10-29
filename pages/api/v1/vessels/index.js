/**
 * Vessels API endpoint
 * Returns list of registered vessels
 */

import vesselsData from '../../../../data/demo/vessels.json';

export default function handler(req, res) {
  const { status, limit } = req.query;

  let vessels = vesselsData.vessels;

  // Filter by status if provided
  if (status) {
    vessels = vessels.filter(v => v.currentPosition.status.toLowerCase().includes(status.toLowerCase()));
  }

  // Limit results if specified
  if (limit) {
    vessels = vessels.slice(0, parseInt(limit));
  }

  res.status(200).json({
    count: vessels.length,
    vessels: vessels
  });
}
