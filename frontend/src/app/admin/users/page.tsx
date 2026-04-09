"use client";

import { useEffect, useMemo, useState } from "react";
import {
    Link2,
    Loader2,
    Shield,
    Unlink,
    UserX,
    Users,
} from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismSearchField, PrismSelect, PrismTableShell, PrismToolbar } from "@/components/prism/PrismControls";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
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

const roleColors: Record<UserRole, string> = {
    student: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
    teacher: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    admin: "bg-fuchsia-500/10 text-fuchsia-400 border-fuchsia-500/20",
    parent: "bg-amber-500/10 text-amber-400 border-amber-500/20",
};

const roleOptions: Array<UserRole | "all"> = ["all", "student", "teacher", "admin", "parent"];

function formatDateTime(value: string | null) {
    if (!value) return "-";
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

export default function UsersPage() {
    const [users, setUsers] = useState<UserItem[]>([]);
    const [links, setLinks] = useState<ParentLinkItem[]>([]);
    const [search, setSearch] = useState("");
    const [roleFilter, setRoleFilter] = useState<UserRole | "all">("all");
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
            } catch (loadError) {
                setError(loadError instanceof Error ? loadError.message : "Failed to load users");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    const parents = useMemo(() => users.filter((user) => user.role === "parent" && user.is_active), [users]);
    const students = useMemo(() => users.filter((user) => user.role === "student" && user.is_active), [users]);

    useEffect(() => {
        if (!parents.some((parent) => parent.id === selectedParentId)) {
            setSelectedParentId(parents[0]?.id || "");
        }
        if (!students.some((student) => student.id === selectedChildId)) {
            setSelectedChildId(students[0]?.id || "");
        }
    }, [parents, students, selectedParentId, selectedChildId]);

    const filtered = useMemo(() => {
        return users.filter((user) => {
            const query = search.trim().toLowerCase();
            const matchesSearch =
                query.length === 0 ||
                user.name.toLowerCase().includes(query) ||
                user.email.toLowerCase().includes(query);
            const matchesRole = roleFilter === "all" || user.role === roleFilter;
            return matchesSearch && matchesRole;
        });
    }, [roleFilter, search, users]);

    const activeUsers = useMemo(() => users.filter((user) => user.is_active).length, [users]);
    const adminUsers = useMemo(() => users.filter((user) => user.role === "admin").length, [users]);

    const handleRoleChange = async (user: UserItem, nextRole: UserRole) => {
        if (nextRole === user.role) return;
        try {
            setActionUserId(user.id);
            setError(null);
            await api.admin.changeUserRole(user.id, nextRole);
            await loadData();
        } catch (changeError) {
            setError(changeError instanceof Error ? changeError.message : "Failed to update role");
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
        } catch (toggleError) {
            setError(toggleError instanceof Error ? toggleError.message : "Failed to update user");
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
        } catch (linkError) {
            setError(linkError instanceof Error ? linkError.message : "Failed to create parent link");
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
        } catch (deleteError) {
            setError(deleteError instanceof Error ? deleteError.message : "Failed to delete parent link");
        } finally {
            setLinkBusy(false);
        }
    };

    return (
        <PrismPage variant="dashboard" className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <Users className="h-3.5 w-3.5" />
                            Admin Directory Surface
                        </PrismHeroKicker>
                    )}
                    title="Govern the school directory without leaving the control room"
                    description="Search identities, apply role and activation overrides, and manage guardian bindings from one operational admin workspace."
                    aside={(
                        <div className="prism-briefing-panel">
                            <p className="prism-status-label">Directory rule</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                Treat role changes and disable actions as operational controls. Use guardian bindings only for active parent and student accounts.
                            </p>
                        </div>
                    )}
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Directory size</span>
                        <span className="prism-status-value">{users.length}</span>
                        <span className="prism-status-detail">Total identities currently tracked in the admin directory.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Active users</span>
                        <span className="prism-status-value">{activeUsers}</span>
                        <span className="prism-status-detail">{adminUsers} admin accounts and {links.length} active guardian bindings.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Filtered view</span>
                        <span className="prism-status-value">{filtered.length}</span>
                        <span className="prism-status-detail">
                            {roleFilter === "all" ? "All roles are visible in the current result set." : `Filtered to ${roleFilter} identities.`}
                        </span>
                    </div>
                </div>

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="admin-users"
                        onRetry={() => {
                            void loadData();
                        }}
                    />
                ) : null}

                <div className="grid gap-6 xl:grid-cols-[minmax(0,1.12fr)_minmax(340px,0.88fr)]">
                    <div className="space-y-6 min-w-0">
                        <PrismPanel className="p-5">
                            <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
                                <div>
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">User directory</h2>
                                    <p className="text-sm text-[var(--text-secondary)]">
                                        Search, filter, and apply role or activation overrides without leaving the directory surface.
                                    </p>
                                </div>
                                <PrismToolbar className="w-full lg:w-auto">
                                    <PrismSearchField
                                        value={search}
                                        onChange={(event) => setSearch(event.target.value)}
                                        placeholder="Search users"
                                        className="flex-1 sm:min-w-[260px]"
                                        aria-label="Search users"
                                    />
                                    <PrismSelect
                                        value={roleFilter}
                                        onChange={(event) => setRoleFilter(event.target.value as UserRole | "all")}
                                        className="sm:w-[180px]"
                                        aria-label="Filter users by role"
                                    >
                                        {roleOptions.map((role) => (
                                            <option key={role} value={role}>
                                                {role}
                                            </option>
                                        ))}
                                    </PrismSelect>
                                </PrismToolbar>
                            </div>

                            {loading ? (
                                <div className="mt-4 flex items-center gap-2 text-sm text-[var(--text-muted)]">
                                    <Loader2 className="h-4 w-4 animate-spin" /> Loading directory...
                                </div>
                            ) : filtered.length === 0 ? (
                                <div className="mt-4">
                                    <EmptyState
                                        icon={Users}
                                        title="No identities match the current filters"
                                        description="Adjust the search query or role filter to bring users back into view."
                                        eyebrow="No directory matches"
                                        scopeNote="The directory view supports role filtering and free-text matching across name and email."
                                    />
                                </div>
                            ) : (
                                <PrismTableShell className="mt-4">
                                    <table className="prism-table min-w-full">
                                        <thead>
                                            <tr>
                                                <th>Identity</th>
                                                <th>Role</th>
                                                <th>Status</th>
                                                <th>Last login</th>
                                                <th>AI load</th>
                                                <th className="text-right">Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {filtered.map((user) => (
                                                <tr key={user.id} className={actionUserId === user.id ? "opacity-60" : ""}>
                                                    <td>
                                                        <div className="flex items-center gap-3">
                                                            <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.04)] font-semibold text-[var(--text-primary)]">
                                                                {user.name.charAt(0).toUpperCase()}
                                                            </div>
                                                            <div>
                                                                <p className="font-medium text-[var(--text-primary)]">{user.name}</p>
                                                                <p className="text-xs text-[var(--text-secondary)]">{user.email}</p>
                                                            </div>
                                                        </div>
                                                    </td>
                                                    <td>
                                                        <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold capitalize ${roleColors[user.role]}`}>
                                                            {user.role}
                                                        </span>
                                                    </td>
                                                    <td>
                                                        <span className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold ${user.is_active ? "border-emerald-500/20 bg-emerald-500/10 text-emerald-400" : "border-red-500/20 bg-red-500/10 text-red-400"}`}>
                                                            <span className={`h-1.5 w-1.5 rounded-full ${user.is_active ? "bg-emerald-400" : "bg-red-400"}`} />
                                                            {user.is_active ? "Active" : "Disabled"}
                                                        </span>
                                                    </td>
                                                    <td className="text-xs text-[var(--text-secondary)]">
                                                        {formatDateTime(user.last_login)}
                                                    </td>
                                                    <td>
                                                        <div className="flex items-center gap-2">
                                                            <div className="h-1.5 w-16 overflow-hidden rounded-full bg-[var(--bg-page)]">
                                                                <div
                                                                    className="h-full rounded-full bg-[linear-gradient(90deg,rgba(96,165,250,0.95),rgba(45,212,191,0.9))]"
                                                                    style={{ width: `${Math.min(100, (user.ai_queries_30d / 50) * 100)}%` }}
                                                                />
                                                            </div>
                                                            <span className="text-xs font-semibold text-[var(--text-primary)]">{user.ai_queries_30d}</span>
                                                        </div>
                                                    </td>
                                                    <td className="text-right">
                                                        <div className="flex flex-wrap items-center justify-end gap-2">
                                                            <PrismSelect
                                                                value={user.role}
                                                                onChange={(event) => void handleRoleChange(user, event.target.value as UserRole)}
                                                                className="min-h-[2.5rem] w-auto px-3 py-2 text-xs font-medium"
                                                                aria-label={`Change role for ${user.name}`}
                                                                disabled={actionUserId === user.id}
                                                            >
                                                                <option value="student">Student</option>
                                                                <option value="teacher">Teacher</option>
                                                                <option value="parent">Parent</option>
                                                                <option value="admin">Admin</option>
                                                            </PrismSelect>
                                                            <button
                                                                type="button"
                                                                onClick={() => void handleToggleActive(user.id)}
                                                                className={`inline-flex items-center gap-2 rounded-xl border px-3 py-2 text-xs font-medium transition ${user.is_active ? "border-red-500/20 bg-red-500/10 text-red-400 hover:bg-red-500/15" : "border-emerald-500/20 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/15"}`}
                                                                aria-label={user.is_active ? `Disable ${user.name}` : `Enable ${user.name}`}
                                                                disabled={actionUserId === user.id}
                                                            >
                                                                <UserX className="h-3.5 w-3.5" />
                                                                {user.is_active ? "Disable" : "Enable"}
                                                            </button>
                                                        </div>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </PrismTableShell>
                            )}
                        </PrismPanel>
                    </div>

                    <div className="space-y-6 min-w-0">
                        <PrismPanel className="p-5 xl:sticky xl:top-6">
                            <div className="flex items-center gap-2">
                                <Link2 className="h-4 w-4 text-[var(--primary)]" />
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">Guardian network</h2>
                            </div>
                            <p className="mt-2 text-sm text-[var(--text-secondary)]">
                                Link active parents to active students to keep reporting and guardian access aligned.
                            </p>

                            <div className="mt-4 space-y-4">
                                <div>
                                    <label htmlFor="guardian-parent" className="mb-2 block text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                                        Guardian
                                    </label>
                                    <PrismSelect
                                        id="guardian-parent"
                                        value={selectedParentId}
                                        onChange={(event) => setSelectedParentId(event.target.value)}
                                        disabled={linkBusy || parents.length === 0}
                                    >
                                        {parents.length === 0 ? (
                                            <option value="">No active guardians</option>
                                        ) : parents.map((parent) => (
                                            <option key={parent.id} value={parent.id}>
                                                {parent.name}
                                            </option>
                                        ))}
                                    </PrismSelect>
                                </div>

                                <div>
                                    <label htmlFor="guardian-student" className="mb-2 block text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                                        Student
                                    </label>
                                    <PrismSelect
                                        id="guardian-student"
                                        value={selectedChildId}
                                        onChange={(event) => setSelectedChildId(event.target.value)}
                                        disabled={linkBusy || students.length === 0}
                                    >
                                        {students.length === 0 ? (
                                            <option value="">No active students</option>
                                        ) : students.map((student) => (
                                            <option key={student.id} value={student.id}>
                                                {student.name}
                                            </option>
                                        ))}
                                    </PrismSelect>
                                </div>

                                <button
                                    type="button"
                                    onClick={() => void handleCreateParentLink()}
                                    className="prism-action inline-flex w-full items-center justify-center gap-2 !bg-[linear-gradient(135deg,rgba(245,158,11,0.95),rgba(249,115,22,0.92))] !text-white !shadow-[0_18px_34px_rgba(245,158,11,0.22)] disabled:cursor-not-allowed disabled:opacity-60"
                                    disabled={linkBusy || !selectedParentId || !selectedChildId}
                                >
                                    <Link2 className="h-4 w-4" />
                                    Create guardian binding
                                </button>
                            </div>
                        </PrismPanel>

                        <PrismPanel className="p-5">
                            <div className="flex items-center gap-2">
                                <Shield className="h-4 w-4 text-[var(--primary)]" />
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">Active bindings registry</h2>
                            </div>
                            <p className="mt-2 text-sm text-[var(--text-secondary)]">
                                Current parent-child bindings remain editable here without changing the underlying user directory data.
                            </p>

                            <div className="mt-4 space-y-3">
                                {links.length === 0 ? (
                                    <EmptyState
                                        icon={Unlink}
                                        title="No guardian bindings yet"
                                        description="Create the first parent-child link from the panel above."
                                        eyebrow="Guardian network empty"
                                        scopeNote="Only active parent and student identities appear in the binding workflow."
                                    />
                                ) : links.map((link) => (
                                    <div key={link.id} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                        <div className="flex items-start justify-between gap-3">
                                            <div>
                                                <p className="text-sm font-semibold text-[var(--text-primary)]">{link.parent_name}</p>
                                                <p className="mt-1 text-xs text-[var(--text-secondary)]">Linked to {link.child_name}</p>
                                                <p className="mt-2 text-[11px] uppercase tracking-[0.16em] text-[var(--text-muted)]">
                                                    {formatDateTime(link.created_at)}
                                                </p>
                                            </div>
                                            <button
                                                type="button"
                                                onClick={() => void handleDeleteParentLink(link.id)}
                                                className="inline-flex items-center gap-2 rounded-xl border border-red-500/20 bg-red-500/10 px-3 py-2 text-xs font-medium text-red-400 transition hover:bg-red-500/15 disabled:cursor-not-allowed disabled:opacity-60"
                                                aria-label={`Delete link for ${link.parent_name} and ${link.child_name}`}
                                                disabled={linkBusy}
                                            >
                                                <Unlink className="h-3.5 w-3.5" />
                                                Remove
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </PrismPanel>
                    </div>
                </div>
            </PrismSection>
        </PrismPage>
    );
}
