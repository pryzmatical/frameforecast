import type { TierOption } from "../types";

interface TierSelectProps {
  label: string;
  options: TierOption[];
  value: string;
  onChange: (value: string) => void;
  error?: string;
}

export function TierSelect({ label, options, value, onChange, error }: TierSelectProps) {
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span className="text-gray-300">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`rounded-md border bg-[#16171d] px-3 py-2 text-gray-100 outline-none focus:border-purple-400 ${
          error ? "border-red-500" : "border-white/10"
        }`}
      >
        <option value="" disabled>
          Select {label.toLowerCase()}&hellip;
        </option>
        {options.map((opt) => (
          <option key={opt.id} value={opt.id}>
            {opt.label} ({opt.example_parts})
          </option>
        ))}
      </select>
      {error && <span className="text-xs text-red-400">{error}</span>}
    </label>
  );
}
