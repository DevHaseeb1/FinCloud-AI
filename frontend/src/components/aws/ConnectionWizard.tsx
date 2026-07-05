"use client";

import * as React from "react";
import { X as XIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { WizardStep1 } from "@/components/aws/WizardStep1";
import { WizardStep2 } from "@/components/aws/WizardStep2";
import { WizardStep3 } from "@/components/aws/WizardStep3";
import { WizardStep4 } from "@/components/aws/WizardStep4";
import * as awsService from "@/services/awsService";
import type { AwsTestCheck } from "@/types/apiTypes";

interface ConnectionWizardProps {
  open: boolean;
  onClose: () => void;
  onComplete: () => void;
}

const STEPS = ["Generate", "Deploy", "Register", "Validate"];

export function ConnectionWizard({ open, onClose, onComplete }: ConnectionWizardProps) {
  const reduced = useReducedMotion();
  const [step, setStep] = React.useState(0);
  const [direction, setDirection] = React.useState<"forward" | "back">("forward");

  const [setupLoading, setSetupLoading] = React.useState(true);
  const [externalId, setExternalId] = React.useState("");
  const [roleName, setRoleName] = React.useState("");
  const [cloudformationUrl, setCloudformationUrl] = React.useState("");
  const [templateDownloadUrl, setTemplateDownloadUrl] = React.useState("");

  const [registerData, setRegisterData] = React.useState({
    name: "",
    role_arn: "",
    account_id: "",
    region: "us-east-1",
    s3_cur_bucket: "",
    s3_cur_prefix: "",
  });
  const [registerLoading, setRegisterLoading] = React.useState(false);
  const [registeredId, setRegisteredId] = React.useState<number | null>(null);

  const [testChecks, setTestChecks] = React.useState<AwsTestCheck[]>([]);
  const [testLoading, setTestLoading] = React.useState(true);
  const [testOverallStatus, setTestOverallStatus] = React.useState<string | null>(null);

  const [legacyMode, setLegacyMode] = React.useState(false);
  const [legacyKeys, setLegacyKeys] = React.useState({ access_key_id: "", secret_access_key: "" });
  const [showSecret, setShowSecret] = React.useState(false);

  React.useEffect(() => {
    if (!open) return;
    setStep(0);
    setDirection("forward");
    setSetupLoading(true);
    setTestChecks([]);
    setTestOverallStatus(null);
    setLegacyMode(false);

    document.body.style.overflow = "hidden";

    awsService.setupConnection().then((res) => {
      setExternalId(res.external_id);
      setRoleName(res.role_name);
      setCloudformationUrl(res.cloudformation_url);
      setTemplateDownloadUrl(res.template_download_url ?? "");
      setSetupLoading(false);
    }).catch(() => {
      setSetupLoading(false);
    });

    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  const goToStep = (s: number, dir: "forward" | "back") => {
    setDirection(dir);
    setStep(s);
  };

  const handleRegister = async () => {
    setRegisterLoading(true);
    try {
      const res = await awsService.createConnection({
        name: registerData.name,
        account_id: registerData.account_id || undefined,
        role_arn: registerData.role_arn || undefined,
        external_id: externalId,
        region: registerData.region,
        s3_cur_bucket: registerData.s3_cur_bucket || undefined,
        s3_cur_prefix: registerData.s3_cur_prefix || undefined,
      });
      setRegisteredId(res.connection_id);
      goToStep(3, "forward");
      runTests(res.connection_id);
    } catch (e) {
      console.error("Register failed", e);
    } finally {
      setRegisterLoading(false);
    }
  };

  const runTests = async (connectionId: number) => {
    setTestLoading(true);
    setTestChecks([]);
    setTestOverallStatus(null);
    try {
      const res = await awsService.testConnection({ connection_id: connectionId });
      setTestChecks(res.checks);
      setTestOverallStatus(res.overall_status);
    } catch (e) {
      setTestChecks([{ check: "STS AssumeRole", status: "error", message: "Test request failed" }]);
      setTestOverallStatus("error");
    } finally {
      setTestLoading(false);
    }
  };

  const handleLegacyRegister = async () => {
    setRegisterLoading(true);
    try {
      const res = await awsService.createConnection({
        name: registerData.name,
        account_id: registerData.account_id || undefined,
        access_key_id: legacyKeys.access_key_id,
        secret_access_key: legacyKeys.secret_access_key,
        region: registerData.region,
      });
      setRegisteredId(res.connection_id);
      goToStep(3, "forward");
      runTests(res.connection_id);
    } catch (e) {
      console.error("Legacy register failed", e);
    } finally {
      setRegisterLoading(false);
    }
  };

  if (!open) return null;

  const stepLabels = legacyMode ? ["Keys", "Validate"] : STEPS;

  return (
    <div
      className="fixed inset-0 z-50"
      onClick={onClose}
      style={{ animation: "fadeIn 200ms" }}
    >
      {!reduced && (
        <style>{`
          @keyframes fadeIn { from { opacity: 0 } to { opacity: 1 } }
        `}</style>
      )}
      <div className="fixed inset-0 bg-space/80 backdrop-blur-sm" />

      <div className="flex min-h-screen items-center justify-center p-4">
      <div
        className="relative bg-surface border border-white/8 rounded-2xl w-full max-w-[560px] max-h-[85vh] overflow-y-auto p-6"
        onClick={(e) => e.stopPropagation()}
        style={{
          animation: reduced ? "none" : "fadeUpCard 300ms var(--ease-out-expo)",
        }}
      >
        {!reduced && (
          <style>{`
            @keyframes fadeUpCard {
              from { opacity: 0; transform: translateY(16px); }
              to { opacity: 1; transform: translateY(0); }
            }
          `}</style>
        )}

        <button
          onClick={onClose}
          className="absolute top-4 right-4 size-8 flex items-center justify-center rounded-md text-muted-foreground hover:bg-white/5 transition-colors duration-100"
          aria-label="Close"
        >
          <XIcon className="size-4" />
        </button>

        {!legacyMode && (
          <div className="flex items-center justify-center gap-2 mb-6">
            {STEPS.map((label, i) => {
              const isCurrent = step === i;
              const isDone = i < step;
              return (
                <div key={label} className="flex items-center gap-2">
                  <div
                    className={cn(
                      "size-2 rounded-full transition-all duration-150",
                      isDone && "bg-cyan",
                      isCurrent && "bg-cyan shadow-[0_0_0_4px] shadow-primary/30",
                      !isDone && !isCurrent && "bg-white/20",
                    )}
                    style={{
                      transform: isCurrent ? "scale(1)" : "scale(0.8)",
                      transitionTimingFunction: "var(--ease-spring)",
                    }}
                  />
                  {i < STEPS.length - 1 && (
                    <div className={cn("w-6 h-px", isDone ? "bg-cyan" : "bg-white/10")} />
                  )}
                </div>
              );
            })}
          </div>
        )}

        <div className="text-center mb-5">
          <h2 className="text-xl font-semibold text-foreground" style={{ fontFamily: "var(--font-sans)", fontWeight: 700 }}>
            {legacyMode ? "Connect with Access Keys" : "Connect your AWS Account"}
          </h2>
        </div>

        <div
          className="transition-all duration-200"
          style={{
            opacity: 1,
            transform: "translateX(0)",
            transitionTimingFunction: "var(--ease-in-out-circ)",
          }}
        >
          {!legacyMode && step === 0 && (
            <WizardStep1
              externalId={externalId}
              roleName={roleName}
              loading={setupLoading}
              onNext={() => goToStep(1, "forward")}
            />
          )}

          {!legacyMode && step === 1 && (
            <WizardStep2
              cloudformationUrl={cloudformationUrl}
              templateDownloadUrl={templateDownloadUrl}
              externalId={externalId}
              onNext={() => goToStep(2, "forward")}
            />
          )}

          {!legacyMode && step === 2 && (
            <WizardStep3
              data={registerData}
              onChange={setRegisterData}
              onSubmit={handleRegister}
              loading={registerLoading}
            />
          )}

          {!legacyMode && step === 3 && (
            <WizardStep4
              checks={testChecks}
              loading={testLoading}
              overallStatus={testOverallStatus}
              connectionId={registeredId}
              onGoBack={() => goToStep(2, "back")}
              onRetry={() => registeredId && runTests(registeredId)}
              onSkipCur={() => {
                setRegisterData((d) => ({ ...d, s3_cur_bucket: "", s3_cur_prefix: "" }));
                if (registeredId) runTests(registeredId);
              }}
              onEdit={() => goToStep(2, "back")}
            />
          )}

          {legacyMode && step === 0 && (
            <div className="space-y-4">
              <div className="bg-ember/10 border border-ember/30 rounded-lg p-3 text-xs text-ember">
                Access keys are less secure than IAM Roles. We recommend using the guided setup above.
              </div>
              <div className="space-y-2">
                <label className="text-xs text-muted-foreground">Access Key ID</label>
                <input
                  className="h-8 w-full rounded-lg border border-input bg-transparent px-2.5 font-mono text-sm"
                  placeholder="AKIA..."
                  value={legacyKeys.access_key_id}
                  onChange={(e) => setLegacyKeys((k) => ({ ...k, access_key_id: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs text-muted-foreground">Secret Access Key</label>
                <div className="relative">
                  <input
                    type={showSecret ? "text" : "password"}
                    className="h-8 w-full rounded-lg border border-input bg-transparent px-2.5 font-mono text-sm pr-8"
                    placeholder="wJalrXUt..."
                    value={legacyKeys.secret_access_key}
                    onChange={(e) => setLegacyKeys((k) => ({ ...k, secret_access_key: e.target.value }))}
                  />
                  <button
                    onClick={() => setShowSecret(!showSecret)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground text-xs"
                    type="button"
                  >
                    {showSecret ? "Hide" : "Show"}
                  </button>
                </div>
              </div>
              <button
                onClick={handleLegacyRegister}
                disabled={registerLoading || !legacyKeys.access_key_id || !legacyKeys.secret_access_key}
                className="w-full h-9 rounded-lg bg-cyan text-space font-semibold text-sm hover:bg-cyan/90 transition-all duration-100 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Connect with Access Keys
              </button>
            </div>
          )}

          {legacyMode && step === 1 && (
            <WizardStep4
              checks={testChecks}
              loading={testLoading}
              overallStatus={testOverallStatus}
              connectionId={registeredId}
              onGoBack={() => goToStep(0, "back")}
              onRetry={() => registeredId && runTests(registeredId)}
              onSkipCur={() => {}}
              onEdit={() => goToStep(0, "back")}
            />
          )}
        </div>

        {!legacyMode && step === 0 && (
          <button
            onClick={() => {
              setLegacyMode(true);
              setStep(0);
            }}
            className="mt-4 w-full text-center text-xs text-muted-foreground hover:text-foreground transition-colors duration-100"
          >
            Use access keys instead
          </button>
        )}
      </div>
      </div>
    </div>
  );
}
