import type { ModCategory, ModOption } from "../types";

interface ModPickerProps {
  mods: ModOption[];
  categories: ModCategory[];
  selected: string[];
  onToggle: (modId: string) => void;
}

export function ModPicker({ mods, categories, selected, onToggle }: ModPickerProps) {
  if (mods.length === 0) {
    return <p className="text-sm text-gray-500">No mods found for this game.</p>;
  }

  const categoryLabel = (id: string) => categories.find((c) => c.id === id)?.label ?? id;

  return (
    <fieldset className="flex flex-col gap-2">
      <legend className="mb-1 text-sm text-gray-300">
        Mods to include <span className="text-gray-500">(optional, pick any number)</span>
      </legend>
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        {mods.map((mod) => (
          <label
            key={mod.id}
            className="flex cursor-pointer items-start gap-2 rounded-md border border-white/10 bg-[#16171d] px-3 py-2 text-sm hover:border-purple-400/50"
          >
            <input
              type="checkbox"
              checked={selected.includes(mod.id)}
              onChange={() => onToggle(mod.id)}
              className="mt-1"
            />
            <span>
              <span className="block text-gray-100">{mod.name}</span>
              <span className="block text-xs text-gray-500">{categoryLabel(mod.category_id)}</span>
            </span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}
