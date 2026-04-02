"use client";

import { useEffect, useMemo, useState } from "react";
import { Search, Shield, UserX, Link2, Unlink, Users } from "lucide-react";

import { api } from "@/lib/api";

type UserRole = "student" | "teacher" | "admin" | "parent";

type UserItem = {
    id: string;
    name: string;
    email: string;
    role: UserRole;
    is_active: boolean;
    last_login: string | null;
    ai_queries_30d: number;
};

type ParentLinkItem = {
    id: string;
    parent_id: string;
    parent_name: string;
    child_id: string;
    child_name: string;
    created_at: string;
};

const roleColors: Record<string, string> = {
    student: "bg-indigo-500/10 text-indigo-500 border-indigo-500/20",
    teacher: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
    admin: "bg-fuchsia-500/10 text-fuchsia-500 border-fuchsia-500/20",
    parent: "bg-amber-500/10 text-amber-500 border-amber-500/20",
};

export default function UsersPage() {
    const [users, setUsers] = useState<UserItem[]>([]);
    const [links, setLinks] = useState<ParentLinkItem[]>([]);
    const [search, setSearch] = useState("");
    const [roleFilter, setRoleFilter] = useState("all");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [actionUserId, setActionUserId] = useState<string | null>(null);
    const [selectedParentId, setSelectedParentId] = useState("");
    const [selectedChildId, setSelectedChildId] = useState("");
    const [linkBusy, setLinkBusy] = useState(false);

    const loadData = async () => {
        const [usersData, linksData] = await Promise.all([
            api.admin.users(),
            api.admin.parentLinks(),
        ]);
        setUsers((usersData || []) as UserItem[]);
        setLinks((linksData || []) as ParentLinkItem[]);
    };

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                await loadData();
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load users");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    const parents = useMemo(
        () => users.filter((u) => u.role === "parent" && u.is_active),
        [users],
    );
    const students = useMemo(
        () => users.filter((u) => u.role === "student" && u.is_active),
        [users],
    );

    useEffect(() => {
        if (!parents.some((p) => p.id === selectedParentId)) {
            setSelectedParentId(parents[0]?.id || "");
        }
        if (!students.some((s) => s.id === selectedChildId)) {
            setSelectedChildId(students[0]?.id || "");
        }
    }, [parents, students, selectedParentId, selectedChildId]);

    const filtered = useMemo(() => {
        return users.filter((u) => {
            const matchesSearch =
                u.name.toLowerCase().includes(search.toLowerCase()) ||
                u.email.toLowerCase().includes(search.toLowerCase());
            const matchesRole = roleFilter === "all" || u.role === roleFilter;
            return matchesSearch && matchesRole;
        });
    }, [users, search, roleFilter]);

    const handleRoleChange = async (user: UserItem, nextRole: UserRole) => {
        if (nextRole === user.role) return;
        try {
            setActionUserId(user.id);
            setError(null);
            await api.admin.changeUserRole(user.id, nextRole);
            await loadData();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to update role");
        } finally {
            setActionUserId(null);
        }
    };

    const handleToggleActive = async (userId: string) => {
        try {
            setActionUserId(userId);
            setError(null);
            await api.admin.toggleUserActive(userId);
            await loadData();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to update user");
        } finally {
            setActionUserId(null);
        }
    };

    const handleCreateParentLink = async () => {
        if (!selectedParentId || !selectedChildId) return;
        try {
            setLinkBusy(true);
            setError(null);
            await api.admin.createParentLink({
                parent_id: selectedParentId,
                child_id: selectedChildId,
            });
            await loadData();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to create parent link");
        } finally {
            setLinkBusy(false);
        }
    };

    const handleDeleteParentLink = async (id: string) => {
        try {
            setLinkBusy(true);
            setError(null);
            await api.admin.deleteParentLink(id);
            await loadData();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to delete parent link");
        } finally {
            setLinkBusy(false);
        }
    };

    const formatDateTime = (value: string | null) => {
        if (!value) return "-";
        const parsed = new Date(value);
        return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
    };

    return (
        <div className="relative max-w-7xl mx-auto py-8">
            <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-gradient-to-bl from-purple-500/10 to-transparent blur-[120px] -z-10 rounded-full pointer-events-none" />
            
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10 stagger-1">
                <div>
                    <div className="inline-flex items-center gap-2 px-3 py-1 mb-4 rounded-full glass-panel border-[var(--border)] text-[var(--text-secondary)] text-sm font-medium shadow-sm">
                        <Users className="w-4 h-4 text-[var(--primary)]" />
                        Directory Service
                    </div>
                    <h1 className="text-3xl md:text-5xl font-extrabold text-[var(--text-primary)] tracking-tight">
                        User <span className="premium-gradient">Management</span>
                    </h1>
                    <p className="text-sm font-bold text-[var(--text-secondary)] mt-4 tracking-wider uppercase">
                        {users.length} Active Nodes
                    </p>
                </div>

                <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
                    <div className="relative flex-1 sm:w-64 group">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)] group-focus-within:text-[var(--primary)] transition-colors" />
                        <input
                            type="text"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            placeholder="Query directory..."
                            className="w-full pl-11 pr-4 py-3 text-sm bg-[var(--bg-page)]/50 backdrop-blur-md border border-[var(--border-strong)] rounded-full focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent transition-all shadow-inner placeholder:text-[var(--text-muted)] font-medium text-[var(--text-primary)]"
                        />
                    </div>
                    
                    <div className="flex border border-[var(--border-strong)] rounded-full bg-[var(--bg-page)]/30 backdrop-blur-md p-1 shadow-inner overflow-hidden max-w-full overflow-x-auto">
                        {["all", "student", "teacher", "admin", "parent"].map((r) => (
                            <button
                                key={r}
                                onClick={() => setRoleFilter(r)}
                                className={`px-4 py-2 text-xs font-bold rounded-full capitalize transition-all whitespace-nowrap ${
                                    roleFilter === r
                                        ? "bg-gradient-to-r from-indigo-500 to-cyan-500 text-white shadow-md shadow-indigo-500/30 scale-105"
                                        : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--text-primary)]/5"
                                }`}
                            >
                                {r}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {error ? (
                <div className="rounded-2xl border border-[var(--error)]/30 bg-[var(--error)]/5 backdrop-blur-md px-5 py-4 text-sm font-semibold text-[var(--error)] mb-8 flex items-center gap-3 shadow-lg stagger-2">
                    <Shield className="w-5 h-5 shrink-0" />
                    {error}
                </div>
            ) : null}

            <div className="grid lg:grid-cols-4 gap-8 stagger-3">
                {/* Main Directory Table */}
                <div className="lg:col-span-3">
                    <div className="glass-panel border-t border-l border-[var(--border-strong)] rounded-3xl shadow-2xl relative overflow-hidden group">
                        <div className="absolute inset-0 bg-gradient-to-br from-[var(--bg-card)]/40 to-transparent -z-10" />
                        
                        <div className="overflow-x-auto">
                            <table className="w-full min-w-[800px] border-collapse">
                                <thead>
                                    <tr className="bg-[var(--bg-page)]/80 backdrop-blur-xl border-b border-[var(--border-strong)] text-left z-10 sticky top-0">
                                        <th className="px-6 py-5 text-[10px] sm:text-xs font-black text-[var(--text-muted)] uppercase tracking-wider">Identity</th>
                                        <th className="px-6 py-5 text-[10px] sm:text-xs font-black text-[var(--text-muted)] uppercase tracking-wider">Access Tier</th>
                                        <th className="px-6 py-5 text-[10px] sm:text-xs font-black text-[var(--text-muted)] uppercase tracking-wider">Status Node</th>
                                        <th className="px-6 py-5 text-[10px] sm:text-xs font-black text-[var(--text-muted)] uppercase tracking-wider">Last Sync</th>
                                        <th className="px-6 py-5 text-[10px] sm:text-xs font-black text-[var(--text-muted)] uppercase tracking-wider">AI Load (30d)</th>
                                        <th className="px-6 py-5 text-[10px] sm:text-xs font-black text-[var(--text-muted)] uppercase tracking-wider text-right">Overrides</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {loading ? (
                                        <tr>
                                            <td className="px-6 py-12 text-sm font-semibold text-[var(--text-muted)] text-center animate-pulse" colSpan={6}>
                                                Connecting to Directory Service...
                                            </td>
                                        </tr>
                                    ) : filtered.length === 0 ? (
                                        <tr>
                                            <td className="px-6 py-12 text-sm font-semibold text-[var(--text-muted)] text-center" colSpan={6}>
                                                No identities match the query parameters.
                                            </td>
                                        </tr>
                                    ) : filtered.map((user, idx) => (
                                        <tr key={user.id} className={`border-b border-[var(--border-light)]/50 transition-colors duration-300 hover:bg-[var(--bg-page)] ${actionUserId === user.id ? 'opacity-50 pointer-events-none' : ''}`}>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-4">
                                                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[var(--bg-card)] to-[var(--bg-page)] border border-[var(--border)] flex items-center justify-center font-bold text-[var(--text-primary)] shadow-inner">
                                                        {user.name.charAt(0).toUpperCase()}
                                                    </div>
                                                    <div>
                                                        <p className="text-sm font-bold text-[var(--text-primary)]">{user.name}</p>
                                                        <p className="text-xs font-medium text-[var(--text-secondary)]">{user.email}</p>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className={`inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold border capitalize ${roleColors[user.role]}`}>
                                                    {user.role}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className={`flex items-center gap-2 text-xs font-bold px-3 py-1.5 rounded-full w-max border ${user.is_active ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.1)]" : "bg-red-500/10 text-red-500 border-red-500/20"}`}>
                                                    <span className={`w-1.5 h-1.5 rounded-full ${user.is_active ? "bg-emerald-500 animate-pulse" : "bg-red-500"}`} />
                                                    {user.is_active ? "Online " : "Disabled"}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 text-xs font-mono font-medium text-[var(--text-secondary)]">
                                                {formatDateTime(user.last_login)}
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-16 h-1.5 rounded-full bg-[var(--bg-page)] overflow-hidden">
                                                        <div 
                                                            className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full" 
                                                            style={{ width: `${Math.min(100, (user.ai_queries_30d / 50) * 100)}%` }}
                                                        />
                                                    </div>
                                                    <span className="text-xs font-black text-[var(--text-primary)]">{user.ai_queries_30d}</span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <div className="flex items-center justify-end gap-2">
                                                    <select
                                                        value={user.role}
                                                        onChange={(e) => void handleRoleChange(user, e.target.value as UserRole)}
                                                        className="px-3 py-1.5 text-xs font-bold border border-[var(--border-strong)] rounded-lg bg-[var(--bg-page)]/50 focus:outline-none focus:border-[var(--primary)] text-[var(--text-secondary)] appearance-none cursor-pointer hover:bg-[var(--bg-card)] transition-colors"
                                                        style={{ backgroundImage: 'url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%239CA3AF%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E")', backgroundRepeat: 'no-repeat', backgroundPosition: 'right 0.5rem top 50%', backgroundSize: '0.5rem auto', paddingRight: '1.5rem' }}
                                                    >
                                                        <option value="student">Student</option>
                                                        <option value="teacher">Teacher</option>
                                                        <option value="parent">Parent</option>
                                                        <option value="admin">Admin</option>
                                                    </select>
                                                    
                                                    <button
                                                        className={`p-1.5 rounded-lg border transition-all ${user.is_active ? 'border-[var(--border)] text-[var(--text-muted)] hover:border-red-500 hover:text-red-500 hover:bg-red-500/10' : 'border-emerald-500/30 text-emerald-500 hover:bg-emerald-500 hover:text-white'}`}
                                                        title={user.is_active ? "Terminate Access" : "Restore Access"}
                                                        onClick={() => void handleToggleActive(user.id)}
                                                    >
                                                        <UserX className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                {/* Sidebar: Parent-Child Linker */}
                <div className="lg:col-span-1 space-y-6">
                    <div className="glass-panel border-t border-l border-[var(--border-strong)] rounded-3xl p-6 shadow-xl relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/10 blur-[50px] rounded-full pointer-events-none group-hover:bg-amber-500/20 transition-colors duration-700" />
                        
                        <h2 className="text-sm font-bold text-[var(--text-primary)] mb-5 flex items-center gap-2">
                            <Link2 className="w-4 h-4 text-amber-500" />
                            Guardian Network
                        </h2>

                        <div className="space-y-4 mb-6">
                            <div>
                                <label className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)] block mb-1">Guardian Node</label>
                                <select
                                    value={selectedParentId}
                                    onChange={(e) => setSelectedParentId(e.target.value)}
                                    className="w-full px-4 py-2.5 text-sm bg-[var(--bg-page)]/50 border border-[var(--border-strong)] rounded-xl focus:outline-none focus:ring-1 focus:ring-amber-500 font-medium text-[var(--text-primary)] shadow-inner appearance-none truncate"
                                    disabled={linkBusy || parents.length === 0}
                                    style={{ backgroundImage: 'url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%239CA3AF%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E")', backgroundRepeat: 'no-repeat', backgroundPosition: 'right 0.75rem top 50%', backgroundSize: '0.65rem auto', paddingRight: '2rem' }}
                                >
                                    {parents.length === 0 ? (
                                        <option value="">No Guardian Logs</option>
                                    ) : (
                                        parents.map((p) => (
                                            <option key={p.id} value={p.id}>{p.name}</option>
                                        ))
                                    )}
                                </select>
                            </div>
                            
                            <div className="flex justify-center -my-2 relative z-10">
                                <div className="w-6 h-6 rounded-full bg-[var(--bg-card)] border border-[var(--border)] flex items-center justify-center shadow-sm">
                                    <ArrowDown className="w-3 h-3 text-[var(--text-muted)]" />
                                </div>
                            </div>
                            
                            <div>
                                <label className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)] block mb-1">Student Node</label>
                                <select
                                    value={selectedChildId}
                                    onChange={(e) => setSelectedChildId(e.target.value)}
                                    className="w-full px-4 py-2.5 text-sm bg-[var(--bg-page)]/50 border border-[var(--border-strong)] rounded-xl focus:outline-none focus:ring-1 focus:ring-amber-500 font-medium text-[var(--text-primary)] shadow-inner appearance-none truncate"
                                    disabled={linkBusy || students.length === 0}
                                    style={{ backgroundImage: 'url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%239CA3AF%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E")', backgroundRepeat: 'no-repeat', backgroundPosition: 'right 0.75rem top 50%', backgroundSize: '0.65rem auto', paddingRight: '2rem' }}
                                >
                                    {students.length === 0 ? (
                                        <option value="">No Student Logs</option>
                                    ) : (
                                        students.map((s) => (
                                            <option key={s.id} value={s.id}>{s.name}</option>
                                        ))
                                    )}
                                </select>
                            </div>
                            
                            <button
                                onClick={() => void handleCreateParentLink()}
                                className="w-full mt-2 px-4 py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 text-white text-sm font-bold rounded-xl hover:shadow-[0_0_15px_rgba(245,158,11,0.4)] transition-all hover:scale-[1.02] flex items-center justify-center gap-2 disabled:opacity-50 disabled:pointer-events-none"
                                disabled={linkBusy || !selectedParentId || !selectedChildId}
                            >
                                <Link2 className="w-4 h-4" />
                                Initiate Binding
                            </button>
                        </div>
                    </div>
                    
                    {/* Bound Links Registry */}
                    <div className="glass-panel border-t border-l border-[var(--border-strong)] rounded-3xl p-6 shadow-xl relative overflow-hidden">
                        <div className="absolute inset-0 bg-[var(--bg-card)]/50 backdrop-blur-md -z-10" />
                        <h3 className="text-xs font-black tracking-wider text-[var(--text-muted)] uppercase mb-4">Active Bindings Registry</h3>
                        
                        {links.length === 0 ? (
                            <div className="py-6 border-2 border-dashed border-[var(--border)] rounded-2xl flex flex-col items-center justify-center text-center">
                                <Unlink className="w-6 h-6 text-[var(--border-strong)] mb-2" />
                                <p className="text-xs font-semibold text-[var(--text-muted)]">Matrix Empty.</p>
                            </div>
                        ) : (
                            <div className="space-y-3 max-h-[300px] overflow-y-auto pr-1">
                                {links.map((link) => (
                                    <div key={link.id} className="p-3.5 rounded-2xl bg-[var(--bg-page)]/70 border border-[var(--border-strong)] flex flex-col gap-2 shadow-inner group transition-colors hover:border-red-500/30 hover:bg-red-500/5">
                                        <div className="flex items-start justify-between">
                                            <div>
                                                <p className="text-xs font-bold text-[var(--text-primary)] leading-tight">{link.parent_name}</p>
                                                <div className="flex items-center gap-1.5 mt-1 opacity-70">
                                                    <ArrowDown className="w-2.5 h-2.5 text-[var(--text-secondary)]" />
                                                    <p className="text-xs font-bold premium-text">{link.child_name}</p>
                                                </div>
                                            </div>
                                            <button
                                                onClick={() => void handleDeleteParentLink(link.id)}
                                                className="p-1.5 rounded bg-[var(--bg-card)] border border-[var(--border)] text-[var(--text-muted)] hover:bg-red-500 hover:text-white hover:border-red-500 transition-all shadow-sm opacity-50 group-hover:opacity-100"
                                                disabled={linkBusy}
                                                title="Sever Binding"
                                            >
                                                <Unlink className="w-3.5 h-3.5" />
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

// Inline helper for arrow down icon
function ArrowDown(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg 
      {...props} 
      xmlns="http://www.w3.org/2000/svg" 
      width="24" 
      height="24" 
      viewBox="0 0 24 24" 
      fill="none" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    >
      <path d="M12 5v14"/>
      <path d="m19 12-7 7-7-7"/>
    </svg>
  );
}
