export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch("/api" + path, options);
  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      message =
        typeof body.detail === "string"
          ? body.detail
          : JSON.stringify(body.detail);
    } catch {
      /* keep status */
    }
    throw new Error(message);
  }
  return res.json() as Promise<T>;
}
export const categories = [
  "UPI & Payments",
  "Credit Cards",
  "Account Access",
  "Mobile Banking",
  "Loans",
  "Customer Support",
  "Fraud & Security",
  "Other",
];
export function query(values: Record<string, string | number>) {
  const params = new URLSearchParams();
  Object.entries(values).forEach(([k, v]) => {
    if (v !== "") params.set(k, String(v));
  });
  return "?" + params.toString();
}
