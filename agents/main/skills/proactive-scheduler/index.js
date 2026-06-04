// proactive-scheduler skill implementation
// Delegates reminder decisions to the mock backend so heartbeat behavior
// stays aligned with /api/proactive-check and /api/proactive-feedback.

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

async function checkProactiveReminder(params = {}) {
  const now = new Date();
  return postJson('/api/proactive-check', {
    hour: params.hour ?? now.getHours(),
    weekday: params.weekday ?? ((now.getDay() + 6) % 7),
    identity_mode: params.identity_mode,
    user_busy: params.user_busy
  });
}

async function recordFeedback(action = 'reject') {
  return postJson('/api/proactive-feedback', { action });
}

async function execute(params = {}) {
  return checkProactiveReminder(params);
}

module.exports = { execute, checkProactiveReminder, recordFeedback };
