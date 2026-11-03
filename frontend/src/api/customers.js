
import api from "./client";

function normalizeCustomer(customer) {
  if (!customer) return customer;

  return {
    ...customer,
    name: customer.contact_name ?? customer.name ?? "",
    company: customer.company_name ?? customer.company ?? "",
    phone: customer.mobile ?? customer.phone ?? "",
  };
}

function unwrapResponse(response) {
  return response?.data?.data ?? response?.data;
}

export async function getCustomers(params = {}) {
  const response = await api.get("/customers/", { params });
  const result = unwrapResponse(response);

  if (Array.isArray(result)) {
    return result.map(normalizeCustomer);
  }

  return {
    ...result,
    results: (result?.results ?? []).map(normalizeCustomer),
  };
}

export async function getCustomer(customerId) {
  const response = await api.get(`/customers/${customerId}/`);
  return normalizeCustomer(unwrapResponse(response));
}

function toApiPayload(customerData) {
  return {
    contact_name: customerData.name ?? customerData.contact_name ?? "",
    email: customerData.email ?? "",
    mobile: customerData.phone ?? customerData.mobile ?? "",
    company_name: customerData.company ?? customerData.company_name ?? "",
  };
}

export async function createCustomer(customerData) {
  const response = await api.post(
    "/customers/",
    toApiPayload(customerData)
  );

  return normalizeCustomer(unwrapResponse(response));
}

export async function updateCustomer(customerId, customerData) {
  const response = await api.patch(
    `/customers/${customerId}/`,
    toApiPayload(customerData)
  );

  return normalizeCustomer(unwrapResponse(response));
}

export async function deleteCustomer(customerId) {
  const response = await api.delete(`/customers/${customerId}/`);
  return response.data;
}
