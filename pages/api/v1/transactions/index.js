/**
 * Transactions API endpoint
 * Returns market transactions
 */

import transactionsData from '../../../../data/demo/transactions.json';

export default function handler(req, res) {
  const { status, buyer, species } = req.query;

  let transactions = transactionsData.transactions;

  // Filter by status if provided
  if (status) {
    transactions = transactions.filter(t => 
      t.status.toLowerCase().includes(status.toLowerCase())
    );
  }

  // Filter by buyer if provided
  if (buyer) {
    transactions = transactions.filter(t => 
      t.buyer.company.toLowerCase().includes(buyer.toLowerCase())
    );
  }

  // Filter by species if provided
  if (species) {
    transactions = transactions.filter(t => 
      t.product.species.toLowerCase().includes(species.toLowerCase())
    );
  }

  res.status(200).json({
    count: transactions.length,
    transactions: transactions
  });
}
