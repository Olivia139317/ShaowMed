// local-life-radar skill implementation
// Calls the dynamic mock backend instead of using stale local fixtures.

const BACKEND_URL = 'http://host.docker.internal:5000';

async function postJson(path, body) {
  const response = await fetch(`${BACKEND_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {})
  });

  if (!response.ok) {
    throw new Error(`Backend request failed: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

async function getRecommendations(params = {}) {
  const payload = {
    message: params.message || params.user_message || params.query || '',
    cuisine: params.cuisine,
    max_price: params.max_price
  };

  return postJson('/api/chat', payload);
}

async function execute(params = {}) {
  return getRecommendations(params);
}

module.exports = { execute, getRecommendations };
