document.getElementById("predictForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    
    const button = document.getElementById("predictButton");
    const resultDiv = document.getElementById("result");
    const loader = document.getElementById("loader");
    
    // Mostrar loader e desabilitar botão
    button.disabled = true;
    loader.style.display = "block";
    resultDiv.textContent = "";

    try {
        const formData = new FormData(event.target);
        const musicData = {
            Duration: parseFloat(formData.get("Duration")),
            Popularity: parseFloat(formData.get("Popularity")),
            Danceability: parseFloat(formData.get("Danceability")),
            Energy: parseFloat(formData.get("Energy")),
            Key: parseFloat(formData.get("Key")),
            Loudness: parseFloat(formData.get("Loudness")),
            Mode: parseFloat(formData.get("Mode")),
            Speechiness: parseFloat(formData.get("Speechiness")),
            Acousticness: parseFloat(formData.get("Acousticness")),
            Instrumentalness: parseFloat(formData.get("Instrumentalness")),
            Liveness: parseFloat(formData.get("Liveness")),
            Valence: parseFloat(formData.get("Valence")),
            Tempo: parseFloat(formData.get("Tempo")),
            "Time Signature": parseFloat(formData.get("Time_Signature"))
        };

        // ✅ Substitua pela URL da SUA API no Render
        const response = await fetch("https://tarot-api-1234.onrender.com/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(musicData)
        });

        if (!response.ok) throw new Error(`Erro HTTP! Status: ${response.status}`);
        
        const result = await response.json();
        resultDiv.textContent = `Carta prevista: ${result.carta_prevista}`;
        resultDiv.style.color = "green";
    } catch (error) {
        console.error("Erro:", error);
        resultDiv.textContent = "Erro ao prever. Verifique o console (F12).";
        resultDiv.style.color = "red";
    } finally {
        button.disabled = false;
        loader.style.display = "none";
    }
});
