import { useEffect, useMemo, useState } from "react";
import { ApiError, fetchCatalog, fetchGameMods, predictFps } from "../lib/api";
import type { Catalog, GameMods, PredictResponse } from "../types";
import { TierSelect } from "../components/TierSelect";
import { ModPicker } from "../components/ModPicker";
import { ResultsPanel } from "../components/ResultsPanel";
import { ErrorBanner } from "../components/ErrorBanner";

interface FormState {
  gameId: string;
  cpuTier: string;
  gpuTier: string;
  ramTier: string;
  resolution: string;
  modIds: string[];
}

const initialForm: FormState = {
  gameId: "",
  cpuTier: "",
  gpuTier: "",
  ramTier: "",
  resolution: "",
  modIds: [],
};

export function Home() {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [catalogError, setCatalogError] = useState<string | null>(null);
  const [catalogLoading, setCatalogLoading] = useState(true);

  const [gameMods, setGameMods] = useState<GameMods | null>(null);
  const [modsLoading, setModsLoading] = useState(false);

  const [form, setForm] = useState<FormState>(initialForm);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const [result, setResult] = useState<PredictResponse | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const loadCatalog = () => {
    setCatalogLoading(true);
    setCatalogError(null);
    fetchCatalog()
      .then(setCatalog)
      .catch((err: unknown) => {
        setCatalogError(err instanceof ApiError ? err.message : "Failed to load form data.");
      })
      .finally(() => setCatalogLoading(false));
  };

  useEffect(loadCatalog, []);

  useEffect(() => {
    if (!form.gameId) {
      setGameMods(null);
      return;
    }
    setModsLoading(true);
    fetchGameMods(form.gameId)
      .then(setGameMods)
      .catch(() => setGameMods({ game_id: form.gameId, mods: [] }))
      .finally(() => setModsLoading(false));
  }, [form.gameId]);

  const selectedGame = useMemo(
    () => catalog?.games.find((g) => g.id === form.gameId) ?? null,
    [catalog, form.gameId]
  );

  function updateField<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({
      ...prev,
      [key]: value,
      ...(key === "gameId" ? { modIds: [] } : {}),
    }));
    setFieldErrors((prev) => ({ ...prev, [key]: "" }));
    setResult(null);
  }

  function toggleMod(modId: string) {
    setForm((prev) => ({
      ...prev,
      modIds: prev.modIds.includes(modId)
        ? prev.modIds.filter((id) => id !== modId)
        : [...prev.modIds, modId],
    }));
  }

  function validate(): boolean {
    const errors: Record<string, string> = {};
    if (!form.gameId) errors.gameId = "Pick a game.";
    if (!form.cpuTier) errors.cpuTier = "Pick a CPU tier.";
    if (!form.gpuTier) errors.gpuTier = "Pick a GPU tier.";
    if (!form.ramTier) errors.ramTier = "Pick a RAM amount.";
    if (!form.resolution) errors.resolution = "Pick a resolution.";
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitError(null);
    setResult(null);
    if (!validate()) return;

    setSubmitting(true);
    try {
      const prediction = await predictFps({
        game_id: form.gameId,
        cpu_tier: form.cpuTier,
        gpu_tier: form.gpuTier,
        ram_tier: form.ramTier,
        resolution: form.resolution,
        mod_ids: form.modIds,
      });
      setResult(prediction);
    } catch (err) {
      setSubmitError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  }

  if (catalogLoading) {
    return <p className="text-sm text-gray-400">Loading form&hellip;</p>;
  }

  if (catalogError || !catalog) {
    return <ErrorBanner message={catalogError ?? "Failed to load form data."} onRetry={loadCatalog} />;
  }

  return (
    <div className="flex flex-col gap-8">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <label className="flex flex-col gap-1 text-sm sm:col-span-2">
            <span className="text-gray-300">Game</span>
            <select
              value={form.gameId}
              onChange={(e) => updateField("gameId", e.target.value)}
              className={`rounded-md border bg-[#16171d] px-3 py-2 text-gray-100 outline-none focus:border-purple-400 ${
                fieldErrors.gameId ? "border-red-500" : "border-white/10"
              }`}
            >
              <option value="" disabled>
                Select a game&hellip;
              </option>
              {catalog.games.map((g) => (
                <option key={g.id} value={g.id}>
                  {g.name}
                </option>
              ))}
            </select>
            {selectedGame && <span className="text-xs text-gray-500">{selectedGame.short_description}</span>}
            {fieldErrors.gameId && <span className="text-xs text-red-400">{fieldErrors.gameId}</span>}
          </label>

          <TierSelect
            label="CPU"
            options={catalog.cpu_tiers}
            value={form.cpuTier}
            onChange={(v) => updateField("cpuTier", v)}
            error={fieldErrors.cpuTier}
          />
          <TierSelect
            label="GPU"
            options={catalog.gpu_tiers}
            value={form.gpuTier}
            onChange={(v) => updateField("gpuTier", v)}
            error={fieldErrors.gpuTier}
          />
          <TierSelect
            label="System RAM"
            options={catalog.ram_tiers}
            value={form.ramTier}
            onChange={(v) => updateField("ramTier", v)}
            error={fieldErrors.ramTier}
          />
          <TierSelect
            label="Resolution"
            options={catalog.resolutions}
            value={form.resolution}
            onChange={(v) => updateField("resolution", v)}
            error={fieldErrors.resolution}
          />
        </div>

        {form.gameId && (
          <div>
            {modsLoading ? (
              <p className="text-sm text-gray-500">Loading mods for {selectedGame?.name}&hellip;</p>
            ) : (
              <ModPicker
                mods={gameMods?.mods ?? []}
                categories={catalog.mod_categories}
                selected={form.modIds}
                onToggle={toggleMod}
              />
            )}
          </div>
        )}

        {submitError && <ErrorBanner message={submitError} />}

        <button
          type="submit"
          disabled={submitting}
          className="self-start rounded-md bg-purple-500 px-4 py-2 text-sm font-medium text-white hover:bg-purple-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {submitting ? "Estimating…" : "Get estimated FPS"}
        </button>
      </form>

      {result && selectedGame && <ResultsPanel result={result} gameName={selectedGame.name} />}
    </div>
  );
}
