/**
 * Storage API endpoint
 * Returns cold storage records
 */

import storageData from '../../../../data/demo/storage.json';

export default function handler(req, res) {
  const { facilityId, species, status } = req.query;

  let records = storageData.storageRecords;

  // Filter by facility if provided
  if (facilityId) {
    records = records.filter(r => r.facilityId === facilityId);
  }

  // Filter by species if provided
  if (species) {
    records = records.filter(r => 
      r.species.toLowerCase().includes(species.toLowerCase())
    );
  }

  // Filter by status if provided
  if (status) {
    records = records.filter(r => r.status.toLowerCase() === status.toLowerCase());
  }

  res.status(200).json({
    count: records.length,
    storageRecords: records
  });
}
