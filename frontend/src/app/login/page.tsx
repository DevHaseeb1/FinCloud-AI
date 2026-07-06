"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@/hooks/useAuth";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { fadeUpDelayed } from "@/lib/animations";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { AuthFeaturesPanel } from "@/components/auth/AuthFeaturesPanel";

export default function LoginPage() {
  const { isAuthenticated, isLoading: authLoading, login } = useAuth();
  const router = useRouter();
  const reduced = useReducedMotion();

  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [showPassword, setShowPassword] = React.useState(false);
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [error, setError] = React.useState("");
  const [fieldErrors, setFieldErrors] = React.useState<{ email?: string; password?: string }>({});
  const [shake, setShake] = React.useState(false);

  React.useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, authLoading, router]);

  const validate = () => {
    const errors: { email?: string; password?: string } = {};
    if (!email) errors.email = "Email is required";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errors.email = "Invalid email format";
    if (!password) errors.password = "Password is required";
    else if (password.length > 72) errors.password = "Password cannot exceed 72 characters";
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!validate()) return;
    setIsSubmitting(true);
    try {
      await login(email, password);
    } catch (err: any) {
      const msg = err?.message || "Invalid email or password";
      setError(msg);
      setShake(true);
      setTimeout(() => setShake(false), 400);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (authLoading) return null;

  return (
    <div className="dark flex min-h-[100dvh] w-full">
      <AuthFeaturesPanel variant="login" />

      {/* Right Panel */}
      <div className="flex w-full items-center justify-center bg-surface p-6 lg:w-1/2">
        <motion.div
          className="w-full max-w-md"
          initial={reduced ? false : "hidden"}
          animate="visible"
          variants={fadeUpDelayed(0.06)}
        >
          <motion.div
            className="rounded-2xl border border-white/8 bg-surface p-8"
            animate={shake ? { x: [0, -6, 6, -4, 4, 0] } : {}}
            transition={{ duration: 0.4 }}
          >
            <h2 className="text-2xl font-bold text-foreground">Welcome back</h2>
            <p className="mt-1 text-sm text-muted-foreground">Sign in to your account</p>

            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -4 }}
                  className="mt-4 rounded-lg bg-destructive/10 px-3 py-2 text-sm text-ember"
                >
                  {error}
                </motion.div>
              )}
            </AnimatePresence>

            <form onSubmit={handleSubmit} className="mt-6 space-y-4">
              <motion.div
                initial={reduced ? false : "hidden"}
                animate="visible"
                variants={fadeUpDelayed(0.1)}
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
                {fieldErrors.email && (
                  <p className="mt-1 text-sm text-ember">{fieldErrors.email}</p>
                )}
              </motion.div>

              <motion.div
                initial={reduced ? false : "hidden"}
                animate="visible"
                variants={fadeUpDelayed(0.14)}
              >
                <label className="mb-1.5 block text-sm font-medium text-foreground">Password</label>
                <div className="relative">
                  <Input
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
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
                {fieldErrors.password && (
                  <p className="mt-1 text-sm text-ember">{fieldErrors.password}</p>
                )}
              </motion.div>

              <motion.div
                initial={reduced ? false : "hidden"}
                animate="visible"
                variants={fadeUpDelayed(0.18)}
              >
                <Button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full bg-cyan text-space font-semibold hover:brightness-110 active:scale-[0.98] transition-all h-10 hover:scale-[1.02]"
                >
                  {isSubmitting ? (
                    <Loader2 className="size-4 animate-spin text-space" />
                  ) : (
                    "Sign in"
                  )}
                </Button>
              </motion.div>
            </form>

            <p className="mt-6 text-center text-sm text-muted-foreground">
              Don&apos;t have an account?{" "}
              <Link href="/signup" className="text-cyan hover:underline">
                Sign up
              </Link>
            </p>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
