import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { isAxiosError } from 'axios';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErrors([]);
    setSubmitting(true);
    try {
      await register(email, password, fullName);
      navigate('/');
    } catch (err) {
      if (isAxiosError(err) && err.response?.data?.errors) {
        setErrors(err.response.data.errors);
      } else if (isAxiosError(err) && err.response?.data?.error) {
        setErrors([err.response.data.error]);
      } else {
        setErrors(['Registration failed.']);
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-sm mx-auto">
      <h1 className="text-2xl font-semibold text-brand-900 mb-6">Create Account</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
          <input
            required value={fullName} onChange={(e) => setFullName(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
          <input
            type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
          <input
            type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <p className="mt-1 text-xs text-slate-400">At least 8 characters.</p>
        </div>
        {errors.length > 0 && (
          <ul className="text-sm text-rejected space-y-0.5">
            {errors.map((e, i) => <li key={i}>{e}</li>)}
          </ul>
        )}
        <button
          type="submit" disabled={submitting}
          className="w-full bg-brand-600 text-white py-2.5 rounded-md hover:bg-brand-700 disabled:opacity-50"
        >
          {submitting ? 'Creating account…' : 'Create Account'}
        </button>
      </form>
      <p className="mt-4 text-sm text-slate-500 text-center">
        Already have an account? <Link to="/login" className="text-brand-600 hover:underline">Log In</Link>
      </p>
    </div>
  );
}
