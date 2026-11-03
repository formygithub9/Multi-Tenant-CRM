
import { NavLink } from "react-router-dom";
import {
  Activity, Bell, Boxes, BriefcaseBusiness, Building2,
  CalendarDays, ChartNoAxesCombined, CircleDollarSign,
  ClipboardList, ContactRound, FileText, LayoutDashboard,
  Package, Settings, ShoppingCart, Users, Truck, X
} from "lucide-react";

const sections = [
  {
    title: "WORKSPACE",
    items: [
      { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
      { label: "Customers", path: "/customers", icon: Building2 },
      { label: "Contacts", path: "/contacts", icon: ContactRound },
      { label: "Leads", path: "/leads", icon: Users },
      { label: "Deals", path: "/deals", icon: BriefcaseBusiness },
      { label: "Activities", path: "/activities", icon: CalendarDays },
    ],
  },
  {
    title: "BUSINESS",
    items: [
      { label: "Vendors", path: "/vendors", icon: Truck },
      { label: "Products", path: "/products", icon: Package },
      { label: "Quotes", path: "/quotes", icon: FileText },
      { label: "Orders", path: "/orders", icon: ShoppingCart },
      { label: "Invoices", path: "/invoices", icon: ClipboardList },
      { label: "Payments", path: "/payments", icon: CircleDollarSign },
    ],
  },
  {
    title: "SYSTEM",
    items: [
      { label: "Analytics", path: "/analytics", icon: ChartNoAxesCombined },
      { label: "Notifications", path: "/notifications", icon: Bell },
      { label: "Team & Roles", path: "/team", icon: Users },
      { label: "Settings", path: "/settings", icon: Settings },
    ],
  },
];

export default function Sidebar({ open, onClose }) {
  return (
    <>
      {open && <button className="sidebar-backdrop" onClick={onClose} aria-label="Close menu" />}
      <aside className={`sidebar ${open ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-mark"><Boxes size={22} /></div>
          <div>
            <strong>Orbit CRM</strong>
            <span>BUSINESS PLATFORM</span>
          </div>
          <button className="icon-button sidebar-close" onClick={onClose} aria-label="Close sidebar">
            <X size={19} />
          </button>
        </div>

        <div className="workspace-switcher">
          <div className="workspace-icon">W</div>
          <div className="workspace-details">
            <strong>Workspace</strong>
            <span>Current organization</span>
          </div>
          <Activity size={16} className="muted-icon" />
        </div>

        <nav className="sidebar-nav">
          {sections.map((section) => (
            <div className="nav-section" key={section.title}>
              <p className="nav-section-title">{section.title}</p>
              {section.items.map(({ label, path, icon: Icon }) => (
                <NavLink
                  key={path}
                  to={path}
                  onClick={onClose}
                  className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
                >
                  <Icon size={18} strokeWidth={1.8} />
                  <span>{label}</span>
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="user-avatar">U</div>
          <div className="user-details">
            <strong>CRM User</strong>
            <span>Workspace member</span>
          </div>
          <Settings size={17} className="muted-icon" />
        </div>
      </aside>
    </>
  );
}
