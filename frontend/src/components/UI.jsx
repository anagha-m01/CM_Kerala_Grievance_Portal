import { Link, NavLink, Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  ArrowRight,
  ClipboardList,
  LayoutDashboard,
  LogIn,
  LogOut,
  Menu,
  ShieldCheck,
} from 'lucide-react';
import { useState } from 'react';

export function Badge({ children, status }) {
  const cls =
    status === 'Resolved'
      ? 'badge-success'
      : status === 'High' || status === 'Reopened'
        ? 'badge-alert'
        : status === 'In Progress'
          ? 'badge-blue'
          : 'badge-neutral';
  return <span className={`badge ${cls}`}>{children || status}</span>;
}
export function Notice({ type = 'error', children }) {
  return children ? (
    <div role="alert" className={`notice ${type}`}>
      {children}
    </div>
  ) : null;
}
export function PageTitle({ eyebrow, title, description, actions }) {
  return (
    <div className="page-heading">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {actions && <div className="heading-actions">{actions}</div>}
    </div>
  );
}
export function StatCard({ title, value, icon, hint }) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <span>{title}</span>
        <span className="stat-icon">{icon || <ClipboardList size={20} />}</span>
      </div>
      <div className="stat-number">{value ?? '—'}</div>
      {hint && <div className="small muted">{hint}</div>}
    </div>
  );
}
export function Empty({
  title = 'Nothing here yet',
  description = 'Records will appear here as they are created.',
}) {
  return (
    <div className="empty">
      <ClipboardList size={32} />
      <strong>{title}</strong>
      <p>{description}</p>
    </div>
  );
}
export function Loading() {
  return <div className="loading">Loading... Free-tier servers may need a moment to wake up.</div>;
}
export function Field({ label, children }) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
    </label>
  );
}

function destination(role) {
  return role === 'cmo' ? '/cmo' : role === 'officer' ? '/officer' : '/citizen';
}
export function Protected({ roles, children }) {
  const { user, loading } = useAuth();
  if (loading) return <Loading />;
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to={destination(user.role)} replace />;
  return children;
}
export function Nav() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const close = () => setOpen(false);
  return (
    <>
      <div className="prototype-bar">
        <ShieldCheck size={14} /> Recruitment prototype • Fictional demonstration data • NOT an
        official Government of Kerala website
      </div>
      <header className="site-header">
        <div className="header-inner">
          <Link to="/" onClick={close} className="brand">
            <div className="brand-mark">CM</div>
            <span>
              <strong>CM KERALA</strong>
              <small>Public Grievance Portal</small>
            </span>
          </Link>
          <button
            className="mobile-menu"
            aria-label="Toggle navigation"
            onClick={() => setOpen((x) => !x)}
          >
            <Menu />
          </button>
          <nav className={open ? 'nav-links open' : 'nav-links'}>
            <NavLink to="/" onClick={close} end>
              Home
            </NavLink>
            <NavLink to="/about" onClick={close}>
              About
            </NavLink>
            <NavLink to="/how-it-works" onClick={close}>
              How It Works
            </NavLink>
            <NavLink to="/departments" onClick={close}>
              Departments
            </NavLink>
            <NavLink to="/faq" onClick={close}>
              FAQ
            </NavLink>
            <NavLink to="/contact" onClick={close}>
              Contact
            </NavLink>
            {user ? (
              <>
                <Link className="btn btn-light" to={destination(user.role)} onClick={close}>
                  <LayoutDashboard size={16} /> Dashboard
                </Link>
                <button
                  className="btn btn-outline"
                  onClick={() => {
                    logout();
                    close();
                    navigate('/');
                  }}
                >
                  <LogOut size={16} /> Logout
                </button>
              </>
            ) : (
              <Link className="btn btn-primary" to="/login" onClick={close}>
                <LogIn size={16} /> Login / Register
              </Link>
            )}
          </nav>
        </div>
      </header>
    </>
  );
}
export function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-inner">
        <div>
          <strong>CM Kerala • Grievance Portal</strong>
          <p>
            Concept application built solely for a recruitment technical assessment. No real public
            grievances should be submitted.
          </p>
        </div>
        <div>
          <Link to="/about">About</Link>
          <Link to="/faq">FAQ</Link>
          <Link to="/contact">Contact</Link>
        </div>
      </div>
      <div className="copyright">
        This prototype is not operated, authorized, or endorsed by the Government of Kerala or the
        Chief Minister's Office.
      </div>
    </footer>
  );
}
export function Layout({ children }) {
  return (
    <>
      <Nav />
      <main className="app-main">{children}</main>
      <Footer />
    </>
  );
}
export function CaseTable({ items }) {
  if (!items.length) return <Empty />;
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Reference</th>
            <th>Subject</th>
            <th>District</th>
            <th>Priority</th>
            <th>Status</th>
            <th>Updated</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map((g) => (
            <tr key={g.id}>
              <td className="mono">{g.reference_no}</td>
              <td>
                <strong>{g.subject}</strong>
                <div className="small muted">{g.category}</div>
              </td>
              <td>{g.district}</td>
              <td>
                <Badge status={g.priority} />
              </td>
              <td>
                <Badge status={g.status} />
              </td>
              <td className="small">{new Date(g.updated_at).toLocaleDateString()}</td>
              <td>
                <Link className="table-link" to={`/grievances/${g.id}`}>
                  Open <ArrowRight size={14} />
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}