let progress = 0;
let interval;

function startLoading() {
    const container = document.getElementById("loader-container");
    const bar = document.getElementById("loader-bar");

    container.classList.add("show");
    progress = 0;

    interval = setInterval(() => {
        if (progress < 90) {
            progress += Math.random() * 8;
            bar.style.width = progress + "%";
        }
    }, 300);
}

function finishLoading(blob) {
    const container = document.getElementById("loader-container");
    const bar = document.getElementById("loader-bar");

    clearInterval(interval);
    bar.style.width = "100%";

    setTimeout(() => {
        container.classList.remove("show");

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "document.pdf";
        a.click();
        window.URL.revokeObjectURL(url);
    }, 400);
}
function stopLoading() {
    const container = document.getElementById("loader-container");
    clearInterval(interval);
    container.classList.remove("show");
}
async function generatePDF() {
    startLoading();

    const form = document.getElementById("generateForm");
    const formData = new FormData(form);

    const res = await fetch("/generate-ui", {
        method: "POST",
        body: formData
    });

    const contentType = res.headers.get("Content-Type");

    if (!res.ok) {
        let message = "Could not generate the document.";

        if (contentType && contentType.includes("application/json")) {
            const data = await res.json();
            message = data.error || message;
        } else {
            message = await res.text();
        }

        stopLoading();
        showToast(message);
        return;
    }

    const blob = await res.blob();
    finishLoading(blob);
}

function showToast(message) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 5000);
}
