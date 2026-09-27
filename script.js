const imageInput = document.getElementById("imageInput");
const imagePreview = document.getElementById("imagePreview");
const previewSection = document.getElementById("previewSection");
const analyzeBtn = document.getElementById("analyzeBtn");
const resultSection = document.getElementById("resultSection");


// ==============================
// IMAGE UPLOAD
// ==============================

imageInput.addEventListener("change", function () {

    const file = imageInput.files[0];

    if (file) {

        imagePreview.src = URL.createObjectURL(file);

        previewSection.style.display = "block";
        resultSection.style.display = "none";
    }
});


// ==============================
// AI ANALYSIS
// ==============================

analyzeBtn.addEventListener("click", async function () {

    const file = imageInput.files[0];

    if (!file) {
        alert("Please choose a tree image first.");
        return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "🤖 AI Analyzing...";

    const formData = new FormData();
    formData.append("image", file);

    try {
        const response = await fetch("/analyze", {
    method: "POST",
    body: formData
});
        
        // Get server response
        const data = await response.json();

        console.log("Backend response:", data);

        // If backend returned error
        if (!response.ok) {

            const details = data.details || data.error || "Unknown backend error";

            alert(
                "❌ Backend / Gemini Error:\n\n" +
                details
            );

            return;
        }

        // AI result
        const analysis = data.analysis;

        if (!analysis) {

            alert("❌ Gemini returned no analysis.");

            return;
        }

        // Show result section
        resultSection.style.display = "block";


        // ==============================
        // RESULT SECTIONS
        // ==============================

        const sections = {
            "Tree Name:": "treeName",
            "Tree Health:": "treeHealth",
            "Leaf Condition:": "leafCondition",
            "Possible Issues:": "issues",
            "Water Requirement:": "water",
            "Care Suggestion:": "care"
        };


        for (const [label, elementId] of Object.entries(sections)) {

            const regex = new RegExp(
                label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") +
                "\\s*(.*?)(?=\\n[A-Za-z ]+:|$)",
                "s"
            );

            const match = analysis.match(regex);

            if (match) {

                document.getElementById(elementId).textContent =
                    match[1].trim();
            }
        }


    } catch (error) {

        console.error("Frontend error:", error);

        alert(
            "❌ Cannot connect to backend.\n\n" +
            error.message
        );

    } finally {

        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "🔍 Analyze Tree";
    }
});