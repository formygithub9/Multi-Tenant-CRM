
import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="not-found">
      <span>404</span>
      <h1>Page not found</h1>
      <p>The page you're looking for doesn't exist.</p>
      <Link className="primary-button" to="/dashboard">Back to dashboard</Link>
    </div>
  );
}
