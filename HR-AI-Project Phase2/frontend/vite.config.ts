import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import postcssNesting from 'postcss-nesting';
import eslintPlugin from 'vite-plugin-eslint';

/** @type {import('vite').UserConfig} */
export default ({ mode }) => {
    // Extends 'process.env.*' with VITE_*-variables from '.env.(mode=production|development)'
    process.env = { ...process.env, ...loadEnv(mode, process.cwd()) };
    // https://vitejs.dev/config/
    return defineConfig({
        plugins: [react(), eslintPlugin()],
        build: {
            outDir: "../frontend/server/dist",
            emptyOutDir: true,
            sourcemap: true
        },
        test: {
            // 👋 add the line below to add jsdom to vite
            environment: 'jsdom',
            globals: true,
            setupFiles: './tests/setup.ts',
        },
        server: {
            proxy: {
                "/api": {
                    target: "http://127.0.0.1:5000",
                    secure: false
                }
            }
        },
        css: {
            postcss: {
                plugins: [
                    postcssNesting
                ],
            },
        }
    })
};
