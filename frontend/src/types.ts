export interface TierOption {
  id: string;
  label: string;
  example_parts: string;
}

export interface GameOption {
  id: string;
  name: string;
  short_description: string;
}

export interface ModOption {
  id: string;
  name: string;
  category_id: string;
  note: string;
}

export interface ModCategory {
  id: string;
  label: string;
  description: string;
}

export interface Catalog {
  games: GameOption[];
  cpu_tiers: TierOption[];
  gpu_tiers: TierOption[];
  ram_tiers: TierOption[];
  resolutions: TierOption[];
  mod_categories: ModCategory[];
}

export interface GameMods {
  game_id: string;
  mods: ModOption[];
}

export interface PredictRequest {
  game_id: string;
  cpu_tier: string;
  gpu_tier: string;
  ram_tier: string;
  resolution: string;
  mod_ids: string[];
}

export interface FeatureImportance {
  label: string;
  importance: number;
}

export interface PredictResponse {
  game_id: string;
  predicted_fps: number;
  low_fps: number;
  high_fps: number;
  feature_importance: FeatureImportance[];
  model_version: string;
  disclaimer: string;
}
