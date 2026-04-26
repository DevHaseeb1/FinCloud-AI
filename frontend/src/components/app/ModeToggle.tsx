"use client";

import { Button } from "@/components/ui/button";
import { useDataMode } from "@/lib/mode";

export function ModeToggle() {
  const { mode, setMode } = useDataMode();
  return (
    <div className="flex items-center gap-1 rounded-md border bg-card p-1">
      <Button
        size="sm"
        variant={mode === "synthetic" ? "default" : "ghost"}
        onClick={() => setMode("synthetic")}
      >
        Synthetic
      </Button>
      <Button
        size="sm"
        variant={mode === "aws" ? "default" : "ghost"}
        onClick={() => setMode("aws")}
      >
        AWS
      </Button>
    </div>
  );
}

