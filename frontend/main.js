const elhealth = document.getElementById("health");
const elinput = document.getElementById("nickInput");

const elsearchBtn = document.getElementById("searchBtn");
const elprofile = document.getElementById("profile");
elsearchBtn.addEventListener("click", () => {
    const nickname = elinput.value;
    if (!nickname) {
        elprofile.textContent = "Введите никнейм"
        return;
    }
    const url = `/api/players/${nickname}`;
    fetch(url)
    .then(response => response.json())
    .then(data =>{
        elprofile.innerHTML = `
        <h2>${data.nickname}</h2>
        <p>Country: ${data.country}</p>
        <p>Level: ${data.level}</p>
        <p>ELO: ${data.elo}</p>
        `
    } )
    .catch(() => {
        elprofile.innerHTML = "<p>Игрок не найден</p>"  
    });
});
function checkBackend() {
    elhealth.textContent = 'checking...';
    fetch('/api/health')
    .then(response => response.json())
    .then(data => {elhealth.textContent = data.status === "ok" ? "🟢 online" : "🔴 offline"})
    .catch(() => {
        elhealth.textContent = "🔴 offline"
    })

}

checkBackend();
