"use client";

import { LandingHeader } from "@/components/landing/LandingHeader";
import { HeroSection } from "@/components/landing/HeroSection";
import { StatsBar } from "@/components/landing/StatsBar";
import { DemoSection } from "@/components/landing/DemoSection";
import { HowItWorksSection } from "@/components/landing/HowItWorksSection";
import { FeaturesSection } from "@/components/landing/FeaturesSection";
import { HowAIWorksSection } from "@/components/landing/HowAIWorksSection";
import { ArchitectureSection } from "@/components/landing/ArchitectureSection";
import { SavingsSection } from "@/components/landing/SavingsSection";
import { FinalCTASection } from "@/components/landing/FinalCTASection";
import { LandingFooter } from "@/components/landing/LandingFooter";

export default function LandingPage() {
  return (
    <div className="dark h-full overflow-y-auto overflow-x-hidden" data-scroll-container>
      <LandingHeader />
      <HeroSection />
      <StatsBar />
      <DemoSection />
      <HowItWorksSection />
      <FeaturesSection />
      <HowAIWorksSection />
      <ArchitectureSection />
      <SavingsSection />
      <FinalCTASection />
      <LandingFooter />
    </div>
  );
}
