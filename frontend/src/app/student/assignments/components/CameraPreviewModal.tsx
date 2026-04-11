"use client";

import { useRef, useState } from "react";
import { AlertCircle, CheckCircle2, RotateCcw, Maximize2, X } from "lucide-react";

interface CameraPreviewModalProps {
    isOpen: boolean;
    onConfirm: (file: File) => void;
    onCancel: () => void;
    isLoading?: boolean;
}

export default function CameraPreviewModal({
    isOpen,
    onConfirm,
    onCancel,
    isLoading = false,
}: CameraPreviewModalProps) {
    const previewRef = useRef<HTMLImageElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [previewImage, setPreviewImage] = useState<string | null>(null);
    const [scale, setScale] = useState(1);
    const [rotation, setRotation] = useState(0);
    const [fileName, setFileName] = useState<string | null>(null);
    const [fileSize, setFileSize] = useState<number | null>(null);
    const [quality, setQuality] = useState<"low" | "medium" | "high">("high");

    const handleFileSelect = (file: File) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const dataUrl = e.target?.result as string;
            setPreviewImage(dataUrl);
            setFileName(file.name);
            setFileSize(file.size);
            setRotation(0);
            setScale(1);
        };
        reader.readAsDataURL(file);
    };

    const handleRetake = () => {
        setPreviewImage(null);
        setFileName(null);
        setFileSize(null);
        fileInputRef.current?.click();
    };

    const handleRotate = () => {
        setRotation((prev) => (prev + 90) % 360);
    };

    const canvasToFile = async (): Promise<File | null> => {
        if (!previewRef.current || !canvasRef.current || !previewImage) return null;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext("2d");
        if (!ctx) return null;

        const img = new Image();
        img.onload = () => {
            canvas.width = img.width;
            canvas.height = img.height;

            ctx.save();
            ctx.translate(canvas.width / 2, canvas.height / 2);
            ctx.rotate((rotation * Math.PI) / 180);
            ctx.drawImage(img, -canvas.width / 2, -canvas.height / 2, canvas.width, canvas.height);
            ctx.restore();
        };
        img.src = previewImage;

        return new Promise((resolve) => {
            img.onload = () => {
                canvas.toBlob(
                    (blob) => {
                        if (blob) {
                            const file = new File([blob], fileName || "camera-submission.jpg", {
                                type: "image/jpeg",
                            });
                            resolve(file);
                        } else {
                            resolve(null);
                        }
                    },
                    "image/jpeg",
                    quality === "high" ? 0.95 : quality === "medium" ? 0.8 : 0.65
                );
            };
        });
    };

    const handleConfirm = async () => {
        const file = await canvasToFile();
        if (file) {
            onConfirm(file);
        }
    };

    if (!isOpen) return null;

    const fileSizeMB = fileSize ? (fileSize / 1024 / 1024).toFixed(2) : null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-sm">
            <div className="w-full max-w-2xl rounded-3xl border border-[var(--border)] bg-[primary-surface] shadow-[0_20px_60px_rgba(0,0,0,0.3)]">
                {/* Header */}
                <div className="flex items-center justify-between border-b border-[var(--border)] px-6 py-4">
                    <h2 className="text-lg font-bold text-[var(--text-primary)]">Review notebook photo</h2>
                    <button
                        onClick={onCancel}
                        disabled={isLoading}
                        className="rounded-lg p-2 text-[var(--text-secondary)] transition hover:bg-[rgba(255,255,255,0.05)] disabled:opacity-50"
                    >
                        <X className="h-5 w-5" />
                    </button>
                </div>

                {/* Content */}
                <div className="space-y-4 p-6">
                    {previewImage ? (
                        <div className="space-y-4">
                            {/* Preview image with rotation */}
                            <div className="flex flex-col items-center justify-center overflow-hidden rounded-2xl border border-[var(--border)] bg-black/20 p-4">
                                {/* eslint-disable-next-line @next/next/no-img-element */}
                                <img
                                    ref={previewRef}
                                    src={previewImage}
                                    alt="Camera preview"
                                    style={{
                                        transform: `rotate(${rotation}deg) scale(${scale})`,
                                        maxHeight: "400px",
                                        maxWidth: "100%",
                                        objectFit: "contain",
                                        transition: "transform 200ms ease-out",
                                    }}
                                    className="rounded-lg"
                                    loading="lazy"
                                />
                            </div>

                            {/* File info and quality controls */}
                            <div className="grid gap-3 sm:grid-cols-2">
                                <div className="rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-3">
                                    <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-[var(--text-muted)]">
                                        File size
                                    </p>
                                    <p className="mt-1 text-sm font-semibold text-[var(--text-primary)]">
                                        {fileSizeMB}
                                        {fileSizeMB && <span className="ml-1 text-xs opacity-60">MB</span>}
                                    </p>
                                </div>

                                <div className="rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-3">
                                    <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-[var(--text-muted)]">
                                        Quality setting
                                    </p>
                                    <div className="mt-2 flex gap-1">
                                        {(["low", "medium", "high"] as const).map((q) => (
                                            <button
                                                key={q}
                                                onClick={() => setQuality(q)}
                                                className={`flex-1 rounded-lg px-2 py-1 text-[10px] font-bold uppercase transition ${
                                                    quality === q
                                                        ? "bg-[var(--primary)] text-[#06101e]"
                                                        : "bg-[rgba(255,255,255,0.05)] text-[var(--text-secondary)] hover:bg-[rgba(255,255,255,0.08)]"
                                                }`}
                                            >
                                                {q}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            {/* Rotation and zoom controls */}
                            <div className="flex gap-2">
                                <button
                                    onClick={handleRotate}
                                    disabled={isLoading}
                                    className="flex flex-1 items-center justify-center gap-2 rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.07)] px-3 py-2.5 text-xs font-bold text-[var(--text-primary)] transition hover:bg-[rgba(148,163,184,0.12)] disabled:opacity-50"
                                >
                                    <RotateCcw className="h-4 w-4" />
                                    Rotate 90°
                                </button>
                                <button
                                    onClick={() => setScale(Math.min(scale + 0.1, 1.5))}
                                    disabled={isLoading || scale >= 1.5}
                                    className="flex flex-1 items-center justify-center gap-2 rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.07)] px-3 py-2.5 text-xs font-bold text-[var(--text-primary)] transition hover:bg-[rgba(148,163,184,0.12)] disabled:opacity-50"
                                >
                                    <Maximize2 className="h-4 w-4" />
                                    Zoom in
                                </button>
                            </div>

                            {/* Quality feedback */}
                            {fileSizeMB && parseFloat(fileSizeMB) > 10 ? (
                                <div className="rounded-2xl border border-amber-500/20 bg-amber-500/6 p-3">
                                    <p className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.12em] text-status-amber">
                                        <AlertCircle className="h-3.5 w-3.5" />
                                        Large file warning
                                    </p>
                                    <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">
                                        This photo is {fileSizeMB} MB. Consider lower quality if upload is slow.
                                    </p>
                                </div>
                            ) : null}
                        </div>
                    ) : (
                        <div className="rounded-2xl border-2 border-dashed border-[var(--border)] bg-[rgba(148,163,184,0.03)] py-12 text-center">
                            <p className="text-sm font-semibold text-[var(--text-secondary)]">
                                Tap the button below to capture your notebook
                            </p>
                        </div>
                    )}

                    <canvas ref={canvasRef} className="hidden" />
                </div>

                {/* Footer */}
                <div className="flex gap-3 border-t border-[var(--border)] px-6 py-4">
                    {previewImage ? (
                        <>
                            <button
                                onClick={handleRetake}
                                disabled={isLoading}
                                className="flex flex-1 items-center justify-center gap-2 rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.07)] px-4 py-3 text-xs font-bold text-[var(--text-primary)] transition hover:bg-[rgba(148,163,184,0.12)] disabled:opacity-50"
                            >
                                <RotateCcw className="h-4 w-4" />
                                Retake
                            </button>
                            <button
                                onClick={handleConfirm}
                                disabled={isLoading}
                                className="flex flex-1 items-center justify-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(79,70,229,0.92))] px-4 py-3 text-xs font-bold text-[#06101e] transition hover:-translate-y-0.5 disabled:opacity-50"
                            >
                                <CheckCircle2 className="h-4 w-4" />
                                {isLoading ? "Confirming..." : "Confirm & Submit"}
                            </button>
                        </>
                    ) : (
                        <>
                            <button
                                onClick={onCancel}
                                disabled={isLoading}
                                className="flex flex-1 items-center justify-center gap-2 rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.07)] px-4 py-3 text-xs font-bold text-[var(--text-primary)] transition hover:bg-[rgba(148,163,184,0.12)] disabled:opacity-50"
                            >
                                <X className="h-4 w-4" />
                                Cancel
                            </button>
                            <label className="flex flex-1 items-center justify-center gap-2 rounded-2xl border border-[rgba(96,165,250,0.28)] bg-[rgba(96,165,250,0.09)] px-4 py-3 text-xs font-bold text-[var(--text-primary)] transition hover:bg-[rgba(96,165,250,0.14)]">
                                Open camera
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept="image/*"
                                    capture="environment"
                                    className="hidden"
                                    onChange={(e) => {
                                        const file = e.target.files?.[0];
                                        if (file) handleFileSelect(file);
                                    }}
                                />
                            </label>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
