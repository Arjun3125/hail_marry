"use client";

import * as Tabs from "@radix-ui/react-tabs";
import Highlight from "@tiptap/extension-highlight";
import Placeholder from "@tiptap/extension-placeholder";
import StarterKit from "@tiptap/starter-kit";
import { EditorContent, useEditor } from "@tiptap/react";
import { FilePenLine, Eye, PencilLine } from "lucide-react";
import { useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

function toEditorHtml(content: string) {
    const blocks = content
        .split(/\n{2,}/)
        .map((block) => block.trim())
        .filter(Boolean)
        .map((block) => `<p>${block.replace(/\n/g, "<br/>")}</p>`);
    return blocks.join("");
}

export function EditableNotesSurface({
    title,
    content,
}: {
    title: string;
    content: string;
}) {
    const editor = useEditor({
        immediatelyRender: false,
        extensions: [
            StarterKit,
            Highlight,
            Placeholder.configure({
                placeholder: "Refine the AI draft into your own notes...",
            }),
        ],
        content: toEditorHtml(content),
        editorProps: {
            attributes: {
                class: "min-h-[260px] focus:outline-none text-sm leading-7 text-[var(--text-primary)]",
            },
        },
    });

    useEffect(() => {
        if (editor && content) {
            editor.commands.setContent(toEditorHtml(content));
        }
    }, [content, editor]);

    return (
        <Tabs.Root defaultValue="preview" className="rounded-2xl border border-[var(--border)] bg-[var(--bg-page)]">
            <div className="flex items-center justify-between border-b border-[var(--border)] px-4 py-3">
                <div className="flex items-center gap-2">
                    <div className="rounded-lg bg-emerald-500/15 p-2 text-emerald-400">
                        <FilePenLine className="h-4 w-4" />
                    </div>
                    <div>
                        <p className="text-sm font-medium text-[var(--text-primary)]">{title}</p>
                        <p className="text-xs text-[var(--text-muted)]">Preview the draft or turn it into editable notes</p>
                    </div>
                </div>
                <Tabs.List className="inline-flex rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-1">
                    <Tabs.Trigger
                        value="preview"
                        className="inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs text-[var(--text-secondary)] data-[state=active]:bg-[var(--bg-page)] data-[state=active]:text-[var(--text-primary)]"
                    >
                        <Eye className="h-3.5 w-3.5" />
                        Preview
                    </Tabs.Trigger>
                    <Tabs.Trigger
                        value="edit"
                        className="inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs text-[var(--text-secondary)] data-[state=active]:bg-[var(--bg-page)] data-[state=active]:text-[var(--text-primary)]"
                    >
                        <PencilLine className="h-3.5 w-3.5" />
                        Edit
                    </Tabs.Trigger>
                </Tabs.List>
            </div>

            <Tabs.Content value="preview" className="p-4">
                <div className="prose prose-invert max-w-none text-sm">
                    <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]}>
                        {content}
                    </ReactMarkdown>
                </div>
            </Tabs.Content>

            <Tabs.Content value="edit" className="p-4">
                <div className="rounded-xl border border-[var(--border)] bg-[var(--bg-card)] p-4">
                    <EditorContent editor={editor} />
                </div>
            </Tabs.Content>
        </Tabs.Root>
    );
}
