
import { useEffect, useState } from "react";
import { Search, Plus, Users, Pencil, Trash2, X, ChevronLeft, ChevronRight,} from "lucide-react";
import { getCustomers, createCustomer, updateCustomer, deleteCustomer as removeCustomer,} from "../api/customers";
import { getApiError } from "../api/errors";

const emptyForm = { name: "", email: "", phone: "", company: "" };

export default function CustomersPage() {
  const [customers, setCustomers] = useState([]);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [next, setNext] = useState(null);
  const [previous, setPrevious] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function loadCustomers() {
      setLoading(true);
      setError("");

      try {
        const data = await getCustomers({
          page,
          search: search.trim() || undefined,
        });

        if (cancelled) return;

        const results = Array.isArray(data) ? data : data.results || [];

        setCustomers(results);
        setNext(Array.isArray(data) ? null : data.next);
        setPrevious(Array.isArray(data) ? null : data.previous);
      } catch (err) {
        if (!cancelled) {
          setError(getApiError(err));
          setCustomers([]);
          setNext(null);
          setPrevious(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadCustomers();

    return () => {
      cancelled = true;
    };
  }, [page, search, reloadKey]);

  function openCreate() {
    setEditing(null);
    setForm(emptyForm);
    setError("");
    setModalOpen(true);
  }

  function openEdit(customer) {
    setEditing(customer);
    setForm({
      name: customer.name || "",
      email: customer.email || "",
      phone: customer.phone || "",
      company: customer.company || customer.company_name || "",
    });
    setError("");
    setModalOpen(true);
  }

  async function saveCustomer(event) {
    event.preventDefault();
    setSaving(true);
    setError("");

    const payload = {
      name: form.name.trim(),
      email: form.email.trim(),
      phone: form.phone.trim(),
      company: form.company.trim(),
    };

    try {
      if (editing) {
        await updateCustomer(editing.id, payload);
      } else {
        await createCustomer(payload);
      }

      setModalOpen(false);
      setEditing(null);
      setForm(emptyForm);
      setPage(1);
      setReloadKey((key) => key + 1);
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteCustomer(customer) {
    if (!window.confirm(`Delete ${customer.name || "this customer"}?`)) {
      return;
    }

    setError("");

    try {
      await removeCustomer(customer.id);
      setReloadKey((key) => key + 1);
    } catch (err) {
      setError(getApiError(err));
    }
  }

  return (
    <div className="customers-page">
      <div className="customers-heading">
        <div>
          <p className="eyebrow">RELATIONSHIP MANAGEMENT</p>
          <h1>Customers</h1>
          <p className="page-subtitle">
            Manage your customer relationships in one place.
          </p>
        </div>

        <button className="primary-button" onClick={openCreate}>
          <Plus size={17} /> Add customer
        </button>
      </div>

      <section className="panel customers-panel">
        <div className="customers-toolbar">
          <div>
            <h2>All customers</h2>
            <p>Customer directory</p>
          </div>

          <label className="customer-search">
            <Search size={16} />
            <input
              value={search}
              onChange={(event) => {
                setSearch(event.target.value);
                setPage(1);
              }}
              placeholder="Search customers..."
            />
          </label>
        </div>

        {error && <div className="customer-error" role="alert">{error}</div>}

        <div className="customers-table-wrap">
          <table className="deals-table customers-table">
            <thead>
              <tr>
                <th>CUSTOMER</th>
                <th>EMAIL</th>
                <th>PHONE</th>
                <th>COMPANY</th>
                <th>ACTIONS</th>
              </tr>
            </thead>

            <tbody>
              {!loading &&
                customers.map((customer) => (
                  <tr key={customer.id}>
                    <td>
                      <div className="customer-name">
                        <span className="customer-avatar">
                          {(customer.name || "?").charAt(0).toUpperCase()}
                        </span>
                        <strong>{customer.name || "Unnamed"}</strong>
                      </div>
                    </td>
                    <td>{customer.email || "—"}</td>
                    <td>{customer.phone || "—"}</td>
                    <td>{customer.company || customer.company_name || "—"}</td>
                    <td>
                      <div className="customer-actions">
                        <button
                          className="customer-action edit"
                          title="Edit customer"
                          aria-label={`Edit ${customer.name || "customer"}`}
                          onClick={() => openEdit(customer)}
                        >
                          <Pencil size={15} />
                        </button>
                        <button
                          className="customer-action delete"
                          title="Delete customer"
                          aria-label={`Delete ${customer.name || "customer"}`}
                          onClick={() => handleDeleteCustomer(customer)}
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}

              {!loading && customers.length === 0 && (
                <tr>
                  <td colSpan="5" className="customers-empty">
                    <Users size={25} />
                    <strong>No customers found</strong>
                    <span>Add a customer or change your search.</span>
                  </td>
                </tr>
              )}

              {loading && (
                <tr>
                  <td colSpan="5" className="customers-empty">
                    Loading customers...
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="customers-pagination">
          <span>Page {page}</span>
          <div>
            <button
              className="secondary-button"
              disabled={!previous || loading}
              onClick={() => setPage((current) => Math.max(1, current - 1))}
            >
              <ChevronLeft size={15} /> Previous
            </button>
            <button
              className="secondary-button"
              disabled={!next || loading}
              onClick={() => setPage((current) => current + 1)}
            >
              Next <ChevronRight size={15} />
            </button>
          </div>
        </div>
      </section>

      {modalOpen && (
        <div
          className="customer-modal-backdrop"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget && !saving) {
              setModalOpen(false);
            }
          }}
        >
          <form className="customer-modal" onSubmit={saveCustomer}>
            <div className="customer-modal-heading">
              <div>
                <h2>{editing ? "Edit customer" : "Add customer"}</h2>
                <p>Enter the customer's contact details.</p>
              </div>
              <button
                type="button"
                className="icon-button"
                onClick={() => setModalOpen(false)}
                aria-label="Close"
                disabled={saving}
              >
                <X size={20} />
              </button>
            </div>

            {[
              ["name", "Customer name", true],
              ["email", "Email address", false],
              ["phone", "Phone number", false],
              ["company", "Company", false],
            ].map(([field, label, required]) => (
              <label className="customer-field" key={field}>
                <span>{label}{required ? " *" : ""}</span>
                <input
                  required={required}
                  type={field === "email" ? "email" : "text"}
                  value={form[field]}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      [field]: event.target.value,
                    }))
                  }
                  placeholder={label}
                />
              </label>
            ))}

            <div className="customer-modal-actions">
              <button
                type="button"
                className="secondary-button"
                onClick={() => setModalOpen(false)}
                disabled={saving}
              >
                Cancel
              </button>
              <button className="primary-button" disabled={saving}>
                {saving
                  ? "Saving..."
                  : editing
                    ? "Save changes"
                    : "Create customer"}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
