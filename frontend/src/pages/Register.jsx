import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../api/auth';
import './Login.css'; // Reusing login styles

export default function Register() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            // 1. Register
            await authAPI.register({
                email,
                password,
                full_name: fullName
            });

            // 2. Auto login after successful registration
            const result = await login(email, password);

            if (!result.success) {
                setError('Регистрация успешна, но не удалось войти автоматически');
                setLoading(false);
                navigate('/login');
            }
            // If login successful, auth context updates and App redirects
        } catch (err) {
            setError(err.response?.data?.message || 'Ошибка регистрации');
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-card card fade-in">
                <div className="login-header">
                    <h1 className="gradient-text">Регистрация</h1>
                    <p className="text-muted">Создание нового аккаунта</p>
                </div>

                <form onSubmit={handleSubmit} className="login-form">
                    <div className="form-group">
                        <label htmlFor="fullname">ФИО</label>
                        <input
                            id="fullname"
                            type="text"
                            className="input"
                            placeholder="Иванов Иван Иванович"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            required
                        />
                    </div>

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
                        {loading ? 'Создание аккаунта...' : 'Зарегистрироваться'}
                    </button>

                    <div className="text-center" style={{ marginTop: '1rem' }}>
                        <span className="text-muted">Уже есть аккаунт? </span>
                        <Link to="/login" className="text-primary" style={{ color: 'var(--accent-secondary)', textDecoration: 'none' }}>
                            Войти
                        </Link>
                    </div>
                </form>
            </div>
        </div>
    );
}
