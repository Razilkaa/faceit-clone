const elHealth = document.getElementById('health');
function checkBackend() {
    elHealth.textContent = 'checking...';
    fetch('/api/health')
    .then(response => response.json())
    .then(data => {elHealth.textContent = data.status === "ok" ? "🟢 online" : "🔴 offline"})
    .catch(() => {
        elHealth.textContent = "🔴 offline"
    })

}

checkBackend();

