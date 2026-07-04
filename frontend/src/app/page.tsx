import { LandingNav } from "@/components/layout/landing-nav";
import { HeroSection } from "@/components/ui/hero-section";
import { HowItWorksSection } from "@/components/ui/how-it-works-section";
import { CMARSection } from "@/components/ui/cmar-section";
import { FeaturesSection } from "@/components/ui/features-section";
import { WhySection } from "@/components/ui/why-section";
import { SafetySection } from "@/components/ui/safety-section";
import { CTASection } from "@/components/ui/cta-section";
import { Activity } from "lucide-react";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-background selection:bg-primary/20">
      <LandingNav />
      <main className="flex-1">
        <HeroSection />
        <HowItWorksSection />
        <CMARSection />
        <FeaturesSection />
        <WhySection />
        <SafetySection />
        <CTASection />
      </main>

      <footer className="border-t border-border bg-muted/30 py-12">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-6 px-4 sm:flex-row sm:px-6">
          <div className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-muted-foreground" />
            <span className="text-sm font-medium text-muted-foreground">AarogyaAgent v2</span>
          </div>
          <p className="text-xs text-muted-foreground text-center sm:text-left">
            Built for clinical reliability. © {new Date().getFullYear()} All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
