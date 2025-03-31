document.getElementById("predictForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    // Coletando os dados do formulário
    const formData = new FormData(event.target);
    const musicData = {};
    formData.forEach((value, key) => {
        musicData[key] = parseFloat(value); // Convertendo para número
    });

    try {
        // Enviar para o backend no Render
        const response = await fetch("https://tarot-classifier.onrender.com/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(musicData),
        });

        const result = await response.json();
        document.getElementById("result").textContent = "Carta prevista: " + result.prediction;
    } catch (error) {
        console.error("Erro:", error);
        document.getElementById("result").textContent = "Erro ao prever a carta.";
    }
});
