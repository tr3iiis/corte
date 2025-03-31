document.getElementById("predictForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const button = document.getElementById("predictButton");
    const resultDiv = document.getElementById("result");
    const loader = document.getElementById("loader");

    // Reset and show loading
    resultDiv.textContent = "";
    resultDiv.style.color = "black"; // Reset color
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
            "Time Signature": parseFloat(document.getElementById("time_signature").value) // Use a chave com espaço aqui também
        };

        // Log para verificar os dados enviados
        console.log("Enviando dados:", JSON.stringify(formData));

        // URL da API no Render com o endpoint /predict
        const apiUrl = "https://tarot-classifier.onrender.com/predict"; // <--- URL CORRIGIDA

        console.log("Chamando API:", apiUrl); // Log para verificar a URL

        const response = await fetch(apiUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(formData)
        });

        console.log("Status da resposta:", response.status); // Log do status

        // Tenta ler a resposta como JSON mesmo se não for 'ok', pode conter um erro útil
        const data = await response.json();
        console.log("Dados recebidos:", data); // Log dos dados recebidos

        if (!response.ok) {
            // Se a resposta JSON tiver uma chave 'error', usa ela, senão usa o status HTTP
            const errorMessage = data.error || `Erro HTTP: ${response.status}`;
            throw new Error(errorMessage);
        }

        // Assumindo que a resposta de sucesso tem a chave 'carta_prevista'
        if (data.carta_prevista !== undefined) {
             resultDiv.textContent = `Carta prevista: ${data.carta_prevista}`;
             resultDiv.style.color = "green";
        } else {
            // Caso a resposta seja 'ok' mas não tenha 'carta_prevista'
            throw new Error("Formato de resposta inesperado do servidor.");
        }


    } catch (error) {
        console.error("Erro durante a requisição fetch:", error);
        // Mostra a mensagem de erro específica capturada
        resultDiv.textContent = `Erro na previsão: ${error.message}`;
        resultDiv.style.color = "red";
    } finally {
        // Garante que o botão e o loader voltem ao normal
        button.disabled = false;
        loader.style.display = "none";
    }
});
