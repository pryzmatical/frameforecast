import { Link, useLocation } from "react-router-dom";

export function Header() {
  const { pathname } = useLocation();

  return (
    <header className="border-b border-white/10 px-4 py-4">
      <div className="mx-auto flex max-w-4xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <Link to="/" className="block">
          <h1 className="text-lg font-semibold text-gray-100">FrameForecast</h1>
          <p className="text-sm text-gray-500">
            An estimated FPS calculator for hardware + game + mod combinations.
          </p>
        </Link>
        <nav className="flex gap-4 text-sm">
          <Link
            to="/"
            className={pathname === "/" ? "text-gray-100" : "text-gray-400 hover:text-gray-200"}
          >
            Calculator
          </Link>
          <Link
            to="/methodology"
            className={
              pathname === "/methodology" ? "text-gray-100" : "text-gray-400 hover:text-gray-200"
            }
          >
            Methodology
          </Link>
        </nav>
      </div>
    </header>
  );
}
