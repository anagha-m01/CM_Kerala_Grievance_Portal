import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  BadgeCheck,
  Building2,
  ClipboardList,
  Clock3,
  FileCheck2,
  HeartHandshake,
  Landmark,
  Search,
  Send,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import { api, errorText } from '../lib/api';
import { Field, Notice, PageTitle } from '../components/UI';

const values = [
  {
    icon: <ClipboardList />,
    title: 'Submit a grievance',
    text: 'Raise an issue with a Kerala district and relevant category.',
  },
  {
    icon: <ShieldCheck />,
    title: 'Transparent review',
    text: 'Follow the stages of review, assignment, action and resolution.',
  },
  {
    icon: <HeartHandshake />,
    title: 'Citizen feedback',
    text: 'Review case updates and provide feedback after resolution.',
  },
];
export function Home() {
  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div>
            <div className="hero-label">
              <span className="status-dot" /> DIGITAL CIVIC SERVICES · PROTOTYPE
            </div>
            <h1>
              Every concern deserves to be <em>heard.</em>
            </h1>
            <p>
              A simple, transparent way to submit and track public service grievances, with
              AI-assisted categorization and a structured review workflow.
            </p>
            <div className="hero-actions">
              <Link className="btn btn-primary btn-lg" to="/citizen/submit">
                Submit a grievance <ArrowRight size={17} />
              </Link>
              <Link className="btn btn-white btn-lg" to="/track">
                <Search size={17} /> Track grievance
              </Link>
            </div>
            <div className="hero-note">
              <ShieldCheck size={17} /> Demonstration system only; do not submit real personal
              information.
            </div>
          </div>
          <div className="hero-panel">
            <div className="mock-panel-top">
              <span className="green-circle" /> <span>GRIEVANCE WORKFLOW</span>
              <span className="mini-pill">Demo</span>
            </div>
            <div className="mock-panel-inner">
              <div className="mock-case">
                <div>
                  <div className="small muted">CASE REFERENCE</div>
                  <strong>CMK-DEMO-0001</strong>
                </div>
                <span className="pill-green">Active</span>
              </div>
              <div className="step-line">
                <span className="step-dot complete" />
                <div>
                  <strong>Grievance submitted</strong>
                  <small>Citizen creates a request</small>
                </div>
              </div>
              <div className="step-line">
                <span className="step-dot complete" />
                <div>
                  <strong>CMO reviews</strong>
                  <small>Validates and forwards the issue</small>
                </div>
              </div>
              <div className="step-line">
                <span className="step-dot" />
                <div>
                  <strong>Department action</strong>
                  <small>Officer investigates and reports</small>
                </div>
              </div>
              <div className="step-line last">
                <span className="step-dot" />
                <div>
                  <strong>Resolution and feedback</strong>
                  <small>CMO approves and citizen responds</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      <section className="container section">
        <div className="section-kicker">HOW WE HELP</div>
        <h2>One connected grievance journey</h2>
        <p className="section-sub">
          Citizens, administrators and officers stay aligned through the complete complaint
          lifecycle.
        </p>
        <div className="feature-grid">
          {values.map((x) => (
            <article className="feature-card" key={x.title}>
              <div className="feature-icon">{x.icon}</div>
              <h3>{x.title}</h3>
              <p>{x.text}</p>
            </article>
          ))}
        </div>
      </section>
      <section className="container section">
        <div className="section-kicker">SAMPLE STATISTICS</div>
        <h2>How a transparent workflow helps</h2>
        <p className="section-sub">
          Illustrative numbers only — not real citizen grievances or official statistics.
        </p>
        <div className="stat-grid">
          <div className="stat-card">
            <div className="small muted">Sample grievances</div>
            <div className="stat-number">1,240</div>
          </div>
          <div className="stat-card">
            <div className="small muted">Illustrative resolutions</div>
            <div className="stat-number">980</div>
          </div>
          <div className="stat-card">
            <div className="small muted">District coverage</div>
            <div className="stat-number">14</div>
          </div>
          <div className="stat-card">
            <div className="small muted">Review roles</div>
            <div className="stat-number">3</div>
          </div>
        </div>
        <div className="section-kicker">FEATURED DEPARTMENTS</div>
        <h2>Sample service categories</h2>
        <div className="feature-grid">
          <div className="feature-card">
            <div className="feature-icon">
              <Building2 />
            </div>
            <h3>Public Works</h3>
            <p>Roads, bridges and public infrastructure.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">
              <Building2 />
            </div>
            <h3>Health Services</h3>
            <p>Public hospitals and healthcare facilities.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">
              <Building2 />
            </div>
            <h3>Education</h3>
            <p>Schools, education infrastructure and services.</p>
          </div>
        </div>
      </section>
      <section className="section soft-section">
        <div className="container cta-strip">
          <div>
            <div className="section-kicker">GET STARTED</div>
            <h2>Have a question about the workflow?</h2>
            <p>Explore the departments and how grievance handling works.</p>
          </div>
          <Link to="/how-it-works" className="btn btn-primary">
            Explore process <ArrowRight size={16} />
          </Link>
        </div>
      </section>
    </>
  );
}
export function About() {
  return (
    <div className="container page-section">
      <PageTitle
        eyebrow="OUR PURPOSE"
        title="About this initiative"
        description="A demonstration of accountable, citizen-centered digital grievance handling."
      />
      <div className="content-grid">
        <section className="panel">
          <h2>Vision</h2>
          <p>
            To illustrate how technology can make civic concerns easier to raise, route and monitor.
          </p>
          <h2>Mission</h2>
          <p>
            Provide citizens with a transparent journey from complaint submission through CMO
            review, department action, resolution and feedback.
          </p>
        </section>
        <section className="panel">
          <h2>Objectives</h2>
          <ul className="bullets">
            <li>Simple citizen access to grievance submission and tracking.</li>
            <li>Role-based review by the Chief Minister's Office and departments.</li>
            <li>Complete audit history for every status change.</li>
            <li>AI recommendations that remain subject to human review.</li>
            <li>Data-driven dashboards and accountability.</li>
          </ul>
          <div className="info-banner">
            This is a fictional recruitment project, not a live Government of Kerala service.
          </div>
        </section>
      </div>
    </div>
  );
}
export function HowItWorks() {
  let steps = [
    [
      '01',
      'Register and submit',
      'Citizen signs in, describes the issue and optionally attaches a file.',
    ],
    [
      '02',
      'AI assistance',
      'An AI model suggests department, category, priority and summary for review.',
    ],
    [
      '03',
      'CMO review',
      'The administrator checks the complaint and assigns an appropriate officer.',
    ],
    [
      '04',
      'Department investigation',
      'The officer records progress and submits an action-taken report.',
    ],
    ['05', 'Review and resolution', 'CMO approves the report or requests further investigation.'],
    [
      '06',
      'Track and give feedback',
      'Citizen tracks the reference number and provides feedback after resolution.',
    ],
  ];
  return (
    <div className="container page-section">
      <PageTitle
        eyebrow="TRANSPARENT PROCESS"
        title="How it works"
        description="Every grievance moves through a recorded, human-reviewed lifecycle."
      />
      <div className="steps-grid">
        {steps.map(([n, title, desc]) => (
          <div className="step-card" key={n}>
            <div className="step-number">{n}</div>
            <h3>{title}</h3>
            <p>{desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
export function Departments() {
  const [items, setItems] = useState([]);
  const [err, setErr] = useState('');
  useEffect(() => {
    api
      .get('/api/departments')
      .then((r) => setItems(r.data))
      .catch((e) => setErr(errorText(e)));
  }, []);
  return (
    <div className="container page-section">
      <PageTitle
        eyebrow="SERVICE DIRECTORY"
        title="Departments"
        description="Sample departments used for routing fictional grievances."
      />
      <Notice>{err}</Notice>
      <div className="feature-grid">
        {items.map((x) => (
          <article className="feature-card" key={x.id}>
            <div className="feature-icon">
              <Building2 />
            </div>
            <h3>{x.name}</h3>
            <p>{x.description}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
export function FAQ() {
  let questions = [
    [
      'Who can submit a grievance?',
      'Registered demo citizen accounts can submit grievances. This is not an official government portal.',
    ],
    [
      'How do I track a grievance?',
      'Use the unique reference number generated after submission. Public tracking displays non-sensitive status and history only.',
    ],
    [
      'What does the AI assistant do?',
      'It suggests a department, category, priority and summary. An administrator makes official workflow decisions.',
    ],
    [
      'Can I upload a supporting document?',
      'Yes. Demo uploads accept PNG, JPEG or PDF files up to 2 MB.',
    ],
    [
      'How will I receive updates?',
      'Sign in to the citizen dashboard or track your reference number to view visible status changes.',
    ],
    [
      'Can I reopen a resolved case?',
      'Yes. A citizen may reopen their own resolved grievance with a reason.',
    ],
    [
      'Is this an official Kerala government service?',
      'No. This is a fictional technical assessment prototype. Do not provide real complaints or sensitive information.',
    ],
  ];
  return (
    <div className="container page-section">
      <PageTitle
        eyebrow="HELP CENTER"
        title="Frequently asked questions"
        description="Answers about submission, tracking and how the demo application works."
      />
      <div className="faq-list">
        {questions.map(([q, a]) => (
          <details key={q}>
            <summary>{q}</summary>
            <p>{a}</p>
          </details>
        ))}
      </div>
    </div>
  );
}
export function Contact() {
  const [data, setData] = useState({ name: '', email: '', subject: '', message: '' });
  const [notice, setNotice] = useState('');
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);
  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setErr('');
    setNotice('');
    try {
      await api.post('/api/contact', data);
      setNotice('Your demo enquiry has been saved. No official government office will receive it.');
      setData({ name: '', email: '', subject: '', message: '' });
    } catch (e) {
      setErr(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="container page-section">
      <PageTitle
        eyebrow="CONTACT"
        title="Send an enquiry"
        description="Reach the demonstration portal team. All enquiries are stored only for testing."
      />
      <div className="content-grid">
        <form className="panel form-grid" onSubmit={submit}>
          <Notice>{err}</Notice>
          <Notice type="success">{notice}</Notice>
          <Field label="Name">
            <input
              required
              minLength={2}
              value={data.name}
              onChange={(e) => setData({ ...data, name: e.target.value })}
            />
          </Field>
          <Field label="Email">
            <input
              type="email"
              required
              value={data.email}
              onChange={(e) => setData({ ...data, email: e.target.value })}
            />
          </Field>
          <Field label="Subject">
            <input
              required
              minLength={3}
              value={data.subject}
              onChange={(e) => setData({ ...data, subject: e.target.value })}
            />
          </Field>
          <Field label="Message">
            <textarea
              required
              minLength={5}
              rows={5}
              value={data.message}
              onChange={(e) => setData({ ...data, message: e.target.value })}
            />
          </Field>
          <button className="btn btn-primary" disabled={busy}>
            {busy ? 'Submitting...' : 'Send enquiry'} <Send size={16} />
          </button>
        </form>
        <aside className="info-side">
          <Landmark size={30} />
          <h2>Recruitment prototype</h2>
          <p>
            This form is part of a technical demonstration and does not contact Kerala government
            offices.
          </p>
          <p>Only use fictional names and messages while evaluating.</p>
        </aside>
      </div>
    </div>
  );
}