/**
 * Catches API endpoint
 * Returns validated catch tickets
 */

import catchesData from '../../../../data/demo/catches.json';

export default function handler(req, res) {
  const { species, vesselId, status } = req.query;

  let catches = catchesData.catches;

  // Filter by species if provided
  if (species) {
    catches = catches.filter(c => 
      c.species.common.toLowerCase().includes(species.toLowerCase())
    );
  }

  // Filter by vessel if provided
  if (vesselId) {
    catches = catches.filter(c => c.vesselId === vesselId);
  }

  // Filter by status if provided
  if (status) {
    catches = catches.filter(c => c.status.toLowerCase() === status.toLowerCase());
  }

  res.status(200).json({
    count: catches.length,
    catches: catches
  });
}
