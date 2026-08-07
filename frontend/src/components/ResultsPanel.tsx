import { Link } from "react-router-dom";
import type { PredictResponse } from "../types";
import { FpsRangeChart } from "./FpsRangeChart";
import { FeatureImportanceChart } from "./FeatureImportanceChart";

interface ResultsPanelProps {
  result: PredictResponse;
  gameName: string;
}

export function ResultsPanel({ result, gameName }: ResultsPanelProps) {
  return (
    <section
      data-testid="results-panel"
      className="flex flex-col gap-6 rounded-lg border border-white/10 bg-[#101116] p-5"
    >
      <div>
        <p className="text-sm text-gray-400">Estimated performance for {gameName}</p>
        <p className="text-4xl font-semibold text-gray-100">
          {result.predicted_fps} <span className="text-lg font-normal text-gray-400">FPS</span>
        </p>
        <p className="text-sm text-gray-500">
          Predicted range: {result.low_fps}&ndash;{result.high_fps} FPS
        </p>
      </div>

      <FpsRangeChart low={result.low_fps} predicted={result.predicted_fps} high={result.high_fps} />

      <div>
        <h3 className="mb-2 text-sm font-medium text-gray-300">
          What mattered most in this estimate
        </h3>
        <FeatureImportanceChart data={result.feature_importance} />
      </div>

      <div className="rounded-md border border-purple-400/30 bg-purple-400/5 p-3 text-xs text-gray-400">
        <p>{result.disclaimer}</p>
        <p className="mt-1">
          Model version {result.model_version}. Full breakdown of how these estimates are built:{" "}
          <Link to="/methodology" className="underline hover:text-gray-200">
            read the Methodology page
          </Link>
          .
        </p>
      </div>
    </section>
  );
}
