const env = import.meta.env.MODE; // "development" | "production"

export const MICROSOFT_OAUTH_URL =
  env === "production"
    ? "https://api.bull-bear.app/auth/microsoft/login/"
    : "http://localhost:8000/auth/microsoft/login/";

export const GOOGLE_OAUTH_URL =
  env === "production"
    ? "https://api.bull-bear.app/auth/google/login/"
    : "http://localhost:8000/auth/google/login/";
