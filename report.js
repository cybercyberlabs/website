(function () {
    const file = decodeURIComponent(location.pathname.split("/").pop() || "report.html");
    const fileLabel = document.querySelector(".status-file");
    const linesLabel = document.querySelector(".status-lines");
    const input = document.getElementById("cmd");
    const msg = document.getElementById("cmdmsg");
    const form = document.getElementById("cmdline");
    const tildes = document.getElementById("tildes");
    const article = document.querySelector("article");

    if (fileLabel) fileLabel.textContent = '"' + file + '" [readonly]';
    if (linesLabel && article) {
        linesLabel.textContent = article.children.length + " lines";
    }

    function goHome() {
        location.href = "../index.html";
    }

    function fillTildes() {
        if (!tildes || !article) return;
        const lineHeight = parseFloat(getComputedStyle(document.body).lineHeight) || 22;
        const count = Math.max(1, Math.ceil(window.innerHeight / lineHeight));
        tildes.replaceChildren();
        for (let i = 0; i < count; i++) {
            tildes.appendChild(document.createElement("span")).textContent = "~";
        }
    }

    if (form) {
        form.addEventListener("submit", function (event) {
            event.preventDefault();
            const cmd = input.value.trim().toLowerCase();
            input.value = "";
            if (cmd === "q" || cmd === "q!" || cmd === "qa" || cmd === "quit" || cmd === "wq") {
                goHome();
                return;
            }
            if (cmd === "pdf") {
                const pdf = document.querySelector(".pdf-link");
                if (pdf) pdf.click();
                msg.textContent = "";
                return;
            }
            msg.textContent = cmd ? "E492: Not an editor command: " + cmd : "";
        });
    }

    let closing = false;
    function closeOnEscape(event) {
        const isEscape = event.key === "Escape" || event.key === "Esc" || event.code === "Escape" || event.keyCode === 27;
        if (!isEscape || closing) return;
        closing = true;
        event.preventDefault();
        event.stopPropagation();
        // Escape also means "stop loading". Navigating in this same event gets cancelled.
        setTimeout(goHome, 0);
    }
    window.addEventListener("keydown", closeOnEscape, true);
    window.addEventListener("keyup", closeOnEscape, true);

    document.addEventListener("keydown", function (event) {
        if (event.key === ":" && document.activeElement !== input) {
            event.preventDefault();
            input.focus();
        }
    });

    fillTildes();
    window.addEventListener("resize", fillTildes);
})();
