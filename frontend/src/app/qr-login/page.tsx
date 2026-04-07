"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Camera, Loader2, QrCode } from "lucide-react";
import { api } from "@/lib/api";
import { getRoleDashboard } from "@/lib/auth";
import { PrismHeroKicker, PrismPage, PrismPanel, PrismSection } from "@/components/prism/PrismPage";

export default function QrLoginPage() {
  const router = useRouter();
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const detectorRef = useRef<{ detect: (video: HTMLVideoElement) => Promise<Array<{ rawValue: string }>> } | null>(null);
  const rafRef = useRef<number | null>(null);

  const [tokenInput, setTokenInput] = useState("");
  const [scanning, setScanning] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const stopScanner = () => {
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    detectorRef.current = null;
    setScanning(false);
  };

  const extractToken = (raw: string) => {
    if (!raw) return "";
    try {
      const url = new URL(raw);
      if (url.pathname.includes("/api/auth/qr-login/")) {
        const parts = url.pathname.split("/api/auth/qr-login/");
        return parts[1] || "";
      }
      const tokenParam = url.searchParams.get("token");
      if (tokenParam) return tokenParam;
    } catch {
      // Ignore URL parsing; use raw input fallback.
    }
    if (raw.includes("/api/auth/qr-login/")) {
      return raw.split("/api/auth/qr-login/")[1]?.split("?")[0] || raw;
    }
    return raw.trim();
  };

  const handleLogin = async (rawToken: string) => {
    const token = extractToken(rawToken);
    if (!token) {
      setError("QR token not found");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await api.auth.qrLogin(token);
      const user = await api.auth.me();
      router.push(getRoleDashboard(user.role));
    } catch (err) {
      setError(err instanceof Error ? err.message : "QR login failed");
    } finally {
      setLoading(false);
      stopScanner();
    }
  };

  const scanLoop = async () => {
    if (!detectorRef.current || !videoRef.current) return;
    try {
      const barcodes = await detectorRef.current.detect(videoRef.current);
      if (barcodes.length > 0) {
        await handleLogin(barcodes[0].rawValue);
        return;
      }
    } catch {
      // Ignore scan errors.
    }
    rafRef.current = requestAnimationFrame(scanLoop);
  };

  const startScanner = async () => {
    setError(null);
    const DetectorConstructor =
      typeof window !== "undefined"
        ? (window as unknown as {
            BarcodeDetector?: new (options?: { formats?: string[] }) => {
              detect: (video: HTMLVideoElement) => Promise<Array<{ rawValue: string }>>;
            };
          }).BarcodeDetector
        : undefined;
    if (!DetectorConstructor) {
      setError("QR scanner is not supported in this browser. Please enter the code manually.");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      detectorRef.current = new DetectorConstructor({ formats: ["qr_code"] });
      setScanning(true);
      rafRef.current = requestAnimationFrame(scanLoop);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to access camera");
    }
  };

  useEffect(() => {
    return () => stopScanner();
  }, []);

  return (
    <PrismPage className="flex min-h-screen items-center py-10">
      <PrismSection className="mx-auto max-w-5xl">
        <div className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="space-y-5">
            <PrismHeroKicker>
              <QrCode className="h-3.5 w-3.5" />
              QR Entry
            </PrismHeroKicker>
            <h1 className="prism-title text-5xl font-black leading-[0.96] text-[var(--text-primary)] md:text-6xl">
              Fast student entry with a <span className="premium-gradient">camera-first flow</span>
            </h1>
            <p className="max-w-xl text-lg leading-8 text-[var(--text-secondary)]">
              Use a school QR card for quick access, or paste the token manually when camera scanning is unavailable.
            </p>
          </div>

          <PrismPanel className="p-6">
            {error ? (
              <div className="mb-4 rounded-[var(--radius-sm)] border border-error-subtle bg-error-subtle px-4 py-3 text-sm text-status-red">
                {error}
              </div>
            ) : null}

            <div className="rounded-[var(--radius-sm)] border border-[var(--border)] bg-[rgba(148,163,184,0.05)] p-3">
              {scanning ? (
                <video ref={videoRef} className="w-full rounded-[var(--radius-sm)]" />
              ) : (
                <div className="flex min-h-[260px] flex-col items-center justify-center rounded-[var(--radius-sm)] border border-dashed border-[var(--border)] bg-[rgba(148,163,184,0.04)] text-center">
                  <Camera className="mb-3 h-8 w-8 text-[var(--text-muted)]" />
                  <p className="text-sm font-semibold text-[var(--text-primary)]">Camera preview will appear here</p>
                  <p className="mt-1 text-xs text-[var(--text-muted)]">Point the rear camera at the school QR card.</p>
                </div>
              )}
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
              <button onClick={() => void startScanner()} className="rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(129,140,248,0.94))] px-4 py-3 text-sm font-semibold text-[#06101e]" disabled={scanning || loading}>
                Start scan
              </button>
              {scanning ? (
                <button onClick={stopScanner} className="rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.06)] px-4 py-3 text-sm font-semibold text-[var(--text-primary)]">
                  Stop scan
                </button>
              ) : null}
            </div>

            <div className="mt-5 border-t border-[var(--border)] pt-5">
              <label className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--text-muted)]">Manual code</label>
              <div className="mt-3 flex gap-2">
                <input
                  value={tokenInput}
                  onChange={(e) => setTokenInput(e.target.value)}
                  placeholder="Enter QR login code"
                  className="flex-1 rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.04)] px-4 py-3 text-sm text-[var(--text-primary)]"
                />
                <button
                  onClick={() => void handleLogin(tokenInput)}
                  disabled={loading || !tokenInput.trim()}
                  className="inline-flex items-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(129,140,248,0.94))] px-4 py-3 text-sm font-semibold text-[#06101e] disabled:opacity-60"
                >
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Login"}
                </button>
              </div>
            </div>
          </PrismPanel>
        </div>
      </PrismSection>
    </PrismPage>
  );
}

