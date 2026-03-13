# Android Play Store Shell (TWA / Capacitor)

This document captures the minimal steps to wrap the VidyaOS PWA as a Play Store app.
Two supported paths are listed: **Trusted Web Activity (recommended)** and **Capacitor**.

---

## 1. Prerequisites
- `frontend/public/manifest.json` is present and kept in sync with branding.
- Service worker is enabled (`frontend/public/sw.js`).
- HTTPS hosting for production (required for TWA).

---

## 2. Trusted Web Activity (Recommended)

### 2.1 Add Digital Asset Links
Create `frontend/public/.well-known/assetlinks.json` using your final Android
package name and signing certificate fingerprint.

Example structure (replace values before production):
```json
[
  {
    "relation": ["delegate_permission/common.handle_all_urls"],
    "target": {
      "namespace": "android_app",
      "package_name": "com.vidyaos.app",
      "sha256_cert_fingerprints": ["REPLACE_WITH_SHA256_FINGERPRINT"]
    }
  }
]
```

### 2.2 Build the TWA
1. Install Bubblewrap: `npm i -g @bubblewrap/cli`
2. Generate the wrapper:
   ```bash
   bubblewrap init --manifest=https://your-domain/manifest.json
   ```
3. Build the Android APK/AAB:
   ```bash
   bubblewrap build
   ```

### 2.3 Publish
- Upload the generated AAB to Play Console.
- Verify the Digital Asset Links file is reachable:
  `https://your-domain/.well-known/assetlinks.json`

---

## 3. Capacitor (Alternative)

1. Install dependencies:
   ```bash
   npm install @capacitor/core @capacitor/cli
   npx cap init VidyaOS com.vidyaos.app
   npx cap add android
   ```
2. Build the PWA assets: `npm run build`
3. Sync to Android: `npx cap sync`
4. Open Android Studio: `npx cap open android`

Use Capacitor if you need native plugins (push notifications, camera).
For a pure PWA shell, TWA is lighter and simpler.

---

## 4. Operational Checklist
- Confirm start URL and icons in `manifest.json`.
- Ensure `APP_CORS_ORIGINS` includes the Android origin if needed.
- Validate QR login flow with device camera.
- Verify service worker caching in offline mode.

