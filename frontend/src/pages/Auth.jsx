import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api, errorText } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { Field, Notice } from '../components/UI';

export function AuthPage({ register = false }) {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', mobile: '', password: '' });
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);
  async function submit(e) {
    e.preventDefault();
    setErr('');
    setBusy(true);
    try {
      if (register) {
        await api.post('/api/auth/register', form);
      }
      const u = await login(form.email, form.password);
      navigate(u.role === 'cmo' ? '/cmo' : u.role === 'officer' ? '/officer' : '/citizen');
    } catch (e) {
      setErr(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  const update = (field, val) => setForm({ ...form, [field]: val });
  return (
    <div className="auth-background">
      <div className="auth-card">
        <div className="eyebrow">SECURE PORTAL ACCESS</div>
        <h1>{register ? 'Create your citizen account' : 'Welcome back'}</h1>
        <p>
          {register
            ? 'Submit and track fictional grievances with a demo citizen account.'
            : 'Sign in to access your role-based grievance dashboard.'}
        </p>
        <Notice>{err}</Notice>
        <form onSubmit={submit} className="form-grid">
          {register && (
            <>
              <Field label="Full name">
                <input
                  minLength={2}
                  required
                  value={form.name}
                  onChange={(e) => update('name', e.target.value)}
                />
              </Field>
              <Field label="Mobile number">
                <input
                  minLength={10}
                  maxLength={15}
                  required
                  value={form.mobile}
                  onChange={(e) => update('mobile', e.target.value)}
                  placeholder="10-digit number"
                />
              </Field>
            </>
          )}
          <Field label="Email address">
            <input
              type="email"
              required
              value={form.email}
              onChange={(e) => update('email', e.target.value)}
              placeholder="name@example.com"
            />
          </Field>
          <Field label="Password">
            <input
              type="password"
              minLength={register ? 8 : 1}
              required
              value={form.password}
              onChange={(e) => update('password', e.target.value)}
            />
          </Field>
          <button disabled={busy} className="btn btn-primary btn-full">
            {busy ? 'Please wait...' : register ? 'Create account' : 'Sign in'}
          </button>
        </form>
        <p className="auth-footer">
          {register ? (
            <>
              Already registered? <Link to="/login">Sign in</Link>
            </>
          ) : (
            <>
              New citizen? <Link to="/register">Create an account</Link>
            </>
          )}
        </p>
        <div className="small muted">
          Demo officer/CMO accounts are provisioned by the seed script, not through public
          registration.
        </div>
      </div>
    </div>
  );
}
