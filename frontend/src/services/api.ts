import axios from "axios";

/**
 * Base Axios instance.
 *
 * In dev, Next.js rewrites /api/* → http://localhost:8000/api/* (see next.config.mjs),
 * so requests can use a relative base URL and avoid CORS entirely.
 * NEXT_PUBLIC_API_BASE_URL can override this for other environments.
 */
export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || "/api/v1",
  timeout: 30000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error?.response?.data?.detail ||
      error?.message ||
      "Unexpected error contacting Vestia API.";
    return Promise.reject(new Error(message));
  }
);

/** Resolve a relative image_path returned by the API to a loadable URL. */
export function uploadUrl(imagePath: string): string {
  const base = process.env.NEXT_PUBLIC_UPLOADS_BASE_URL || "/uploads";
  return `${base}/${imagePath}`;
}

/** Same as uploadUrl, but points at the generated thumbnail. */
export function thumbnailUrl(imagePath: string): string {
  const base = process.env.NEXT_PUBLIC_UPLOADS_BASE_URL || "/uploads";
  const parts = imagePath.split("/");
  const filename = parts.pop() as string;
  const dir = parts.join("/");
  return `${base}/${dir}/thumb_${filename}`;
}
