import type { SupportingDetailRegionProps } from "../types/pcmawTypes";

export default function SupportingDetailRegion({
  artifact,
}: SupportingDetailRegionProps) {
  return (
    <section className="pcmaw-supporting-detail-region">
      <h2>Supporting Detail</h2>
      <p>Processing, provenance, and technical detail will live here.</p>
      <p>Total points: {artifact.points.length}</p>
    </section>
  );
}