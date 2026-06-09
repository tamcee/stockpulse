const login = async (username, password) => {
    const data = await api.request('/api/auth/login', {
        method: 'POST', body: JSON.stringify({username, password})
    });
    if (data.token) localStorage.setItem('token', data.token);
};

const register = async (username, password) => {
    await api.request('/api/auth/register', {
        method: 'POST', body: JSON.stringify({username, password})
    });
};
