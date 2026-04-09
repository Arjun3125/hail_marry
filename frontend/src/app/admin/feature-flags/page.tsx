"use client";

import { useEffect, useState } from "react";
import { Search, Loader2, ShieldAlert, Zap, BookOpen, Settings2 } from "lucide-react";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismSection } from "@/components/prism/PrismPage";
import { api } from "@/lib/api";

type FeatureFlag = {
    id: number;
    feature_id: string;
    name: string;
    description: string;
    category: "AI" | "Non-AI";
    module?: string;
    ai_intensity?: string;
    enabled: boolean;
};

export default function FeatureFlagsPage() {
    const [features, setFeatures] = useState<FeatureFlag[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");
    const [toggling, setToggling] = useState<string | null>(null);
    const [applyingProfile, setApplyingProfile] = useState<string | null>(null);

    useEffect(() => {
        loadFeatures();
    }, []);

    const loadFeatures = async () => {
        try {
            setLoading(true);
            const data = await api.admin.features();
            setFeatures(data);
        } catch (error) {
            console.error("Failed to load features", error);
        } finally {
            setLoading(false);
        }
    };

    const handleToggle = async (featureId: string, currentEnabled: boolean) => {
        try {
            setToggling(featureId);
            setFeatures(prev => prev.map(f => 
                f.feature_id === featureId ? { ...f, enabled: !currentEnabled } : f
            ));
            await api.admin.toggleFeature(featureId, !currentEnabled);
        } catch (error) {
            console.error("Failed to toggle feature", error);
            setFeatures(prev => prev.map(f => 
                f.feature_id === featureId ? { ...f, enabled: currentEnabled } : f
            ));
        } finally {
            setToggling(null);
        }
    };

    const handleApplyProfile = async (profileName: "ai_tutor" | "ai_helper" | "full_erp") => {
        if (!confirm(`Are you sure you want to apply the ${profileName} profile? This will bulk-toggle multiple features and disrupt active users.`)) return;
        
        try {
            setApplyingProfile(profileName);
            await api.admin.applyProfile(profileName);
            // Reload features to get exact state matching the backend
            await loadFeatures();
            alert(`Profile '${profileName}' applied successfully!`);
        } catch (error) {
            console.error("Failed to apply profile", error);
            alert("Failed to apply system profile.");
        } finally {
            setApplyingProfile(null);
        }
    };

    const filteredFeatures = features.filter(f => 
        f.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
        f.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        f.feature_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        f.module?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        f.ai_intensity?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const aiFeatures = filteredFeatures.filter(f => f.category === "AI" || f.ai_intensity === "Heavy AI" || f.ai_intensity === "Medium AI");
    
    // Create a set of AI feature IDs to prevent rendering the same feature twice
    const aiFeatureIds = new Set(aiFeatures.map(f => f.feature_id));
    const nonAiFeatures = filteredFeatures.filter(f => !aiFeatureIds.has(f.feature_id));

    if (loading && features.length === 0) {
        return (
            <PrismPage variant="dashboard" className="space-y-6 pb-8">
                <PrismSection className="space-y-6">
                    <div className="flex min-h-[400px] items-center justify-center">
                        <Loader2 className="w-8 h-8 animate-spin text-[var(--primary)]" />
                    </div>
                </PrismSection>
            </PrismPage>
        );
    }

    const FeatureCard = ({ feature }: { feature: FeatureFlag }) => {
        // Compute colors for AI Intensity badge
        let intensityColor = "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400";
        if (feature.ai_intensity === "Heavy AI") intensityColor = "bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-400";
        if (feature.ai_intensity === "Medium AI") intensityColor = "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-400";
        if (feature.ai_intensity === "Low AI") intensityColor = "bg-teal-100 text-teal-700 dark:bg-teal-900/40 dark:text-teal-400";

        return (
            <div className="flex items-center justify-between p-4 bg-[var(--bg-card)] border border-[var(--border)] rounded-[var(--radius)] hover:border-[var(--primary)]/30 transition-colors shadow-sm">
                <div className="flex-1 mr-4">
                    <div className="flex flex-wrap items-center gap-2 mb-2">
                        <h3 className="text-sm font-bold text-[var(--text-primary)]">{feature.name}</h3>
                        <span className="text-[10px] font-mono bg-[var(--bg-page)] text-[var(--text-muted)] px-2 py-0.5 rounded-full border border-[var(--border)]">
                            {feature.feature_id}
                        </span>
                        {feature.ai_intensity && (
                            <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full ${intensityColor}`}>
                                {feature.ai_intensity}
                            </span>
                        )}
                        {feature.module && (
                            <span className="text-[10px] bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 px-2 py-0.5 rounded-full border border-slate-200 dark:border-slate-700">
                                {feature.module}
                            </span>
                        )}
                    </div>
                    <p className="text-xs text-[var(--text-secondary)]">{feature.description}</p>
                </div>
                
                <div className="flex flex-col items-end gap-2 shrink-0">
                    <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-1 rounded-md ${
                        feature.enabled 
                            ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' 
                            : 'bg-red-500/10 text-red-600 dark:text-red-400'
                    }`}>
                        {feature.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                    
                    <button
                        onClick={() => handleToggle(feature.feature_id, feature.enabled)}
                        disabled={toggling === feature.feature_id || applyingProfile !== null}
                        className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:ring-offset-2 disabled:opacity-50 ${
                            feature.enabled ? 'bg-[var(--primary)]' : 'bg-[var(--border)]'
                        }`}
                    >
                        <span
                            className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                                feature.enabled ? 'translate-x-5' : 'translate-x-0'
                            }`}
                        >
                            {toggling === feature.feature_id && (
                                <Loader2 className="w-3 h-3 absolute top-1 left-1 animate-spin text-[var(--text-muted)]" />
                            )}
                        </span>
                    </button>
                </div>
            </div>
        );
    };

    return (
        <PrismPage variant="dashboard" className="max-w-6xl space-y-6 pb-12">
            <PrismSection className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <ShieldAlert className="h-3.5 w-3.5" />
                            Admin Feature Surface
                        </PrismHeroKicker>
                    )}
                    title="Control platform capabilities without losing operational clarity"
                    description="Search features, bulk-apply system profiles, and toggle AI or ERP modules from one global control layer."
                />
                
                <div>
                    
                </div>
                
                <div className="relative shrink-0">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
                    <input
                        type="text"
                        placeholder="Search IDs, Modules or Features..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full md:w-80 pl-9 pr-4 py-2 bg-[var(--bg-card)] border border-[var(--border)] rounded-[var(--radius)] text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--primary)] shadow-sm"
                    />
                </div>
            </div>

            {/* Quick Profiles Control Panel */}
            <div className="bg-[var(--primary)]/5 border border-[var(--primary)]/20 rounded-[var(--radius)] p-5">
                <h3 className="text-sm font-bold text-[var(--text-primary)] mb-3 flex items-center gap-2">
                    <Settings2 className="w-4 h-4 text-[var(--primary)]" />
                    Quick System Profiles
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <button 
                        onClick={() => handleApplyProfile("ai_tutor")}
                        disabled={applyingProfile !== null}
                        className="flex flex-col items-start p-4 bg-[var(--bg-card)] border border-[var(--border)] rounded-[var(--radius)] hover:border-purple-500/50 transition-colors text-left"
                    >
                        <div className="flex items-center gap-2 font-bold mb-1 text-purple-600 dark:text-purple-400">
                            <BookOpen className="w-4 h-4" /> AI Tutor Mode
                        </div>
                        <p className="text-xs text-[var(--text-secondary)]">Heavily activates Adaptive Learning & Heavy AI. Disables strict admin ERP functions.</p>
                        {applyingProfile === "ai_tutor" && <Loader2 className="w-4 h-4 animate-spin mt-2 text-[var(--text-muted)]" />}
                    </button>
                    
                    <button 
                        onClick={() => handleApplyProfile("ai_helper")}
                        disabled={applyingProfile !== null}
                        className="flex flex-col items-start p-4 bg-[var(--bg-card)] border border-[var(--border)] rounded-[var(--radius)] hover:border-blue-500/50 transition-colors text-left"
                    >
                        <div className="flex items-center gap-2 font-bold mb-1 text-blue-600 dark:text-blue-400">
                            <Zap className="w-4 h-4" /> AI Helper Mode
                        </div>
                        <p className="text-xs text-[var(--text-secondary)]">Balanced profile. Core ERP operational + Medium/Low AI Assistance enabled.</p>
                        {applyingProfile === "ai_helper" && <Loader2 className="w-4 h-4 animate-spin mt-2 text-[var(--text-muted)]" />}
                    </button>

                    <button 
                        onClick={() => handleApplyProfile("full_erp")}
                        disabled={applyingProfile !== null}
                        className="flex flex-col items-start p-4 bg-[var(--bg-card)] border border-[var(--border)] rounded-[var(--radius)] hover:border-emerald-500/50 transition-colors text-left"
                    >
                        <div className="flex items-center gap-2 font-bold mb-1 text-emerald-600 dark:text-emerald-400">
                            <ShieldAlert className="w-4 h-4" /> Full ERP Mode
                        </div>
                        <p className="text-xs text-[var(--text-secondary)]">Prioritizes 100% Administrative execution. Disables Heavy AI token consumption flows.</p>
                        {applyingProfile === "full_erp" && <Loader2 className="w-4 h-4 animate-spin mt-2 text-[var(--text-muted)]" />}
                    </button>
                </div>
            </div>

            <div className="grid lg:grid-cols-2 gap-8">
                {/* AI & Learning Features Section */}
                <div className="space-y-4">
                    <div className="flex items-center justify-between border-b border-[var(--border)] pb-2 mb-4 sticky top-0 bg-[var(--bg-page)] z-10 py-2">
                        <h2 className="text-lg font-bold text-[var(--text-primary)] flex items-center gap-2">
                            <span className="text-2xl">🤖</span> AI & Learning
                        </h2>
                        <span className="text-xs bg-[var(--primary)]/10 text-[var(--primary)] px-2 py-1 rounded-full font-medium">
                            {aiFeatures.filter(f => f.enabled).length} / {aiFeatures.length} Active
                        </span>
                    </div>
                    <div className="space-y-3">
                        {aiFeatures.length === 0 ? (
                            <p className="text-sm text-[var(--text-muted)] text-center py-8 bg-[var(--bg-card)] rounded-[var(--radius)] border border-[var(--border)]">No AI features found.</p>
                        ) : (
                            aiFeatures.map(f => <FeatureCard key={f.feature_id} feature={f} />)
                        )}
                    </div>
                </div>

                {/* ERP & Admin Features Section */}
                <div className="space-y-4">
                    <div className="flex items-center justify-between border-b border-[var(--border)] pb-2 mb-4 sticky top-0 bg-[var(--bg-page)] z-10 py-2">
                        <h2 className="text-lg font-bold text-[var(--text-primary)] flex items-center gap-2">
                            <span className="text-2xl">⚙️</span> Administrative ERP
                        </h2>
                        <span className="text-xs bg-[var(--primary)]/10 text-[var(--primary)] px-2 py-1 rounded-full font-medium">
                            {nonAiFeatures.filter(f => f.enabled).length} / {nonAiFeatures.length} Active
                        </span>
                    </div>
                    <div className="space-y-3">
                        {nonAiFeatures.length === 0 ? (
                            <p className="text-sm text-[var(--text-muted)] text-center py-8 bg-[var(--bg-card)] rounded-[var(--radius)] border border-[var(--border)]">No ERP features found.</p>
                        ) : (
                            nonAiFeatures.map(f => <FeatureCard key={f.feature_id} feature={f} />)
                        )}
                    </div>
                </div>
            </div>
            </PrismSection>
        </PrismPage>
    );
}
