import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FpsRangeChart } from "../components/FpsRangeChart";
import { FeatureImportanceChart } from "../components/FeatureImportanceChart";

describe("FpsRangeChart", () => {
  it("renders without crashing for a typical prediction", () => {
    render(<FpsRangeChart low={50} predicted={60} high={70} />);
    expect(screen.getByTestId("fps-range-chart")).toBeInTheDocument();
  });
});

describe("FeatureImportanceChart", () => {
  it("renders a bar per feature", () => {
    render(
      <FeatureImportanceChart
        data={[
          { label: "GPU tier", importance: 0.5 },
          { label: "CPU tier", importance: 0.3 },
          { label: "Game", importance: 0.2 },
        ]}
      />
    );
    expect(screen.getByTestId("feature-importance-chart")).toBeInTheDocument();
  });
});
