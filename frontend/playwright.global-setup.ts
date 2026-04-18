import { ChildProcess, spawn } from 'child_process';
import http from 'http';
import path from 'path';

const BACKEND_PORT = 8000;
const BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`;
const MAX_RETRIES = 60;
const RETRY_DELAY_MS = 1000;

let backendProcess: ChildProcess | null = null;

function checkBackendHealth(attempt = 1): Promise<boolean> {
  return new Promise<boolean>((resolve) => {
    const req = http.get(`${BACKEND_URL}/health`, { timeout: 2000 }, (res) => {
      resolve(res.statusCode === 200 || res.statusCode === 204);
    });

    req.on('error', () => {
      if (attempt < MAX_RETRIES) {
        if (attempt % 10 === 1) {
          console.log(`[E2E Setup] Backend health check ${attempt}/${MAX_RETRIES}...`);
        }
        setTimeout(() => {
          checkBackendHealth(attempt + 1).then(resolve);
        }, RETRY_DELAY_MS);
      } else {
        resolve(false);
      }
    });

    req.on('timeout', () => {
      req.destroy();
      if (attempt < MAX_RETRIES) {
        setTimeout(() => {
          checkBackendHealth(attempt + 1).then(resolve);
        }, RETRY_DELAY_MS);
      } else {
        resolve(false);
      }
    });
  });
}

async function globalSetup() {
  // Skip backend setup if demo mode is enabled
  if (process.env.DEMO_MODE === 'true') {
    console.log('[E2E Setup] DEMO_MODE enabled, skipping backend startup');
    return;
  }

  console.log('[E2E Setup] Checking backend health...');
  
  // Check if backend is already running
  const isHealthy = await checkBackendHealth(1);
  if (isHealthy) {
    console.log('[E2E Setup] Backend API is already running on port 8000');
    return;
  }

  console.log('[E2E Setup] Backend not responding, attempting to start...');
  console.log(`[E2E Setup] Current directory: ${process.cwd()}`);
  console.log(`[E2E Setup] Launching backend with Python...`);
  
  return new Promise<void>((resolve, reject) => {
    // Use the absolute path to the backend directory
    const backendDir = path.join(process.cwd(), 'backend');
    const backendScript = path.join(backendDir, 'run_api.py');
    
    console.log(`[E2E Setup] Backend script: ${backendScript}`);

    backendProcess = spawn('python', [
      backendScript,
      '--host', '127.0.0.1',
      '--port', BACKEND_PORT.toString(),
    ], {
      cwd: backendDir,
      env: {
        ...process.env,
        PYTHONUNBUFFERED: '1',
        PYTHONDONTWRITEBYTECODE: '1',
        DEMO_MODE: 'true',  // Enable demo mode for E2E tests
      },
      stdio: ['ignore', 'pipe', 'pipe'],
      shell: process.platform === 'win32' ? true : false,
    });

    if (!backendProcess || !backendProcess.pid) {
      reject(new Error('[E2E Setup] Failed to spawn backend process'));
      return;
    }

    console.log(`[E2E Setup] Backend process started with PID ${backendProcess.pid}`);

    let startupTimeout: NodeJS.Timeout | null = null;
    let outputLines = '';

    const onData = (data: Buffer, label: string) => {
      const text = data.toString();
      outputLines += text;
      console.log(`[Backend ${label}] ${text.trim()}`);
    };

    backendProcess.stdout?.on('data', (data: Buffer) => onData(data, 'OUT'));
    backendProcess.stderr?.on('data', (data: Buffer) => onData(data, 'ERR'));

    const healthCheck = async () => {
      const isHealthy = await checkBackendHealth();
      if (isHealthy) {
        if (startupTimeout) clearTimeout(startupTimeout);
        console.log('[E2E Setup] Backend API is ready!');
        resolve();
      } else {
        if (startupTimeout) clearTimeout(startupTimeout);
        console.error('[E2E Setup] Backend failed to start after max retries');
        console.error('[E2E Setup] Recent output:');
        console.error(outputLines.split('\n').slice(-20).join('\n'));
        if (backendProcess) {
          backendProcess.kill('SIGTERM');
        }
        reject(new Error('Backend API failed to become healthy within timeout'));
      }
    };

    // Start health check after a brief delay
    startupTimeout = setTimeout(healthCheck, 2000);

    backendProcess.on('error', (error: Error) => {
      if (startupTimeout) clearTimeout(startupTimeout);
      console.error('[E2E Setup] Failed to start backend process:', error.message);
      reject(error);
    });

    backendProcess.on('exit', (code: number, signal: string) => {
      if (code !== 0) {
        console.log(`[E2E Setup] Backend process exited with code ${code} (signal: ${signal})`);
      }
    });
  });
}

export default globalSetup;

