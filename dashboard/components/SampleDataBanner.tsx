export default function SampleDataBanner({ visible }: { visible: boolean }) {
  if (!visible) return null;

  return (
    <div className="w-full bg-ember/15 border-b border-ember/40 text-ember">
      <div className="max-w-5xl mx-auto px-6 py-2.5 flex items-center gap-2 text-sm font-mono">
        <span aria-hidden="true">⚠</span>
        <span>
          Sample data — these numbers are placeholders, not a real benchmark run.
          Run <code className="font-mono bg-ember/10 px-1 rounded">benchmark/run_all.py</code> on a GPU
          and copy the output into <code className="font-mono bg-ember/10 px-1 rounded">dashboard/data/benchmark_results.json</code>.
        </span>
      </div>
    </div>
  );
}
