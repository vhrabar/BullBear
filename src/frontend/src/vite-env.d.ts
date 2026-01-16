interface ImportMetaEnv {
  readonly VITE_ENV?: "development" | "production";
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}