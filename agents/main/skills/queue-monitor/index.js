// queue-monitor skill implementation
// Starts and checks long-running queue monitors through the mock backend.

const BACKEND_URL = 'http://host.docker.internal:5000';

async function request(path, options = {}) {
  const response = await fetch(`${BACKEND_URL}${path}`, options);
  if (!response.ok) {
    throw new Error(`Backend request failed: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

async function execute(params = {}) {
  const restaurantName = params.restaurant_name || params.restaurant || params.name;
  const targetCount = params.target_count ?? params.target_queue_count ?? 5;

  return request('/api/queue-monitor/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      restaurant_name: restaurantName,
      target_count: targetCount
    })
  });
}

async function checkQueueStatus(taskId) {
  if (taskId) {
    return request(`/api/queue-monitor/check/${encodeURIComponent(taskId)}`);
  }
  return request('/api/monitors/check-all');
}

async function stopQueueMonitor(taskId) {
  return request(`/api/queue-monitor/stop/${encodeURIComponent(taskId)}`, {
    method: 'POST'
  });
}

module.exports = { execute, checkQueueStatus, stopQueueMonitor };
