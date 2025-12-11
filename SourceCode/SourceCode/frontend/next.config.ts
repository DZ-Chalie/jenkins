import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,
  async rewrites() {
    return [
      {
        source: "/api/python/:path*",
        destination: "http://backend:8000/:path*", // Proxy to backend container
      },
    ];
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
      {
        protocol: "https",
        hostname: "dbscthumb-phinf.pstatic.net",
      },
      {
        protocol: "https",
        hostname: "postfiles.pstatic.net",
      },
      {
        protocol: "https",
        hostname: "imgnews.pstatic.net", // Adding news image domain just in case
      },
      {
        protocol: "http",
        hostname: "**",
      },
    ],
  },
};

export default nextConfig;
