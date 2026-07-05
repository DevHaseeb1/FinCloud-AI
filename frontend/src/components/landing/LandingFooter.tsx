"use client";

import * as React from "react";

export function LandingFooter() {
  return (
    <footer className="border-t border-white/[0.06] bg-background">
      <div className="mx-auto max-w-7xl px-6 md:px-20 py-8">
        <div className="border-t border-white/[0.04] pt-6 text-center">
          <p className="text-xs text-white/30">
            &copy; {new Date().getFullYear()} FinCloud-AI. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
