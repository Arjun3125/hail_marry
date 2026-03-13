"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Camera, Loader2, QrCode } from "lucide-react";

import { api } from "@/lib/api";
import { getRoleDashboard } from "@/lib/auth";

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
            // non-url token payload
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
            // ignore scan errors
        }
        rafRef.current = requestAnimationFrame(scanLoop);
    };

    const startScanner = async () => {
        setError(null);
        const DetectorConstructor = typeof window !== "undefined" ? (window as unknown as { BarcodeDetector?: new (options?: { formats?: string[] }) => { detect: (video: HTMLVideoElement) => Promise<Array<{ rawValue: string }>> } }).BarcodeDetector : undefined;
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
        <div className="min-h-screen bg-[var(--bg-page)] flex items-center justify-center px-4">
            <div className="w-full max-w-lg space-y-6">
                <div className="text-center">
                    <div className="w-16 h-16 bg-[var(--primary-light)] rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <QrCode className="w-8 h-8 text-[var(--primary)]" />
                    </div>
                    <h1 className="text-2xl font-bold text-[var(--text-primary)]">Student QR Login</h1>
                    <p className="text-sm text-[var(--text-secondary)] mt-2">
                        Scan your school QR card or enter the code below.
                    </p>
                </div>

                {error ? (
                    <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)]">
                        {error}
                    </div>
                ) : null}

                <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-6 space-y-4">
                    <div className="rounded-[var(--radius-sm)] border border-[var(--border)] bg-[var(--bg-page)] p-3">
                        {scanning ? (
                            <video ref={videoRef} className="w-full rounded-[var(--radius-sm)]" />
                        ) : (
                            <div className="text-sm text-[var(--text-muted)] flex items-center gap-2">
                                <Camera className="w-4 h-4" />
                                Camera preview will appear here.
                            </div>
                        )}
                    </div>

                    <div className="flex flex-wrap gap-2">
                        <button
                            onClick={() => void startScanner()}
                            className="px-4 py-2 text-sm bg-[var(--primary)] text-white rounded-[var(--radius-sm)] hover:bg-[var(--primary-hover)] disabled:opacity-60"
                            disabled={scanning || loading}
                        >
                            Start Scan
                        </button>
                        {scanning && (
                            <button
                                onClick={stopScanner}
                                className="px-4 py-2 text-sm border border-[var(--border)] rounded-[var(--radius-sm)] hover:bg-[var(--bg-hover)]"
                            >
                                Stop Scan
                            </button>
                        )}
                    </div>

                    <div className="border-t border-[var(--border)] pt-4">
                        <label className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-widest">Manual Code</label>
                        <div className="mt-2 flex gap-2">
                            <input
                                value={tokenInput}
                                onChange={(e) => setTokenInput(e.target.value)}
                                placeholder="Enter QR login code"
                                className="flex-1 px-3 py-2 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                            />
                            <button
                                onClick={() => void handleLogin(tokenInput)}
                                disabled={loading || !tokenInput.trim()}
                                className="px-4 py-2 text-sm bg-[var(--primary)] text-white rounded-[var(--radius-sm)] hover:bg-[var(--primary-hover)] disabled:opacity-60 flex items-center gap-2"
                            >
                                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Login"}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
