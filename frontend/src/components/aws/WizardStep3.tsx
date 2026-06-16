"use client";

import * as React from "react";
import { Loader2, Check, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface WizardStep3Data {
  name: string;
  role_arn: string;
  account_id: string;
  region: string;
  s3_cur_bucket: string;
  s3_cur_prefix: string;
}

interface WizardStep3Props {
  data: WizardStep3Data;
  onChange: (data: WizardStep3Data) => void;
  onSubmit: () => void;
  loading: boolean;
}

function parseAccountIdFromArn(arn: string): string | null {
  const match = arn.match(/^arn:aws:iam::(\d{12}):/);
  return match ? match[1] : null;
}

export function WizardStep3({ data, onChange, onSubmit, loading }: WizardStep3Props) {
  const [accountDetected, setAccountDetected] = React.useState(false);
  const [curOpen, setCurOpen] = React.useState(false);

  const handleArnBlur = () => {
    if (!data.account_id) {
      const accountId = parseAccountIdFromArn(data.role_arn);
      if (accountId) {
        onChange({ ...data, account_id: accountId });
        setAccountDetected(true);
        setTimeout(() => setAccountDetected(false), 3000);
      }
    }
  };

  return (
    <div className="space-y-5">
      <p className="text-sm text-muted-foreground">
        Find this in the CloudFormation stack Outputs tab.
      </p>

      <div className="space-y-2">
        <label className="text-xs text-muted-foreground">Role ARN</label>
        <Input
          placeholder="arn:aws:iam::123456789012:role/FinCloudAIReadOnlyRole"
          value={data.role_arn}
          onChange={(e) => onChange({ ...data, role_arn: e.target.value })}
          onBlur={handleArnBlur}
          className="font-mono text-sm"
        />
      </div>

      <div className="space-y-2">
        <label className="text-xs text-muted-foreground">AWS Account ID</label>
        <Input
          placeholder="123456789012"
          value={data.account_id}
          onChange={(e) => onChange({ ...data, account_id: e.target.value })}
          className="font-mono text-sm"
        />
        {accountDetected && (
          <p className="text-xs text-emerald-400 flex items-center gap-1" style={{ animation: "fade-up 150ms var(--ease-out-expo)" }}>
            <Check className="size-3" /> Account ID detected
          </p>
        )}
      </div>

      <div className="space-y-2">
        <label className="text-xs text-muted-foreground">Region</label>
          <Select value={data.region} onValueChange={(v) => onChange({ ...data, region: v ?? "us-east-1" })}>
          <SelectTrigger className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {["us-east-1", "us-east-2", "us-west-1", "us-west-2", "eu-west-1", "eu-central-1", "ap-southeast-1", "ap-northeast-1"].map((r) => (
              <SelectItem key={r} value={r}>{r}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <label className="text-xs text-muted-foreground">Connection Name</label>
        <Input
          placeholder="Production AWS"
          value={data.name}
          onChange={(e) => onChange({ ...data, name: e.target.value })}
        />
      </div>

      <div className="bg-surface-raised rounded-lg border border-white/8 overflow-hidden">
        <button
          onClick={() => setCurOpen(!curOpen)}
          className="w-full flex items-center justify-between px-3 py-2.5 text-sm text-foreground hover:bg-white/5 transition-colors duration-100"
        >
          <span className="text-muted-foreground">Cost &amp; Usage Reports (optional)</span>
          <ChevronDown
            className={cn(
              "size-4 text-muted-foreground transition-transform duration-150",
              curOpen && "rotate-180",
            )}
            style={{ transitionTimingFunction: "var(--ease-out-expo)" }}
          />
        </button>
        {curOpen && (
          <div className="px-3 pb-3 space-y-3" style={{ animation: "fade-up 150ms var(--ease-out-expo)" }}>
            <div className="space-y-2">
              <label className="text-xs text-muted-foreground">S3 CUR Bucket</label>
              <Input
                placeholder="my-cur-bucket"
                value={data.s3_cur_bucket}
                onChange={(e) => onChange({ ...data, s3_cur_bucket: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label className="text-xs text-muted-foreground">S3 CUR Prefix</label>
              <Input
                placeholder="cur/"
                value={data.s3_cur_prefix}
                onChange={(e) => onChange({ ...data, s3_cur_prefix: e.target.value.trimStart() })}
              />
            </div>
          </div>
        )}
      </div>

      <button
        onClick={onSubmit}
        disabled={loading || !data.role_arn || !data.name}
        className={cn(
          "w-full h-9 rounded-lg font-semibold text-sm transition-all duration-150 flex items-center justify-center gap-2",
          loading || !data.role_arn || !data.name
            ? "bg-cyan/40 text-space/60 cursor-not-allowed opacity-40"
            : "bg-cyan text-space hover:bg-cyan/90 opacity-100",
        )}
      >
        {loading ? <Loader2 className="size-4 animate-spin" /> : null}
        Register Connection
      </button>
    </div>
  );
}
