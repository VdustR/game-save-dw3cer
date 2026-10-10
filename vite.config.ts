import { defineConfig } from "vite-plus";
export default defineConfig({
  build: { target: "es2022" },
  lint: { options: { typeAware: true }, ignorePatterns: ["public/**"] },
  fmt: { ignorePatterns: ["public/**", "ACCEPTANCE_NATIVE.json", "ACCEPTANCE_BROWSER.json"] },
  test: { include: ["src/**/*.test.ts"] },
});
