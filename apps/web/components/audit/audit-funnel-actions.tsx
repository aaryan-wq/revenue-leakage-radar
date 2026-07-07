"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

export interface AuditFunnelAction {
  label: string;
  disabled?: boolean;
  loading?: boolean;
  onClick: () => void | Promise<void>;
}

interface AuditFunnelActionsContextValue {
  action: AuditFunnelAction | null;
  setAction: (action: AuditFunnelAction | null) => void;
}

const AuditFunnelActionsContext = createContext<AuditFunnelActionsContextValue | null>(null);

export function AuditFunnelActionsProvider({ children }: { children: ReactNode }) {
  const [action, setAction] = useState<AuditFunnelAction | null>(null);
  const value = useMemo(() => ({ action, setAction }), [action]);

  return (
    <AuditFunnelActionsContext.Provider value={value}>{children}</AuditFunnelActionsContext.Provider>
  );
}

export function useAuditFunnelAction(): AuditFunnelAction | null {
  const context = useContext(AuditFunnelActionsContext);
  return context?.action ?? null;
}

/** Register the primary funnel CTA for the current page (cleared on unmount). */
export function useRegisterFunnelAction(action: AuditFunnelAction | null) {
  const context = useContext(AuditFunnelActionsContext);
  const setAction = context?.setAction;

  const label = action?.label ?? "";
  const disabled = action?.disabled ?? false;
  const loading = action?.loading ?? false;
  const onClick = action?.onClick;

  const stableOnClick = useCallback(() => {
    void onClick?.();
  }, [onClick]);

  useEffect(() => {
    if (!setAction) return;

    if (!action) {
      setAction(null);
      return;
    }

    setAction({
      label,
      disabled,
      loading,
      onClick: stableOnClick,
    });

    return () => setAction(null);
  }, [action, disabled, label, loading, setAction, stableOnClick]);
}
