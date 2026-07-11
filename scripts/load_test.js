import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '5s', target: 5 }, // Ramp up
    { duration: '10s', target: 5 }, // Stable
    { duration: '5s', target: 0 }, // Ramp down
  ],
  thresholds: {
    // Health API < 100ms
    'http_req_duration{target:health}': ['p(95)<100'],
    // Metrics API < 250ms
    'http_req_duration{target:metrics}': ['p(95)<250'],
    // Auth API < 300ms
    'http_req_duration{target:auth}': ['p(95)<300'],
    // Review API < 500ms
    'http_req_duration{target:review}': ['p(95)<500'],
    // Chat API < 12s
    'http_req_duration{target:chat}': ['p(95)<12000', 'avg<8000'],
    'http_req_failed': ['rate<0.01'], // less than 1% errors
  }
};

const BASE_URL = 'http://localhost:8000/api/v1';

export default function () {
  // 1. Health API
  const resHealth = http.get(`${BASE_URL}/health`, { tags: { target: 'health' } });
  check(resHealth, { 'health status 200': (r) => r.status === 200 });
  
  sleep(1);

  // 2. Auth API (Login)
  const payload = JSON.stringify({ username: 'dr_smith', password: 'password123' });
  const params = { headers: { 'Content-Type': 'application/json' }, tags: { target: 'auth' } };
  const resAuth = http.post(`${BASE_URL}/auth/login`, payload, params);
  check(resAuth, { 'auth status 200': (r) => r.status === 200 });

  const token = resAuth.json('access_token');
  const authHeaders = { headers: { 'Authorization': `Bearer ${token}` } };
  
  sleep(1);

  // 3. Metrics API
  const resMetrics = http.get(`${BASE_URL}/metrics/overview`, { ...authHeaders, tags: { target: 'metrics' } });
  check(resMetrics, { 'metrics status 200': (r) => r.status === 200 });
  
  sleep(1);

  // 4. Review API
  const resReview = http.get(`${BASE_URL}/reviews/tasks`, { ...authHeaders, tags: { target: 'review' } });
  check(resReview, { 'review status 200': (r) => r.status === 200 });
  
  sleep(1);
  
  // 5. Chat API
  // We can't realistically mock an entire LangGraph run concurrently at high load without killing a local machine.
  // But we will send a basic ping to the chat endpoint to measure the initial routing latency.
  const chatPayload = JSON.stringify({ message: "Hello", session_id: "test_session_k6" });
  const chatParams = { headers: { 'Content-Type': 'application/json' }, tags: { target: 'chat' } };
  const resChat = http.post(`${BASE_URL}/chat`, chatPayload, chatParams);
  check(resChat, { 'chat status 200': (r) => r.status === 200 });
}
