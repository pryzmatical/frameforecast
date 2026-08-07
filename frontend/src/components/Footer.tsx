import { Link } from "react-router-dom";

export function Footer() {
  return (
    <footer className="border-t border-white/10 px-4 py-6 text-center text-xs text-gray-500">
      <p className="mx-auto max-w-2xl">
        FrameForecast is an independent portfolio project. It produces an{" "}
        <strong className="text-gray-400">estimate</strong> from a small trained model, not a
        simulation or measurement of real gameplay. It is not affiliated with, endorsed by, or
        sponsored by any game publisher, GPU/CPU vendor, or mod author/platform referenced in this
        app. NVIDIA, AMD, and Intel are trademarks of their respective owners, as are the game
        titles listed here. See{" "}
        <Link to="/methodology" className="underline hover:text-gray-300">
          Methodology
        </Link>{" "}
        for details.
      </p>
    </footer>
  );
}
