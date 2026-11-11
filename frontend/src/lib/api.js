import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 75000, // Free hosting may require an initial cold-start.
});
api.interceptors.request.use(config => {
  const token = sessionStorage.getItem('cmk_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
export function errorText(error) {
  const data = error?.response?.data?.detail;
  if (Array.isArray(data)) return data.map(x => x.msg || 'Invalid input').join('; ');
  return typeof data === 'string' ? data : (error?.message || 'Something went wrong');
}
export const DISTRICTS = ['Thiruvananthapuram','Kollam','Pathanamthitta','Alappuzha','Kottayam','Idukki','Ernakulam','Thrissur','Palakkad','Malappuram','Kozhikode','Wayanad','Kannur','Kasaragod'];
export const STATUSES = ['Submitted','Under Review','In Progress','Resolved','Reopened'];
export const PRIORITIES = ['Low','Medium','High'];
