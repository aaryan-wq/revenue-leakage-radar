"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";

export interface AuditFunnelAction {
  label: string;
  disabled?: boolean;
  loading?: boolean;
  onClick: () => void | Promise<void>;
}

interface FunnelActionMeta {
  label: string;
  disabled?: boolean;
  loading?: boolean;
}

interface FunnelActionsApi {
  register: (action: AuditFunnelAction | null) => void;
  invoke: () => void;
}

const FunnelActionsApiContext = createContext<FunnelActionsApi | null>(null);
const FunnelActionMetaContext = createContext<FunnelActionMeta | null>(null);

export function AuditFunnelActionsProvider({ children }: { children: ReactNode }) {
  const onClickRef = useRef<(() => void | Promise<void>) | null>(null);
  const [meta, setMeta] = useState<FunnelActionMeta | null>(null);

  const register = useCallback((action: AuditFunnelAction | null) => {
    if (!action) {
      onClickRef.current = null;
      setMeta(null);
      return;
    }

    onClickRef.current = action.onClick;
    setMeta({
      label: action.label,
      disabled: action.disabled,
      loading: action.loading,
    });
  }, []);

  const invoke = useCallback(() => {
    void onClickRef.current?.();
  }, []);

  const api = useMemo(() => ({ register, invoke }), [invoke, register]);

  return (
    <FunnelActionsApiContext.Provider value={api}>
      <FunnelActionMetaContext.Provider value={meta}>{children}</FunnelActionMetaContext.Provider>
    </FunnelActionsApiContext.Provider>
  );
}

export function useAuditFunnelAction(): FunnelActionMeta | null {
  return useContext(FunnelActionMetaContext);
}

export function useInvokeFunnelAction(): () => void {
  const api = useContext(FunnelActionsApiContext);
  return api?.invoke ?? (() => undefined);
}

/** Register the primary funnel CTA for the current page (cleared on unmount). */
export function useRegisterFunnelAction(action: AuditFunnelAction | null) {
  const api = useContext(FunnelActionsApiContext);
  const onClickRef = useRef(action?.onClick ?? null);
  onClickRef.current = action?.onClick ?? null;

  const label = action?.label ?? "";
  const disabled = action?.disabled ?? false;
  const loading = action?.loading ?? false;
  const isActive = action != null;

  useEffect(() => {
    if (!api) return;

    if (!isActive) {
      api.register(null);
      return;
    }

    api.register({
      label,
      disabled,
      loading,
      onClick: () => onClickRef.current?.(),
    });

    return () => api.register(null);
  }, [api, disabled, isActive, label, loading]);
}
