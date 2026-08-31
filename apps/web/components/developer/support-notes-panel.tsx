"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/page-loading";
import { createAdminSupportNote, getAdminSupportNotes } from "@/lib/admin-api";
import { useAppAuth } from "@/lib/app-auth";
import { ApiError } from "@/lib/api";
import { queryKeys } from "@/lib/query/keys";
import type { SupportNote } from "@rlr/shared";
import { toast } from "@/lib/toast";

function formatTimestamp(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function SupportNotesPanel() {
  const { getToken } = useAppAuth();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [entityType, setEntityType] = useState("audit");
  const [entityId, setEntityId] = useState("");
  const [body, setBody] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const notesQuery = useQuery({
    queryKey: queryKeys.adminNotes({ page }),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new ApiError("Authentication required.", 401);
      return getAdminSupportNotes(token, { page, page_size: 25 });
    },
  });

  const handleCreate = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!entityId.trim() || !body.trim()) {
      toast.error("Entity ID and note body are required.");
      return;
    }

    setSubmitting(true);
    try {
      const token = await getToken();
      if (!token) return;
      await createAdminSupportNote(token, {
        entity_type: entityType,
        entity_id: entityId.trim(),
        body: body.trim(),
      });
      toast.success("Support note saved.");
      setBody("");
      await queryClient.invalidateQueries({ queryKey: ["admin", "notes"] });
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Unable to save note.");
    } finally {
      setSubmitting(false);
    }
  };

  if (notesQuery.isLoading) {
    return <PageLoadingSkeleton message="Loading support notes…" variant="list" />;
  }

  if (notesQuery.error) {
    const message =
      notesQuery.error instanceof ApiError ? notesQuery.error.message : "Unable to load notes.";
    return (
      <div className="rounded-2xl border border-line/60 bg-secondary/30 p-8 text-center">
        <p className="text-muted-foreground">{message}</p>
        <Button className="mt-4" onClick={() => void notesQuery.refetch()}>
          Retry
        </Button>
      </div>
    );
  }

  const data = notesQuery.data;
  const items = data?.items ?? [];

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)]">
      <GlassCard className="p-6">
        <h2 className="font-heading text-xl tracking-tight">Add support note</h2>
        <form onSubmit={(event) => void handleCreate(event)} className="mt-6 space-y-4">
          <div>
            <label htmlFor="entity-type" className="text-sm font-medium">
              Entity type
            </label>
            <select
              id="entity-type"
              value={entityType}
              onChange={(event) => setEntityType(event.target.value)}
              className="mt-2 h-11 w-full rounded-xl border border-line/60 bg-secondary/20 px-4 text-sm"
            >
              <option value="audit">Audit</option>
              <option value="report">Report</option>
              <option value="user">User</option>
              <option value="purchase">Purchase</option>
              <option value="upload">Upload</option>
            </select>
          </div>
          <div>
            <label htmlFor="entity-id" className="text-sm font-medium">
              Entity ID
            </label>
            <input
              id="entity-id"
              value={entityId}
              onChange={(event) => setEntityId(event.target.value)}
              className="mt-2 h-11 w-full rounded-xl border border-line/60 bg-secondary/20 px-4 text-sm"
              placeholder="UUID or Clerk user ID"
            />
          </div>
          <div>
            <label htmlFor="note-body" className="text-sm font-medium">
              Note
            </label>
            <textarea
              id="note-body"
              value={body}
              onChange={(event) => setBody(event.target.value)}
              rows={6}
              className="mt-2 w-full rounded-xl border border-line/60 bg-secondary/20 px-4 py-3 text-sm"
              placeholder="Document support context, refund rationale, or follow-up actions."
            />
          </div>
          <Button type="submit" disabled={submitting}>
            {submitting ? "Saving…" : "Save note"}
          </Button>
        </form>
      </GlassCard>

      <GlassCard className="overflow-hidden p-0">
        {items.length === 0 ? (
          <div className="p-10 text-center text-muted-foreground">No support notes yet.</div>
        ) : (
          <div className="divide-y divide-line/40">
            {items.map((note: SupportNote) => (
              <article key={note.id} className="px-6 py-5">
                <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                  <span>{note.entity_type}</span>
                  <span>·</span>
                  <span>{note.entity_id}</span>
                  <span>·</span>
                  <span>{formatTimestamp(note.created_at)}</span>
                </div>
                <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed">{note.body}</p>
              </article>
            ))}
          </div>
        )}
      </GlassCard>

      {data && data.total > data.page_size && (
        <div className="lg:col-span-2 flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Page {data.page} of {Math.ceil(data.total / data.page_size)}
          </p>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((current) => current - 1)}
            >
              Previous
            </Button>
            <Button
              variant="secondary"
              size="sm"
              disabled={page * data.page_size >= data.total}
              onClick={() => setPage((current) => current + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
