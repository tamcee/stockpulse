const api = {
    request: async (url, options = {}) => {
        const token = localStorage.getItem('token');
        const headers = { ...options.headers, 'Content-Type': 'application/json' };
        if (token) headers['Authorization'] = `Bearer ${token}`;
        const res = await fetch(url, { ...options, headers });
        return res.json();
    }
};
