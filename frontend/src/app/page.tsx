"use client";

import { LandingHeader } from "@/components/landing/LandingHeader";
import { HeroSection } from "@/components/landing/HeroSection";
import { StatsBar } from "@/components/landing/StatsBar";
import { DemoSection } from "@/components/landing/DemoSection";
import { DifferentiatorsSection } from "@/components/landing/DifferentiatorsSection";
import { FeaturesSection } from "@/components/landing/FeaturesSection";
import { HowItWorksSection } from "@/components/landing/HowItWorksSection";
import { ArchitectureSection } from "@/components/landing/ArchitectureSection";
import { SavingsSection } from "@/components/landing/SavingsSection";
import { TechExcellenceSection } from "@/components/landing/TechExcellenceSection";
import { FinalCTASection } from "@/components/landing/FinalCTASection";
import { LandingFooter } from "@/components/landing/LandingFooter";

export default function LandingPage() {
  return (
    <div className="h-full overflow-y-auto overflow-x-hidden" data-scroll-container>
      <LandingHeader />
      <HeroSection />
      <StatsBar />
      <DemoSection />
      <DifferentiatorsSection />
      <FeaturesSection />
      <HowItWorksSection />
      <ArchitectureSection />
      <SavingsSection />
      <TechExcellenceSection />
      <FinalCTASection />
      <LandingFooter />
    </div>
  );
}
