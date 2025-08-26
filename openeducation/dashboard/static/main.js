// Placeholder for future interactivity
console.log("OpenEducation dashboard loaded.");

document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/summary')
        .then(response => response.json())
        .then(data => {
            const content = `
                <h2>Welcome to your learning dashboard!</h2>
                <p>Syllabi Generated: ${data.syllabi_count}</p>
                <p>Coaching Cycles: ${data.coaching_cycles_count}</p>
                <p>Performance Reports: ${data.performance_reports_count}</p>
            `;
            document.getElementById('dashboard-content').innerHTML = content;
        })
        .catch(error => console.error('Error fetching summary data:', error));
});
