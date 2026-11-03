
import { useEffect, useState } from "react";
import { Users, UserRound, Target, TrendingUp, ArrowUpRight, ArrowDownRight, Plus, CalendarDays, MoreHorizontal, Clock3, CheckCircle2, Phone, Mail, Building2,} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getDashboardSummary } from "../api/dashboard";
import { getApiError } from "../api/errors";

const metricConfig = [
  { key: "total_customers", label: "Total Customers", icon: Users, color: "purple" },
  { key: "active_leads", label: "Active Leads", icon: Target, color: "blue" },
  { key: "open_deals", label: "Open Deals", icon: TrendingUp, color: "green" },
  { key: "total_contacts", label: "Total Contacts", icon: UserRound, color: "orange" },
];

const activityIcons = {
  call: Phone,
  email: Mail,
  customer: Building2,
  deal: CheckCircle2,
};

function SectionHeading({ title, subtitle, action }) {
  return (
    <div className="section-heading">
      <div>
        <h2>{title}</h2>
        <p>{subtitle}</p>
      </div>
      {action}
    </div>
  );
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
      setLoading(true);
      setError("");

      try {
        const result = await getDashboardSummary();
        if (!cancelled) setData(result);
      } catch (err) {
        if (!cancelled) setError(getApiError(err));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadDashboard();

    return () => {
      cancelled = true;
    };
  }, []);

  const summary = data?.metrics || data?.summary || data || {};
  const deals = data?.recent_deals || data?.deals || [];
  const activities = data?.recent_activities || data?.activities || [];
  const tasks = data?.tasks || [];

  return (
    <div className="dashboard-page">
      <div className="dashboard-heading">
        <div>
          <p className="eyebrow">OVERVIEW</p>
          <h1>Business overview <span>✦</span></h1>
          <p className="page-subtitle">
            Here's what's happening with your business today.
          </p>
        </div>
        <div className="dashboard-actions">
          <button className="secondary-button" type="button">
            <CalendarDays size={16} /> Overview
          </button>
          <button
            className="primary-button"
            type="button"
            onClick={() => navigate("/customers")}
          >
            <Plus size={17} /> View customers
          </button>
        </div>
      </div>

      {error && (
        <div className="customer-error" role="alert">
          {error}
        </div>
      )}

      <div className="metrics-grid">
        {metricConfig.map((metric) => {
          const Icon = metric.icon;
          const value = summary[metric.key];

          return (
            <article className="metric-card" key={metric.key}>
              <div className="metric-top">
                <span>{metric.label}</span>
                <span className={`metric-icon ${metric.color}`}>
                  <Icon size={19} />
                </span>
              </div>
              <div className="metric-value">
                {loading ? "—" : Number.isFinite(Number(value)) && value != null
                  ? Number(value).toLocaleString()
                  : "—"}
              </div>
              <div className="metric-footer">
                <span>Live data</span>
                <span>From your workspace</span>
              </div>
            </article>
          );
        })}
      </div>

      {loading && (
        <p className="page-subtitle">Loading dashboard data...</p>
      )}

      <div className="dashboard-main-grid">
        <section className="panel deals-panel">
          <SectionHeading
            title="Recent deals"
            subtitle="Your latest sales opportunities"
            action={
              <button
                className="text-button"
                type="button"
                onClick={() => navigate("/deals")}
              >
                View all <ArrowUpRight size={15} />
              </button>
            }
          />
          <div className="deals-table-wrap">
            <table className="deals-table">
              <thead>
                <tr>
                  <th>DEAL / CONTACT</th>
                  <th>VALUE</th>
                  <th>STAGE</th>
                  <th>PROGRESS</th>
                </tr>
              </thead>
              <tbody>
                {!loading && deals.map((deal, index) => {
                  const progress = Math.min(
                    100,
                    Math.max(0, Number(deal.progress) || 0)
                  );

                  return (
                    <tr key={deal.id ?? index}>
                      <td>
                        <strong>{deal.company || deal.name || deal.title || "—"}</strong>
                        <span>{deal.contact_name || deal.person || "—"}</span>
                      </td>
                      <td className="deal-value">
                        {deal.value ?? deal.amount ?? "—"}
                      </td>
                      <td>
                        <span className="stage-badge purple">
                          {deal.stage || deal.status || "—"}
                        </span>
                      </td>
                      <td>
                        <div className="progress-cell">
                          <div className="progress-track">
                            <div
                              className="progress-fill purple"
                              style={{ width: `${progress}%` }}
                            />
                          </div>
                          <span>{progress}%</span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
                {!loading && deals.length === 0 && (
                  <tr>
                    <td colSpan="4" className="customers-empty">
                      No recent deals available.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="panel activity-panel">
          <SectionHeading
            title="Recent activity"
            subtitle="Latest workspace updates"
            action={
              <button
                className="icon-button"
                type="button"
                aria-label="More activity options"
              >
                <MoreHorizontal size={19} />
              </button>
            }
          />
          <div className="activity-list">
            {!loading && activities.map((activity, index) => {
              const type = String(activity.type || activity.action || "").toLowerCase();
              const Icon = Object.entries(activityIcons).find(([key]) =>
                type.includes(key)
              )?.[1] || Clock3;

              return (
                <div className="activity-item" key={activity.id ?? index}>
                  <span className="activity-icon blue">
                    <Icon size={16} />
                  </span>
                  <div className="activity-content">
                    <strong>
                      {activity.title || activity.description || activity.action || "Activity"}
                    </strong>
                    <p>{activity.detail || activity.subject || ""}</p>
                    <span>
                      <Clock3 size={12} /> {activity.time || activity.created_at || "—"}
                    </span>
                  </div>
                </div>
              );
            })}
            {!loading && activities.length === 0 && (
              <p className="page-subtitle">No recent activity available.</p>
            )}
          </div>
        </section>
      </div>

      <section className="panel tasks-panel">
        <SectionHeading
          title="Your tasks"
          subtitle="Tasks and follow-ups"
          action={
            <button
              className="text-button"
              type="button"
              onClick={() => navigate("/activities")}
            >
              View all <ArrowUpRight size={15} />
            </button>
          }
        />
        <div className="tasks-list">
          {!loading && tasks.map((task, index) => (
            <label
              className={`task-item ${task.is_completed || task.done ? "task-done" : ""}`}
              key={task.id ?? index}
            >
              <input
                type="checkbox"
                checked={Boolean(task.is_completed ?? task.done)}
                readOnly
              />
              <span className="task-copy">
                <strong>{task.title || task.name || "Untitled task"}</strong>
                <small>
                  <Clock3 size={13} /> {task.due_at || task.time || "No due date"}
                </small>
              </span>
            </label>
          ))}
          {!loading && tasks.length === 0 && (
            <p className="page-subtitle">No tasks available.</p>
          )}
        </div>
      </section>

      <p className="demo-notice">
        Dashboard values are loaded from the configured API. Missing fields appear as dashes.
      </p>
    </div>
  );
}
