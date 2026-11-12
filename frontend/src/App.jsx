import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { Layout, Protected } from './components/UI';
import { Home, About, HowItWorks, Departments, Contact, FAQ } from './pages/Public';
import { AuthPage } from './pages/Auth';
import { CitizenDashboard, SubmitGrievance, TrackGrievance } from './pages/Citizen';
import { CmoDashboard, OfficerDashboard, GrievanceDetails } from './pages/Cases';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
            <Route path="/how-it-works" element={<HowItWorks />} />
            <Route path="/departments" element={<Departments />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/faq" element={<FAQ />} />
            <Route path="/track" element={<TrackGrievance />} />
            <Route path="/login" element={<AuthPage />} />
            <Route path="/register" element={<AuthPage register />} />
            <Route
              path="/citizen"
              element={
                <Protected roles={['citizen']}>
                  <CitizenDashboard />
                </Protected>
              }
            />
            <Route
              path="/citizen/submit"
              element={
                <Protected roles={['citizen']}>
                  <SubmitGrievance />
                </Protected>
              }
            />
            <Route
              path="/cmo"
              element={
                <Protected roles={['cmo']}>
                  <CmoDashboard />
                </Protected>
              }
            />
            <Route
              path="/officer"
              element={
                <Protected roles={['officer']}>
                  <OfficerDashboard />
                </Protected>
              }
            />
            <Route
              path="/grievances/:id"
              element={
                <Protected>
                  <GrievanceDetails />
                </Protected>
              }
            />
            <Route
              path="*"
              element={
                <div className="container page-section">
                  <h1>Page not found</h1>
                  <p>The requested page is unavailable.</p>
                </div>
              }
            />
          </Routes>
        </Layout>
      </AuthProvider>
    </BrowserRouter>
  );
}