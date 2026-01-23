let dotenv;
if (typeof process !== "undefined" && process.versions != null && process.versions.node != null) {
  dotenv = await import("dotenv");
  dotenv.config();
}

const env = typeof process !== "undefined" && process.env?.NODE_ENV?.trim() || "development";

export const MICROSOFT_OAUTH_URL =
  env === "production"
    ? "https://api.bull-bear.app/auth/microsoft/login/"
    : "http://localhost:8000/auth/microsoft/login/";

export const GOOGLE_OAUTH_URL =
  env === "production"
    ? "https://api.bull-bear.app/auth/google/login/"
    : "http://localhost:8000/auth/google/login/";
