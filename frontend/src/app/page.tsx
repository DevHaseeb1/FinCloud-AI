"use client";

import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { DashboardPage } from "@/components/dashboard/DashboardPage";

export default function Home() {
  return (
    <ProtectedRoute>
      <DashboardPage />
    </ProtectedRoute>
  );
}
