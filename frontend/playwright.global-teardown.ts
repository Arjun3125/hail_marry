async function globalTeardown() {
  // Cleanup is handled by the global setup's signal handlers
  console.log('[E2E Teardown] Tests completed, backend cleanup initiated');
}

export default globalTeardown;
