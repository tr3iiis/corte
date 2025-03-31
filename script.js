document.getElementById("predictForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    
    const button = document.getElementById("predictButton");
    const resultDiv = document.getElementById("result");
    const loader = document.getElementById("loader");
    
    // Reset and show loading
    resultDiv.textContent = "";
    button.disabled = true;
    loader.style.display = "block";

    try {
        // Capture form data
        const formData = {
            Duration: parseFloat(document.getElementById("duration").value),
            Popularity: parseFloat(document.getElementById("popularity").value),
            Danceability: parseFloat(document.getElementById("danceability").value),
            Energy: parseFloat(document.getElementById("energy").value),
            Key: parseFloat(document.getElementById("key").value),
            Loudness: parseFloat(document.getElementById("loudness").value),
            Mode: parseFloat(document.getElementById("mode").value),
            Speechiness: parseFloat(document.getElementById("speechiness").value),
            Acousticness: parseFloat(document.getElementById("acousticness").value),
            Instrumentalness: parseFloat(document.getElementById("instrumentalness").value),
            Liveness: parseFloat(document.getElementById("liveness").value),
            Valence: parseFloat(document.getElementById("valence").value),
            Tempo: parseFloat(document.getElementById("tempo").value),
            "Time Signature": parseFloat(document.getElementById("time_signature").value)
        };

        // Replace with your actual API endpoint
        const response = await fetch("https://tarot-classifier.onrender.com/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }

        const data = await response.json();
        resultDiv.textContent = `Carta prevista: ${data.carta_prevista}`;
        resultDiv.style.color = "green";

    } catch (error) {
        console.error("Erro:", error);
        resultDiv.textContent = "Erro na previsão. Verifique o console (F12).";
        resultDiv.style.color = "red";
    } finally {
        button.disabled = false;
        loader.style.display = "none";
    }
});
