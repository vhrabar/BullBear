// Combine CRA and Vite env variables
const env = (() => {
  // Vite
  if (typeof import.meta !== "undefined" && import.meta.env?.VITE_ENV) {
    return import.meta.env.VITE_ENV;
  }
  // Fallback: if CRA replaced REACT_APP_ENV at build time
  if (typeof process !== "undefined" && process.env?.REACT_APP_ENV) {
    return process.env.REACT_APP_ENV;
  }
  return "development"; // default
})();
export const MICROSOFT_OAUTH_URL =
  env === "production"
    ? "https://api.bull-bear.app/auth/microsoft/login"
    : "http://localhost:8000/auth/microsoft/login";

export const GOOGLE_OAUTH_URL =
  env === "production"
    ? "https://api.bull-bear.app/auth/google/login"
    : "http://localhost:8000/auth/google/login";



export const IS_PRODUCTION = env === "production";
