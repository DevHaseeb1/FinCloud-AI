"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, Loader2, Check } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { AuthFeaturesPanel } from "@/components/auth/AuthFeaturesPanel";

function computeStrength(pw: string): number {
  let score = 0;
  if (pw.length >= 8) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^a-zA-Z0-9]/.test(pw)) score++;
  return score;
}

function StrengthBar({ strength }: { strength: number }) {
  const segments = [
    { label: "Weak", color: "var(--ember)" },
    { label: "Fair", color: "#FBBF24" },
    { label: "Good", color: "#22D3EE" },
    { label: "Strong", color: "var(--cyan)" },
  ];
  return (
    <div className="mt-2 flex gap-1">
      {segments.map((seg, i) => (
        <div
          key={i}
          className="h-1 flex-1 rounded-full bg-white/10 transition-all duration-200"
          style={{ transitionTimingFunction: "var(--ease-out-expo)" }}
        >
          <div
            className="h-full rounded-full transition-all duration-200"
            style={{
              width: i < strength ? "100%" : "0%",
              backgroundColor: i < strength ? seg.color : undefined,
              transitionTimingFunction: "var(--ease-out-expo)",
            }}
          />
        </div>
      ))}
    </div>
  );
}

export default function SignupPage() {
  const { isAuthenticated, isLoading: authLoading, signup } = useAuth();
  const router = useRouter();
  const reduced = useReducedMotion();

  const [name, setName] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [confirmPassword, setConfirmPassword] = React.useState("");
  const [showPassword, setShowPassword] = React.useState(false);
  const [showConfirm, setShowConfirm] = React.useState(false);
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [error, setError] = React.useState("");
  const [fieldErrors, setFieldErrors] = React.useState<Record<string, string>>({});
  const [success, setSuccess] = React.useState(false);

  React.useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.push("/");
    }
  }, [isAuthenticated, authLoading, router]);

  const validate = () => {
    const errors: Record<string, string> = {};
    if (!name || name.length < 2) errors.name = "Name is required (min 2 chars)";
    if (!email) errors.email = "Email is required";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errors.email = "Invalid email format";
    if (!password) errors.password = "Password is required";
    else if (password.length < 8) errors.password = "Min 8 characters";
    else if (password.length > 72) errors.password = "Password cannot exceed 72 characters";
    else if (!/[A-Z]/.test(password)) errors.password = "Must contain an uppercase letter";
    else if (!/[0-9]/.test(password)) errors.password = "Must contain a number";
    if (confirmPassword !== password) errors.confirmPassword = "Passwords do not match";
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const passwordStrength = computeStrength(password);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!validate()) return;
    setIsSubmitting(true);
    try {
      await signup(name, email, password);
      setSuccess(true);
    } catch (err: any) {
      const msg = err?.message || "Registration failed";
      setError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (authLoading) return null;

  if (success) {
    return (
      <div className="flex min-h-[100dvh] w-full items-center justify-center bg-surface p-6">
        <div className="flex flex-col items-center gap-4">
          <div
            className="flex size-16 items-center justify-center rounded-full bg-cyan/20"
            style={{
              animation: "scaleIn 300ms var(--ease-spring)",
            }}
          >
            <Check className="size-8 text-cyan" />
          </div>
          <h2 className="text-xl font-bold text-foreground">Account created!</h2>
          <p className="text-sm text-muted-foreground">Redirecting to dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-[100dvh] w-full">
      <AuthFeaturesPanel variant="signup" />

      {/* Right Panel */}
      <div className="flex w-full items-center justify-center bg-surface p-6 lg:w-1/2">
        <div
          className="w-full max-w-md"
          style={{
            opacity: reduced ? 1 : 0,
            animation: reduced ? "none" : "fade-up 320ms var(--ease-out-expo) 60ms forwards",
          }}
        >
          <div className="rounded-2xl border border-white/8 bg-surface p-8">
            <h2 className="text-2xl font-bold text-foreground">Create your account</h2>
            <p className="mt-1 text-sm text-muted-foreground">Start monitoring your cloud costs</p>

            {error && (
              <div
                className="mt-4 rounded-lg bg-destructive/10 px-3 py-2 text-sm text-ember"
                style={{
                  animation: "slideDown 150ms var(--ease-out-expo)",
                }}
              >
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="mt-6 space-y-4">
              <div
                style={{
                  opacity: reduced ? 1 : 0,
                  animation: reduced ? "none" : "fade-up 320ms var(--ease-out-expo) 100ms forwards",
                }}
              >
                <label className="mb-1.5 block text-sm font-medium text-foreground">Full name</label>
                <Input
                  type="text"
                  placeholder="John Doe"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="bg-surface-raised border-white/10 focus-visible:ring-cyan/50"
                  aria-invalid={!!fieldErrors.name}
                />
                {fieldErrors.name && <p className="mt-1 text-sm text-ember">{fieldErrors.name}</p>}
              </div>

              <div
                style={{
                  opacity: reduced ? 1 : 0,
                  animation: reduced ? "none" : "fade-up 320ms var(--ease-out-expo) 140ms forwards",
                }}
              >
                <label className="mb-1.5 block text-sm font-medium text-foreground">Email</label>
                <Input
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="bg-surface-raised border-white/10 focus-visible:ring-cyan/50"
                  aria-invalid={!!fieldErrors.email}
                />
                {fieldErrors.email && <p className="mt-1 text-sm text-ember">{fieldErrors.email}</p>}
              </div>

              <div
                style={{
                  opacity: reduced ? 1 : 0,
                  animation: reduced ? "none" : "fade-up 320ms var(--ease-out-expo) 180ms forwards",
                }}
              >
                <label className="mb-1.5 block text-sm font-medium text-foreground">Password</label>
                <div className="relative">
                  <Input
                    type={showPassword ? "text" : "password"}
                    placeholder="Min 8 chars, 1 uppercase, 1 number"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="bg-surface-raised border-white/10 focus-visible:ring-cyan/50 pr-10"
                    aria-invalid={!!fieldErrors.password}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                    tabIndex={-1}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
                  </button>
                </div>
                {password && <StrengthBar strength={passwordStrength} />}
                {fieldErrors.password && <p className="mt-1 text-sm text-ember">{fieldErrors.password}</p>}
              </div>

              <div
                style={{
                  opacity: reduced ? 1 : 0,
                  animation: reduced ? "none" : "fade-up 320ms var(--ease-out-expo) 220ms forwards",
                }}
              >
                <label className="mb-1.5 block text-sm font-medium text-foreground">Confirm password</label>
                <div className="relative">
                  <Input
                    type={showConfirm ? "text" : "password"}
                    placeholder="Re-enter your password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="bg-surface-raised border-white/10 focus-visible:ring-cyan/50 pr-10"
                    aria-invalid={!!fieldErrors.confirmPassword}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirm(!showConfirm)}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                    tabIndex={-1}
                    aria-label={showConfirm ? "Hide confirm password" : "Show confirm password"}
                  >
                    {showConfirm ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
                  </button>
                </div>
                {fieldErrors.confirmPassword && (
                  <p className="mt-1 text-sm text-ember">{fieldErrors.confirmPassword}</p>
                )}
              </div>

              <Button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-cyan text-space font-semibold hover:brightness-110 active:scale-[0.98] transition-all h-10"
              >
                {isSubmitting ? (
                  <Loader2 className="size-4 animate-spin text-space" />
                ) : (
                  "Create account"
                )}
              </Button>
            </form>

            <p className="mt-6 text-center text-sm text-muted-foreground">
              Already have an account?{" "}
              <Link href="/login" className="text-cyan hover:underline">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes slideDown {
          from { opacity: 0; transform: translateY(-4px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes scaleIn {
          from { transform: scale(0); }
          to { transform: scale(1); }
        }
      `}</style>
    </div>
  );
}
