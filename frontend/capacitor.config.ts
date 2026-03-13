// Capacitor config — install @capacitor/cli to enable native builds
// npm i -D @capacitor/core @capacitor/cli

type CapacitorConfig = {
  appId: string;
  appName: string;
  webDir: string;
  server?: Record<string, unknown>;
  plugins?: Record<string, unknown>;
  android?: Record<string, unknown>;
};

const config: CapacitorConfig = {
  appId: 'com.modernhustlers.vidyaos',
  appName: 'VidyaOS',
  webDir: 'out',
  server: {
    // In development, point to your Next.js dev server
    // url: 'http://localhost:3000',
    // cleartext: true,
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#0f172a',
      androidScaleType: 'CENTER_CROP',
      showSpinner: true,
      spinnerColor: '#3b82f6',
    },
    StatusBar: {
      style: 'DARK',
      backgroundColor: '#0f172a',
    },
  },
  android: {
    allowMixedContent: true,
    captureInput: true,
    webContentsDebuggingEnabled: false,
  },
};

export default config;
