
import { Bell, LogOut, Menu, Search, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function Topbar({ onMenuClick }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/", { replace: true });
  }

  const displayName = user?.username || user?.email || "User";
  const initial = displayName.charAt(0).toUpperCase();

  return (
    <header className="topbar">
      <button
        className="icon-button mobile-menu"
        onClick={onMenuClick}
        aria-label="Open menu"
      >
        <Menu size={21} />
      </button>

      <div className="global-search">
        <Search size={18} />
        <input aria-label="Search CRM" placeholder="Search anything..." />
        <kbd>Ctrl K</kbd>
      </div>

      <div className="topbar-actions">
        <button
          className="ai-button"
          type="button"
          onClick={() => navigate("/assistant")}
        >
          <Sparkles size={16} />
          <span>AI Assistant</span>
        </button>

        <button
          className="icon-button notification-button"
          type="button"
          aria-label="Notifications"
          onClick={() => navigate("/notifications")}
        >
          <Bell size={19} />
        </button>

        <div className="topbar-user">
          <div className="topbar-avatar" title={displayName}>
            {initial}
          </div>
          <span className="topbar-user-name">{displayName}</span>
        </div>

        <button
          className="logout-button"
          type="button"
          onClick={handleLogout}
          title="Log out"
        >
          <LogOut size={17} />
          <span>Logout</span>
        </button>
      </div>
    </header>
  );
}
