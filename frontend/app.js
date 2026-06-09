document.addEventListener('DOMContentLoaded', () => {
    console.log("App loaded. Ready for SPA routing.");
    
    const searchInput = document.getElementById('search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            // debounced search logic
        });
    }
});
