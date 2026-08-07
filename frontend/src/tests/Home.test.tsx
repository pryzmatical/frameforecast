import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Home } from "../pages/Home";
import * as api from "../lib/api";

const CATALOG = {
  games: [{ id: "skyrim_se", name: "Skyrim Special Edition", short_description: "An RPG." }],
  cpu_tiers: [{ id: "cpu_mid", label: "Mid-range", example_parts: "Ryzen 5 7600" }],
  gpu_tiers: [{ id: "gpu_upper_mid", label: "Upper-mid", example_parts: "RTX 4070" }],
  ram_tiers: [{ id: "ram_16", label: "16 GB", example_parts: "16 GB" }],
  resolutions: [{ id: "1080p", label: "1920x1080", example_parts: "1080p" }],
  mod_categories: [
    { id: "graphics_overhaul", label: "Graphics/shader overhaul", description: "ENB etc." },
  ],
};

const MODS = {
  game_id: "skyrim_se",
  mods: [{ id: "skyrim_enb", name: "ENB graphics overhaul", category_id: "graphics_overhaul", note: "" }],
};

const PREDICTION = {
  game_id: "skyrim_se",
  predicted_fps: 72.5,
  low_fps: 65,
  high_fps: 80,
  feature_importance: [{ label: "GPU tier", importance: 0.5 }],
  model_version: "1.0.0",
  disclaimer: "This is an estimate, not a simulation or measurement of actual gameplay.",
};

function renderHome() {
  return render(
    <MemoryRouter>
      <Home />
    </MemoryRouter>
  );
}

describe("Home", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("shows validation errors when submitting with nothing selected", async () => {
    vi.spyOn(api, "fetchCatalog").mockResolvedValue(CATALOG as never);

    renderHome();
    await screen.findByText(/select a game/i);

    fireEvent.click(screen.getByRole("button", { name: /get estimated fps/i }));

    expect(await screen.findByText("Pick a game.")).toBeInTheDocument();
    expect(screen.getByText("Pick a CPU tier.")).toBeInTheDocument();
  });

  it("submits a valid selection and renders the prediction", async () => {
    vi.spyOn(api, "fetchCatalog").mockResolvedValue(CATALOG as never);
    vi.spyOn(api, "fetchGameMods").mockResolvedValue(MODS as never);
    const predictSpy = vi.spyOn(api, "predictFps").mockResolvedValue(PREDICTION as never);

    renderHome();
    await screen.findByText(/select a game/i);

    fireEvent.change(screen.getByLabelText(/^game$/i), { target: { value: "skyrim_se" } });
    await screen.findByText(/enb graphics overhaul/i);

    fireEvent.change(screen.getByLabelText(/^cpu$/i), { target: { value: "cpu_mid" } });
    fireEvent.change(screen.getByLabelText(/^gpu$/i), { target: { value: "gpu_upper_mid" } });
    fireEvent.change(screen.getByLabelText(/system ram/i), { target: { value: "ram_16" } });
    fireEvent.change(screen.getByLabelText(/resolution/i), { target: { value: "1080p" } });

    fireEvent.click(screen.getByRole("button", { name: /get estimated fps/i }));

    await waitFor(() => expect(predictSpy).toHaveBeenCalledWith({
      game_id: "skyrim_se",
      cpu_tier: "cpu_mid",
      gpu_tier: "gpu_upper_mid",
      ram_tier: "ram_16",
      resolution: "1080p",
      mod_ids: [],
    }));

    expect(await screen.findByTestId("results-panel")).toBeInTheDocument();
    expect(screen.getByText("72.5")).toBeInTheDocument();
  });

  it("shows a retry-able error banner when the catalog fails to load", async () => {
    vi.spyOn(api, "fetchCatalog").mockRejectedValue(new api.ApiError("network down", 0));

    renderHome();

    expect(await screen.findByTestId("error-banner")).toHaveTextContent("network down");
  });
});
