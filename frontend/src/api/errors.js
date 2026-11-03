
export function getApiError(error) {
  const data = error.response?.data;

  if (typeof data?.detail === "string") {
    return data.detail;
  }

  if (typeof data?.message === "string") {
    return data.message;
  }

  if (data && typeof data === "object") {
    const messages = Object.values(data)
      .flat()
      .filter((value) => typeof value === "string");

    if (messages.length) {
      return messages.join(" ");
    }
  }

  if (error.response?.status === 401) {
    return "Your session has expired. Please sign in again.";
  }

  if (!error.response) {
    return "Unable to connect to the server. Please try again.";
  }

  return "Something went wrong. Please try again.";
}
