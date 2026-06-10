"use client";

import * as React from "react";

export type DataMode = "synthetic";

type ModeContextValue = {
  mode: DataMode;
  setMode: (mode: DataMode) => void;
};

const ModeContext = React.createContext<ModeContextValue | null>(null);

const STORAGE_KEY = "fincloud:data-mode";

export function ModeProvider({ children }: { children: React.ReactNode }) {
  const [mode, setModeState] = React.useState<DataMode>("synthetic");

  React.useEffect(() => {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (raw === "synthetic") setModeState(raw);
  }, []);

  const setMode = React.useCallback((next: DataMode) => {
    setModeState(next);
    window.localStorage.setItem(STORAGE_KEY, next);
  }, []);

  const value = React.useMemo(() => ({ mode, setMode }), [mode, setMode]);

  return <ModeContext.Provider value={value}>{children}</ModeContext.Provider>;
}

export function useDataMode() {
  const ctx = React.useContext(ModeContext);
  if (!ctx) throw new Error("useDataMode must be used within ModeProvider");
  return ctx;
}

