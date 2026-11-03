import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Boxes, Eye, EyeOff, LockKeyhole, Mail, Phone } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const [companyMobile, setCompanyMobile] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login({
        company_mobile: companyMobile.trim(),
        email: email.trim(),
        password,
      });

      navigate(location.state?.from?.pathname || "/dashboard", {
        replace: true,
      });
    } catch (err) {
      const data = err.response?.data;
      const validationErrors = Object.values(data?.errors || {})
        .flat()
        .filter((value) => typeof value === "string")
        .join(" ");

      const responseErrors = Object.values(data || {})
        .filter((value) => typeof value === "string")
        .join(" ");

      setError(
        data?.message ||
          data?.detail ||
          validationErrors ||
          responseErrors ||
          err.message ||
          "Unable to sign in. Please check your credentials and try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-brand-panel">
        <div className="login-brand">
          <div className="brand-mark">
            <Boxes size={23} />
          </div>
          <strong>Orbit CRM</strong>
        </div>

        <div className="login-promo">
          <span className="promo-label">
            ONE PLATFORM. YOUR WHOLE BUSINESS.
          </span>

          <h1>Build stronger relationships. Grow with clarity.</h1>

          <p>
            Bring customers, sales, and everyday business operations together
            in one organized workspace.
          </p>

          <div className="promo-decoration">
            <div className="promo-window">
              <div className="promo-window-bar">
                <i />
                <i />
                <i />
              </div>

              <div className="promo-window-content">
                <div />
                <div />
                <div />
                <div />
              </div>
            </div>
          </div>
        </div>

        <p className="login-copyright">Multi-Tenant CRM Platform</p>
      </section>

      <section className="login-form-panel">
        <div className="login-form-wrap">
          <div className="login-mobile-brand">
            <div className="brand-mark">
              <Boxes size={22} />
            </div>
            <strong>Orbit CRM</strong>
          </div>

          <p className="eyebrow">WELCOME BACK</p>
          <h2>Sign in to your account</h2>

          <p className="login-subtitle">
            Enter your credentials to access your workspace.
          </p>

          <form className="login-form" onSubmit={handleSubmit}>
            <label htmlFor="companyMobile">Company mobile</label>
            <div className="input-wrap">
              <Phone size={18} />

              <input
                id="companyMobile"
                type="tel"
                placeholder="Registered company mobile"
                autoComplete="tel"
                value={companyMobile}
                onChange={(event) => setCompanyMobile(event.target.value)}
                required
              />
            </div>

            <label htmlFor="email">Email address</label>
            <div className="input-wrap">
              <Mail size={18} />

              <input
                id="email"
                type="email"
                placeholder="you@company.com"
                autoComplete="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </div>

            <label htmlFor="password">Password</label>
            <div className="input-wrap">
              <LockKeyhole size={18} />

              <input
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="Enter your password"
                autoComplete="current-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />

              <button
                className="password-toggle"
                type="button"
                onClick={() => setShowPassword((current) => !current)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>

            {error && (
              <p role="alert" className="login-error">
                {error}
              </p>
            )}

            <button
              className="primary-button login-submit"
              type="submit"
              disabled={loading}
            >
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </form>

          <p className="login-footnote">
            Secure access to your business workspace.
          </p>
        </div>
      </section>
    </main>
  );
}