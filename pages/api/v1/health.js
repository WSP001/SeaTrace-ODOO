/**
 * Health check endpoint
 * Returns service status and build information
 */

export default function handler(req, res) {
  res.status(200).json({
    status: 'healthy',
    service: 'SeaTrace API',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    build: {
      environment: process.env.NODE_ENV || 'development',
      gitCommit: process.env.GIT_COMMIT || 'local',
      deployedAt: process.env.DEPLOYED_AT || new Date().toISOString()
    },
    pillars: {
      seaside: 'operational',
      deckside: 'operational',
      dockside: 'operational',
      marketside: 'operational'
    }
  });
}
