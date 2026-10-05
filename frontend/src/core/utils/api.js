import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

let refreshPromise = null

const isAuthEndpoint = url =>
  typeof url === 'string' && (url.includes('/auth/login') || url.includes('/auth/refresh'))

api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  response => response,
  async error => {
    const { response, config } = error

    // Не пытаемся обновлять токен для самих auth-запросов и повторных попыток,
    // чтобы исключить бесконечный цикл.
    if (
      !response ||
      response.status !== 401 ||
      !config ||
      config._retry ||
      isAuthEndpoint(config.url)
    ) {
      return Promise.reject(error)
    }

    config._retry = true
    try {
      refreshPromise = refreshPromise || api.post('/auth/refresh')
      const { data } = await refreshPromise
      refreshPromise = null

      if (data?.access_token) {
        localStorage.setItem('access_token', data.access_token)
      }
      if (data?.user) {
        localStorage.setItem('user', JSON.stringify(data.user))
      }

      return api(config)
    } catch {
      refreshPromise = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/') {
        window.location.href = '/'
      }
      return Promise.reject(error)
    }
  }
)

export default api
