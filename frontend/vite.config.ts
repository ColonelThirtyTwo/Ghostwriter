import { defineConfig, UserConfig } from "vite";
import react from "@vitejs/plugin-react";
import sourcemaps from "rollup-plugin-sourcemaps2";
import { resolve } from "path";

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
    return {
        plugins: [react()],
        base: "/static/",
        build: {
            rollupOptions: {
                plugins: [sourcemaps()],
                input: {
                    cvss: resolve(__dirname, "./src/cvss/ui.js"),
                    forms: resolve(__dirname, "./src/forms/index.ts"),
                    observation_form: resolve(
                        __dirname,
                        "./src/collab_forms/forms/observation.tsx"
                    ),
                    common_styles: resolve(
                        __dirname,
                        "./src/common_styles.scss"
                    ),
                },
                output: {
                    entryFileNames: "assets/[name].js",
                    //chunkFileNames: "assets/[name].js",
                    assetFileNames: "assets/[name].[ext]",
                    sourcemapIgnoreList: false,

                    manualChunks: (id: string) => {
                        //console.log(id);
                        if (id.includes("node_modules")) return "vendor";
                        else if (
                            id.includes("/collab_forms/") &&
                            !id.includes("/collab_forms/forms/")
                        )
                            return "collab_common";
                    },
                },
            },
            minify: mode !== "development",
            sourcemap: mode === "development",
            watch:
                mode === "development"
                    ? {
                          chokidar: {
                              // Needed for docker on WSL
                              usePolling: true,
                          },
                      }
                    : null,
        },
        css: {
            preprocessorOptions: {
                scss: {
                    api: "modern",
                    quietDeps: true,
                },
            },
        },
    } satisfies UserConfig;
});
