import fs from "fs";
import path from "path";
import type { BenchmarkResults } from "./types";

/**
 * Loads the dashboard's data. Prefers a real benchmark run; falls back to
 * the sample dataset if the real one hasn't been generated/copied in yet.
 *
 * This is a server-only module (uses `fs`) — only import it from server
 * components, not from anything rendered client-side.
 */
export function loadResults(): BenchmarkResults {
  const realPath = path.join(process.cwd(), "data", "benchmark_results.json");
  const samplePath = path.join(process.cwd(), "data", "sample_results.json");

  const fileToRead = fs.existsSync(realPath) ? realPath : samplePath;
  const raw = fs.readFileSync(fileToRead, "utf-8");
  return JSON.parse(raw) as BenchmarkResults;
}
