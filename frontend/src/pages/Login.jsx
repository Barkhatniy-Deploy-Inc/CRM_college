import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import './Login.css';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        const result = await login(email, password);

        if (!result.success) {
            setError(result.error);
            setLoading(false);
        }
        // При успехе App.jsx автоматически перенаправит на Dashboard
    };

    return (
        <div className="login-container">
            <div className="login-card card fade-in">
                <div className="login-header">
                    <h1 className="gradient-text">CRM College</h1>
                    <p className="text-muted">Система управления колледжем</p>
                </div>

                <form onSubmit={handleSubmit} className="login-form">
                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            id="email"
                            type="email"
                            className="input"
                            placeholder="your@email.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Пароль</label>
                        <input
                            id="password"
                            type="password"
                            className="input"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    {error && (
                        <div className="error-message">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        className="btn btn-primary btn-full"
                        disabled={loading}
                    >
                        {loading ? 'Вход...' : 'Войти'}
                    </button>

                    <div className="text-center" style={{ marginTop: '1rem', textAlign: 'center' }}>
                        <span className="text-muted">Нет аккаунта? </span>
                        <Link to="/register" className="text-primary" style={{ color: 'var(--accent-secondary)', textDecoration: 'none' }}>
                            Зарегистрироваться
                        </Link>
                    </div>
                </form>
            </div>
        </div>
    );
}
