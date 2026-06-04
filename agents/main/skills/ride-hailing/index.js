// ride-hailing skill implementation
// Books rides through the mock backend so traffic-aware estimates are shared.

const BACKEND_URL = 'http://host.docker.internal:5000';

async function execute(params = {}) {
  const response = await fetch(`${BACKEND_URL}/api/ride-hailing`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      destination: params.destination,
      origin: params.origin || '当前位置',
      car_type: params.car_type || '快车'
    })
  });

  if (!response.ok) {
    throw new Error(`Backend request failed: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

module.exports = { execute };
