/** @type {import('next').NextConfig} */

// In local dev, the backend runs on the host at localhost:8000.
// In docker-compose, it's reached via the service name "backend".
const BACKEND_URL = process.env.BACKEND_INTERNAL_URL || "http://localhost:8000";

const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: "http", hostname: "localhost", port: "8000", pathname: "/uploads/**" },
      { protocol: "http", hostname: "backend", port: "8000", pathname: "/uploads/**" },
    ],
  },
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${BACKEND_URL}/api/:path*` },
      { source: "/uploads/:path*", destination: `${BACKEND_URL}/uploads/:path*` },
    ];
  },
};

export default nextConfig;
