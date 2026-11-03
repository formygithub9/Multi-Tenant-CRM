import api from "./client";

export async function getDashboardSummary() {
  const response = await api.get("/dashboard/summary/");
  return response.data;
}
