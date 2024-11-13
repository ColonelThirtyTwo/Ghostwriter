import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import sourcemaps from "rollup-plugin-sourcemaps2";
import { resolve } from 'path';

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
    return {
        plugins: [react()],
        base: "/static/",
        build: {
            rollupOptions: {
                plugins: [sourcemaps()],
                input: {
                    "cvss": resolve(__dirname, "./src/cvss/ui.js"),
                    "forms": resolve(__dirname, "./src/forms/index.ts"),
                },
                output: {
                    entryFileNames: "assets/[name].js",
                    //chunkFileNames: "assets/[name].js",
                    assetFileNames: "assets/[name].[ext]",
                    sourcemapIgnoreList: false,
                },
            },
            sourcemap: mode === "development",
            watch: mode === "development" ? {
                chokidar: {
                    // Needed for docker on WSL
                    usePolling: true,
                },
            } : null,
        },
        css: {
            preprocessorOptions: {
                scss: {
                    api: "modern",
                    quietDeps: true,
                },
            },
        },
    };
});
