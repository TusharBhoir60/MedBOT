import { PhysicianLayout } from "@/components/layout/physician-layout";

export default function ReviewDetailPage({ params }: { params: { id: string } }) {
  return (
    <PhysicianLayout>
      <div className="p-6 sm:p-10">
        <h1 className="text-2xl font-bold tracking-tight">Review Case {params.id}</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Case detail placeholder. Full agent pipeline results and confidence scoring will be shown here.
        </p>
      </div>
    </PhysicianLayout>
  );
}
