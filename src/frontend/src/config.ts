import dotenv from "dotenv";

dotenv.config();

const env = process.env.NODE_ENV?.trim() || "development";

export const MICROSOFT_OAUTH_URL =
  env === "production"
    ? process.env.MICROSOFT_OAUTH_URL_PROD
    : process.env.MICROSOFT_OAUTH_URL_DEV;

export const GOOGLE_OAUTH_URL =
  env === "production"
    ? process.env.GOOGLE_OAUTH_URL_PROD
    : process.env.GOOGLE_OAUTH_URL_DEV;

export const IS_PRODUCTION = env === "production";
