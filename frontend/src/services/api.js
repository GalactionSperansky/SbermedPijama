const API_URL = import.meta.env.VITE_API_URL || '/api'

export async function api(path, options = {}) {
  const token = localStorage.getItem('diinozavr_token')
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) }
  if (token) headers.Authorization = `Token ${token}`

  let response
  try {
    response = await fetch(`${API_URL}${path}`, { ...options, headers })
  } catch {
    throw new Error('Сервер временно недоступен. Проверьте, что backend запущен на порту 8000.')
  }
  if (response.status === 204) return null
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    const message = data.detail || data.non_field_errors?.[0] || Object.values(data).flat()?.[0] || 'Не удалось выполнить запрос.'
    throw new Error(message)
  }
  return data
}
