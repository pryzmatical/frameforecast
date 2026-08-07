import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    include: ["src/tests/**/*.test.ts", "src/tests/**/*.test.tsx"],
    setupFiles: ["./src/tests/setup.ts"],
    // The default "forks" pool hangs in some sandboxed/WSL environments;
    // "threads" is faster to start here and behaves the same for these tests.
    pool: "threads",
  },
});
