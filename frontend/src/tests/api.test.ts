import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, fetchCatalog, predictFps } from "../lib/api";

function mockFetchOnce(response: Partial<Response> & { json?: () => Promise<unknown> }) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => ({}),
      ...response,
    } as Response)
  );
}

describe("fetchCatalog", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns parsed JSON on success", async () => {
    mockFetchOnce({ json: async () => ({ games: [], cpu_tiers: [] }) });
    const result = await fetchCatalog();
    expect(result).toEqual({ games: [], cpu_tiers: [] });
  });

  it("throws an ApiError with the response detail on a non-ok response", async () => {
    mockFetchOnce({
      ok: false,
      status: 422,
      statusText: "Unprocessable Entity",
      json: async () => ({ detail: "Unknown game_id 'bogus'" }),
    });

    await expect(fetchCatalog()).rejects.toMatchObject({
      message: "Unknown game_id 'bogus'",
      status: 422,
    });
  });

  it("wraps network failures in a friendly ApiError", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValueOnce(new TypeError("Failed to fetch"))
    );

    await expect(fetchCatalog()).rejects.toBeInstanceOf(ApiError);
  });
});

describe("predictFps", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("POSTs the payload and returns the prediction", async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => ({ predicted_fps: 60 }),
    } as Response);
    vi.stubGlobal("fetch", fetchMock);

    const payload = {
      game_id: "skyrim_se",
      cpu_tier: "cpu_mid",
      gpu_tier: "gpu_upper_mid",
      ram_tier: "ram_16",
      resolution: "1080p",
      mod_ids: [],
    };
    const result = await predictFps(payload);

    expect(result).toEqual({ predicted_fps: 60 });
    const [url, init] = fetchMock.mock.calls[0];
    expect(String(url)).toContain("/predict");
    expect(init?.method).toBe("POST");
    expect(JSON.parse(init?.body as string)).toEqual(payload);
  });
});
