import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ["lucide-react"],
  webpack: (config) => {
    config.resolve.symlinks = false;
    config.resolve.modules = [
      path.resolve(__dirname, "node_modules"),
      "node_modules",
    ];
    config.resolve.alias = {
      ...(config.resolve.alias || {}),
      "@": path.resolve(__dirname, "src"),
      "lucide-react": path.resolve(__dirname, "node_modules/lucide-react"),
      "recharts": path.resolve(__dirname, "node_modules/recharts"),
      "lightweight-charts": path.resolve(__dirname, "node_modules/lightweight-charts"),
      "axios": path.resolve(__dirname, "node_modules/axios"),
      "clsx": path.resolve(__dirname, "node_modules/clsx"),
      "tailwind-merge": path.resolve(__dirname, "node_modules/tailwind-merge"),
    };
    return config;
  },
};

export default nextConfig;
