"use client";

import { useState, useRef, useEffect } from "react";
import { api } from "@/lib/api";
import { Loader2, Palette, Save, Type, Image as ImageIcon, CheckCircle2 } from "lucide-react";

export default function BrandingConfigPage() {
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [extracting, setExtracting] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const [form, setForm] = useState({
        primary_color: "#2563eb",
        secondary_color: "#16a34a",
        font_family: "Inter",
        logo_url: ""
    });

    useEffect(() => {
        loadConfig();
    }, []);

    const loadConfig = async () => {
        try {
            setLoading(true);
            const data = await api.admin.brandingConfig();
            setForm({
                primary_color: data.primary_color || "#2563eb",
                secondary_color: data.secondary_color || "#16a34a",
                font_family: data.font_family || "Inter",
                logo_url: data.logo_url || ""
            });
        } catch (error) {
            console.error("Failed to load branding config", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        try {
            setSaving(true);
            await api.admin.saveBranding(form);
            alert("Branding configuration saved successfully! Reload the page to see changes globally.");
        } catch (error) {
            console.error("Failed to save branding", error);
            alert("Failed to save branding configuration.");
        } finally {
            setSaving(false);
        }
    };

    const handleLogoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        try {
            setExtracting(true);
            const formData = new FormData();
            formData.append("file", file);

            // Mock saving the logo to S3/Local and getting url back. 
            // Here we just extract colors using the endpoint.
            const data = await api.admin.extractBranding(formData);
            
            if (data?.success && data.suggested_palette) {
                setForm(prev => ({
                    ...prev,
                    primary_color: data.suggested_palette.primary,
                    secondary_color: data.suggested_palette.secondary,
                    // logo_url: "url-to-uploaded-image" // In a real system, upload endpoint returns URL
                }));
                alert(`Extracted Palette:\nPrimary: ${data.suggested_palette.primary}\nSecondary: ${data.suggested_palette.secondary}`);
            }
        } catch (error) {
            console.error("Failed to extract colors", error);
            alert("Failed to process logo and extract colors.");
        } finally {
            setExtracting(false);
            if (fileInputRef.current) fileInputRef.current.value = "";
        }
    };

    if (loading) {
        return <div className="p-8 flex justify-center"><Loader2 className="animate-spin text-[var(--primary)]" /></div>;
    }

    return (
        <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* Left Column: Settings Form */}
            <div className="space-y-6">
                <div>
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                        <Palette className="w-6 h-6 text-[var(--primary)]" />
                        Branding Engine
                    </h1>
                    <p className="text-sm text-[var(--text-secondary)] mt-1">
                        Customize the platform's visual identity. Changes will instantly propagate to all students and teachers under your organization.
                    </p>
                </div>

                <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-[var(--radius)] p-6 space-y-6 shadow-sm">
                    
                    {/* Logo Section */}
                    <div>
                        <h3 className="text-sm font-semibold mb-3 flex items-center gap-2 border-b border-[var(--border)] pb-2">
                            <ImageIcon className="w-4 h-4 text-emerald-500" />
                            Logo & Color Extraction
                        </h3>
                        <p className="text-xs text-[var(--text-muted)] mb-4">
                            Upload a logo to automatically extract your brand's color palette mathematically powered by AI color analysis.
                        </p>
                        
                        <div className="flex items-center gap-4">
                            <input 
                                type="file" 
                                accept="image/png, image/jpeg, image/svg+xml"
                                className="hidden"
                                ref={fileInputRef}
                                onChange={handleLogoUpload}
                            />
                            <button 
                                onClick={() => fileInputRef.current?.click()}
                                disabled={extracting}
                                className="px-4 py-2 border border-dashed border-[var(--border)] rounded-md text-sm font-medium hover:bg-[var(--bg-hover)] transition-colors flex items-center gap-2 w-full justify-center"
                            >
                                {extracting ? <Loader2 className="w-4 h-4 animate-spin" /> : "Upload Organization Logo"}
                            </button>
                        </div>
                    </div>

                    {/* Colors Section */}
                    <div>
                        <h3 className="text-sm font-semibold mb-3 flex items-center gap-2 border-b border-[var(--border)] pb-2 mt-6">
                            <Palette className="w-4 h-4 text-blue-500" />
                            Theme Colors
                        </h3>
                        
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="text-xs font-medium text-[var(--text-secondary)] block mb-1">Primary Brand Color</label>
                                <div className="flex items-center gap-2">
                                    <input 
                                        type="color" 
                                        value={form.primary_color}
                                        onChange={e => setForm({...form, primary_color: e.target.value})}
                                        className="h-10 w-14 rounded cursor-pointer border-0 p-0"
                                    />
                                    <input 
                                        type="text" 
                                        value={form.primary_color}
                                        onChange={e => setForm({...form, primary_color: e.target.value})}
                                        className="flex-1 bg-[var(--bg-page)] border border-[var(--border)] rounded px-3 py-2 text-sm font-mono"
                                    />
                                </div>
                            </div>
                            
                            <div>
                                <label className="text-xs font-medium text-[var(--text-secondary)] block mb-1">Secondary / Success</label>
                                <div className="flex items-center gap-2">
                                    <input 
                                        type="color" 
                                        value={form.secondary_color}
                                        onChange={e => setForm({...form, secondary_color: e.target.value})}
                                        className="h-10 w-14 rounded cursor-pointer border-0 p-0"
                                    />
                                    <input 
                                        type="text" 
                                        value={form.secondary_color}
                                        onChange={e => setForm({...form, secondary_color: e.target.value})}
                                        className="flex-1 bg-[var(--bg-page)] border border-[var(--border)] rounded px-3 py-2 text-sm font-mono"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Typography Section */}
                    <div>
                        <h3 className="text-sm font-semibold mb-3 flex items-center gap-2 border-b border-[var(--border)] pb-2 mt-6">
                            <Type className="w-4 h-4 text-purple-500" />
                            Typography
                        </h3>
                        
                        <select 
                            value={form.font_family}
                            onChange={e => setForm({...form, font_family: e.target.value})}
                            className="w-full bg-[var(--bg-page)] border border-[var(--border)] rounded p-2 text-sm"
                        >
                            <option value="Inter">Inter (Modern & Clean)</option>
                            <option value="Merriweather">Merriweather (Academic Serif)</option>
                            <option value="Roboto">Roboto (Corporate System)</option>
                            <option value="Poppins">Poppins (Friendly Geometric)</option>
                        </select>
                    </div>

                    <button 
                        onClick={handleSave}
                        disabled={saving}
                        className="w-full bg-[var(--primary)] text-white font-medium py-2 rounded-[var(--radius)] flex justify-center items-center gap-2 hover:opacity-90 transition-opacity mt-4"
                    >
                        {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                        Save Brand Settings
                    </button>
                </div>
            </div>

            {/* Right Column: Live Preview */}
            <div className="sticky top-24 h-max">
                <div className="mb-2 flex justify-between items-center">
                    <span className="text-xs font-bold uppercase tracking-widest text-[var(--text-muted)]">Live Interface Preview</span>
                    <span className="flex items-center gap-1 text-[10px] text-emerald-600 bg-emerald-100 dark:bg-emerald-900/30 px-2 py-0.5 rounded-full">
                        <CheckCircle2 className="w-3 h-3" /> Real-time
                    </span>
                </div>
                
                {/* 
                    This wrapper intelligently overrides standard CSS variables locally 
                    so the preview perfectly matches how it will render globally.
                */}
                <div 
                    className="border-4 border-[var(--border-light)] rounded-2xl overflow-hidden shadow-2xl transition-all duration-500"
                    style={{
                        '--primary': form.primary_color,
                        '--success': form.secondary_color,
                        '--font-sans': `${form.font_family}, system-ui`
                    } as React.CSSProperties}
                >
                    {/* Mocked Application UI */}
                    <div className="bg-[var(--bg-page)] h-[600px] flex flex-col font-sans text-[var(--text-primary)]">
                        
                        {/* Mock Navbar */}
                        <div className="bg-[var(--card)] border-b border-[var(--border)] p-4 flex justify-between items-center">
                            <div className="font-bold text-lg flex items-center gap-2 text-[var(--primary)] shrink-0">
                                <span className="w-8 h-8 rounded bg-[var(--primary)] flex items-center justify-center text-white text-sm">OS</span>
                                {form.font_family} Academy
                            </div>
                            <div className="w-8 h-8 rounded-full bg-[var(--input)] animate-pulse" />
                        </div>

                        {/* Mock Dashboard Body */}
                        <div className="flex-1 p-6 space-y-6 overflow-y-auto">
                            <div className="flex justify-between items-end">
                                <div>
                                    <h2 className="text-xl font-bold">Good morning, Student!</h2>
                                    <p className="text-sm text-[var(--text-muted)]">You have 2 upcoming assignments.</p>
                                </div>
                                <button className="bg-[var(--primary)] text-white px-4 py-2 rounded-[var(--radius)] text-sm font-medium shadow-sm hover:opacity-90">
                                    View Schedule
                                </button>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-[var(--card)] border border-[var(--border)] p-4 rounded-[var(--radius)] shadow-sm">
                                    <div className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider mb-2">Subject Performance</div>
                                    <div className="text-3xl font-black text-[var(--primary)]">85%</div>
                                    <div className="text-xs text-[var(--success)] mt-1 font-medium bg-[var(--success)]/10 inline-block px-1 rounded">+5% from last week</div>
                                </div>
                                
                                <div className="bg-[var(--card)] border border-[var(--border)] p-4 rounded-[var(--radius)] shadow-sm">
                                    <div className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider mb-2">Attendance</div>
                                    <div className="text-3xl font-black text-[var(--success)]">100%</div>
                                    <div className="text-xs text-[var(--text-secondary)] mt-1 font-medium bg-[var(--bg-hover)] inline-block px-1 rounded">Perfect streak!</div>
                                </div>
                            </div>
                            
                            <div className="bg-[var(--primary)]/10 border border-[var(--primary)]/20 p-4 rounded-[var(--radius)]">
                                <h4 className="font-bold text-[var(--primary)] text-sm mb-1">AI Study Assistant Active</h4>
                                <p className="text-xs text-[var(--text-secondary)] opacity-80 mb-3">Your personalized AI tutor is ready to help you prepare for the Midterm.</p>
                                <button className="bg-[var(--primary)] text-white text-xs font-medium px-4 py-1.5 rounded-full">Start Session</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
