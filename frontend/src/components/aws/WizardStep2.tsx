"use client";

import * as React from "react";
import { ChevronDown, Download, ExternalLink, Terminal } from "lucide-react";
import { cn } from "@/lib/utils";
import { api } from "@/services/api";

interface WizardStep2Props {
  cloudformationUrl: string;
  templateDownloadUrl: string;
  externalId: string;
  onNext: () => void;
}

const permissions = [
  "ce:GetCostAndUsage",
  "ce:GetCostForecast",
  "s3:GetObject",
  "s3:ListBucket",
];

export function WizardStep2({ cloudformationUrl, templateDownloadUrl, externalId, onNext }: WizardStep2Props) {
  const [deployed, setDeployed] = React.useState(false);
  const [permissionsOpen, setPermissionsOpen] = React.useState(false);

  const handleDownload = async () => {
    try {
      const res = await api.get(templateDownloadUrl, { responseType: "blob" });
      const url = URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = "fincloud-ai-readonly-role.yaml";
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error("Download failed", e);
    }
  };

  return (
    <div className="space-y-5">
      <p className="text-sm text-muted-foreground">
        Deploy a read-only IAM role in your AWS account. No write permissions are granted.
      </p>

      <div className="bg-surface-raised rounded-lg border border-white/8 overflow-hidden">
        <button
          onClick={() => setPermissionsOpen(!permissionsOpen)}
          className="w-full flex items-center justify-between px-3 py-2.5 text-sm text-foreground hover:bg-white/5 transition-colors duration-100"
        >
          <span>Permissions this role receives</span>
          <ChevronDown
            className={cn(
              "size-4 text-muted-foreground transition-transform duration-150",
              permissionsOpen && "rotate-180",
            )}
            style={{ transitionTimingFunction: "var(--ease-out-expo)" }}
          />
        </button>
        {permissionsOpen && (
          <div className="px-3 pb-3 space-y-1.5" style={{ animation: "fade-up 150ms var(--ease-out-expo)" }}>
            {permissions.map((perm) => (
              <div key={perm} className="font-mono text-xs text-muted-foreground pl-2 border-l-2 border-cyan/30">
                {perm}
              </div>
            ))}
          </div>
        )}
      </div>

      <button
        onClick={() => window.open(cloudformationUrl, "_blank")}
        className="flex items-center justify-center gap-2 w-full h-9 rounded-lg bg-violet text-white font-semibold text-sm hover:bg-violet/90 transition-all duration-100"
      >
        <ExternalLink className="size-4" />
        Launch in AWS Console
      </button>

      <button
        onClick={handleDownload}
        className="flex items-center justify-center gap-2 w-full h-9 rounded-lg bg-cyan text-space font-semibold text-sm hover:bg-cyan/90 transition-all duration-100"
      >
        <Download className="size-4" />
        Download CloudFormation Template
      </button>

      <div className="space-y-3">
        <div className="flex items-center gap-2 text-sm font-medium text-foreground">
          <Terminal className="size-4 text-cyan" />
          Deploy via AWS CLI
        </div>
        <code className="block font-mono text-xs bg-space/50 p-3 rounded border border-white/8 select-all leading-relaxed">
          {`aws cloudformation create-stack \\\n  --stack-name FinCloudAIReadOnlyRole \\\n  --template-body file://./fincloud-ai-readonly-role.yaml \\\n  --parameters ParameterKey=ExternalId,ParameterValue=${externalId} \\\n  --capabilities CAPABILITY_NAMED_IAM`}
        </code>
        <p className="text-xs text-muted-foreground">
          Download the template above, then run this command in your terminal.
        </p>
      </div>

      <div className="bg-surface-raised rounded-lg p-3 border border-white/8 text-xs text-muted-foreground space-y-1">
        <p className="font-medium text-foreground mb-1">Manual deploy via AWS Console:</p>
        <ol className="list-decimal pl-4 space-y-1">
          <li>Open <span className="text-cyan">CloudFormation</span> in AWS Console</li>
          <li>Click <span className="text-cyan">Create stack &rarr; With new resources</span></li>
          <li>Select <span className="text-cyan">Template is ready</span> &rarr; <span className="text-cyan">Upload a template file</span></li>
          <li>Upload the downloaded YAML file</li>
          <li>Set <span className="text-cyan">ExternalId</span> parameter to: <code className="font-mono bg-space/50 px-1 rounded select-all">{externalId}</code></li>
          <li>Check <span className="text-cyan">I acknowledge that AWS CloudFormation might create IAM resources</span></li>
          <li>Click <span className="text-cyan">Create stack</span></li>
        </ol>
      </div>

      <p className="text-xs text-muted-foreground text-center">
        The stack takes ~2 minutes to deploy. Return here once it&apos;s complete.
      </p>

      <label className="flex items-center gap-2.5 cursor-pointer group">
        <input
          type="checkbox"
          checked={deployed}
          onChange={(e) => setDeployed(e.target.checked)}
          className="size-4 rounded border-white/20 accent-cyan"
        />
        <span className="text-sm text-muted-foreground group-hover:text-foreground transition-colors duration-100">
          I&apos;ve deployed the stack
        </span>
      </label>

      <button
        onClick={onNext}
        disabled={!deployed}
        className={cn(
          "w-full h-9 rounded-lg font-semibold text-sm transition-all duration-150",
          deployed
            ? "bg-cyan text-space hover:bg-cyan/90 opacity-100"
            : "bg-cyan/40 text-space/60 cursor-not-allowed opacity-40",
        )}
      >
        Next &rarr;
      </button>
    </div>
  );
}
