"use client";

import { useEffect, useMemo, useState } from "react";
import { Search, Shield, UserX, Link2, Unlink } from "lucide-react";

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
    student: "bg-blue-50 text-[var(--primary)]",
    teacher: "bg-green-50 text-[var(--success)]",
    admin: "bg-purple-50 text-purple-700",
    parent: "bg-orange-50 text-orange-700",
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
        <div>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-[var(--text-primary)]">User Management</h1>
                    <p className="text-sm text-[var(--text-secondary)]">{users.length} total users</p>
                </div>
            </div>

            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)] mb-4">
                    {error}
                </div>
            ) : null}

            <div className="flex gap-3 mb-4">
                <div className="relative flex-1 max-w-xs">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
                    <input
                        type="text"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search users..."
                        className="w-full pl-10 pr-4 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                    />
                </div>
                {["all", "student", "teacher", "admin", "parent"].map((r) => (
                    <button
                        key={r}
                        onClick={() => setRoleFilter(r)}
                        className={`px-3 py-2 text-xs font-medium rounded-[var(--radius-sm)] capitalize transition-colors ${roleFilter === r
                                ? "bg-[var(--primary)] text-white"
                                : "bg-white border border-[var(--border)] text-[var(--text-secondary)] hover:border-[var(--primary)]"
                            }`}
                    >
                        {r}
                    </button>
                ))}
            </div>

            <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] overflow-hidden">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-[var(--border)]">
                            <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">User</th>
                            <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">Role</th>
                            <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">Status</th>
                            <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">Last Login</th>
                            <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">AI (30d)</th>
                            <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr>
                                <td className="px-5 py-6 text-sm text-[var(--text-muted)]" colSpan={6}>
                                    Loading users...
                                </td>
                            </tr>
                        ) : filtered.length === 0 ? (
                            <tr>
                                <td className="px-5 py-6 text-sm text-[var(--text-muted)]" colSpan={6}>
                                    No users found.
                                </td>
                            </tr>
                        ) : filtered.map((user) => (
                            <tr key={user.id} className="border-b border-[var(--border-light)] hover:bg-[var(--bg-page)] transition-colors">
                                <td className="px-5 py-3">
                                    <p className="text-sm font-medium text-[var(--text-primary)]">{user.name}</p>
                                    <p className="text-xs text-[var(--text-muted)]">{user.email}</p>
                                </td>
                                <td className="px-5 py-3">
                                    <span className={`text-xs font-medium px-2.5 py-1 rounded-full capitalize ${roleColors[user.role]}`}>
                                        {user.role}
                                    </span>
                                </td>
                                <td className="px-5 py-3">
                                    <span className={`flex items-center gap-1.5 text-xs ${user.is_active ? "text-[var(--success)]" : "text-[var(--error)]"}`}>
                                        <span className={`w-1.5 h-1.5 rounded-full ${user.is_active ? "bg-[var(--success)]" : "bg-[var(--error)]"}`} />
                                        {user.is_active ? "Active" : "Inactive"}
                                    </span>
                                </td>
                                <td className="px-5 py-3 text-sm text-[var(--text-secondary)]">
                                    {formatDateTime(user.last_login)}
                                </td>
                                <td className="px-5 py-3 text-sm text-[var(--text-primary)] font-medium">{user.ai_queries_30d}</td>
                                <td className="px-5 py-3">
                                    <div className="flex items-center gap-2">
                                        <div className="flex items-center gap-1">
                                            <Shield className="w-4 h-4 text-[var(--text-muted)]" />
                                            <select
                                                value={user.role}
                                                onChange={(e) => void handleRoleChange(user, e.target.value as UserRole)}
                                                className="px-2 py-1 text-xs border border-[var(--border)] rounded"
                                                disabled={actionUserId === user.id}
                                            >
                                                <option value="student">student</option>
                                                <option value="teacher">teacher</option>
                                                <option value="admin">admin</option>
                                                <option value="parent">parent</option>
                                            </select>
                                        </div>
                                        <button
                                            className="p-1.5 text-[var(--text-muted)] hover:text-[var(--error)] transition-colors"
                                            title={user.is_active ? "Deactivate" : "Activate"}
                                            onClick={() => void handleToggleActive(user.id)}
                                            disabled={actionUserId === user.id}
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

            <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5 mt-6">
                <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">Parent-Child Links</h2>

                <div className="grid md:grid-cols-[1fr_1fr_auto] gap-3 mb-4">
                    <select
                        value={selectedParentId}
                        onChange={(e) => setSelectedParentId(e.target.value)}
                        className="px-3 py-2.5 border border-[var(--border)] rounded-[var(--radius-sm)] text-sm"
                        disabled={linkBusy || parents.length === 0}
                    >
                        {parents.length === 0 ? (
                            <option value="">No parent users available</option>
                        ) : (
                            parents.map((p) => (
                                <option key={p.id} value={p.id}>{p.name} ({p.email})</option>
                            ))
                        )}
                    </select>
                    <select
                        value={selectedChildId}
                        onChange={(e) => setSelectedChildId(e.target.value)}
                        className="px-3 py-2.5 border border-[var(--border)] rounded-[var(--radius-sm)] text-sm"
                        disabled={linkBusy || students.length === 0}
                    >
                        {students.length === 0 ? (
                            <option value="">No student users available</option>
                        ) : (
                            students.map((s) => (
                                <option key={s.id} value={s.id}>{s.name} ({s.email})</option>
                            ))
                        )}
                    </select>
                    <button
                        onClick={() => void handleCreateParentLink()}
                        className="px-4 py-2.5 bg-[var(--primary)] text-white text-sm font-medium rounded-[var(--radius-sm)] hover:bg-[var(--primary-hover)] transition-colors flex items-center gap-2"
                        disabled={linkBusy || !selectedParentId || !selectedChildId}
                    >
                        <Link2 className="w-4 h-4" />
                        Link
                    </button>
                </div>

                {links.length === 0 ? (
                    <p className="text-sm text-[var(--text-muted)]">No parent-child links configured yet.</p>
                ) : (
                    <div className="space-y-2">
                        {links.map((link) => (
                            <div key={link.id} className="p-3 rounded-[var(--radius-sm)] border border-[var(--border)] flex items-center justify-between gap-3">
                                <div>
                                    <p className="text-sm font-medium text-[var(--text-primary)]">
                                        {link.parent_name}{" -> "}{link.child_name}
                                    </p>
                                    <p className="text-xs text-[var(--text-muted)]">Created: {formatDateTime(link.created_at)}</p>
                                </div>
                                <button
                                    onClick={() => void handleDeleteParentLink(link.id)}
                                    className="px-3 py-1.5 text-xs rounded bg-red-50 text-[var(--error)] flex items-center gap-1"
                                    disabled={linkBusy}
                                >
                                    <Unlink className="w-3.5 h-3.5" />
                                    Unlink
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
