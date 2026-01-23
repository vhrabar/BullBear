/// <reference types="vite/client" />

declare module '*.css' {
  const content: { [className: string]: string };
  export default content;
}

interface ImportMetaEnv {
  readonly VITE_ENV?: "development" | "production";
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}