let currentGeneratedScript = null;
let currentFormData = null;

document.getElementById('contentForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    await handleGeneration('/generate', 'Generating full script...');
});

document.getElementById('btn-hook').addEventListener('click', async () => {
    const form = document.getElementById('contentForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    await handleGeneration('/generate/hook', 'Generating catchy hook...');
});

document.getElementById('btn-calendar').addEventListener('click', async () => {
    const form = document.getElementById('contentForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    await handleGeneration('/calendar', 'Generating 3-day content calendar...', true);
});

async function handleGeneration(endpoint, loadingMessage, isCalendar = false) {
    const resultDiv = document.getElementById('result');
    const actionBtns = document.getElementById('action-buttons');
    const saveStatus = document.getElementById('save-status');

    resultDiv.innerHTML = `<p class="text-blue-600 font-semibold mt-4 animate-pulse">${loadingMessage}</p>`;
    actionBtns.classList.add('hidden');
    saveStatus.classList.add('hidden');
    currentGeneratedScript = null;

    const form = document.getElementById('contentForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    if (isCalendar) {
        data.post_count = 3;
        data.start_date = new Date().toISOString();
    }
    currentFormData = data;

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || "Failed to generate content.");
        }

        const result = await response.json();

        if (endpoint === '/generate/hook') {
            resultDiv.innerHTML = `<strong>Generated Hook:</strong><br/><br/>${escapeHtml(result.hook)}`;
        } else if (endpoint === '/calendar') {
            let html = `<strong>Generated Calendar for ${escapeHtml(result.platform)}:</strong><br/><br/>`;
            result.posts.forEach((post, index) => {
                const date = new Date(post.scheduled_date).toLocaleDateString();
                html += `<div class="mb-4 p-3 border rounded bg-white shadow-sm">
                    <div class="font-bold text-blue-800 mb-2">Day ${index + 1} - ${date}</div>
                    <div class="text-sm">${escapeHtml(post.content.script)}</div>
                </div>`;
            });
            resultDiv.innerHTML = html;
        } else {
            // standard script
            currentGeneratedScript = result.content.script;
            resultDiv.innerHTML = `
                <button onclick="navigator.clipboard.writeText(currentGeneratedScript)" class="absolute top-2 right-2 text-blue-500 hover:text-blue-700 font-semibold text-xs bg-white px-3 py-1 rounded shadow cursor-pointer border border-blue-200">Copy</button>
                <div class="pt-6">${escapeHtml(currentGeneratedScript)}</div>
            `;
            actionBtns.classList.remove('hidden'); // allow saving
        }

    } catch (error) {
        resultDiv.innerHTML = `<p class="text-red-500 font-semibold mt-4">Error: ${escapeHtml(error.message)}</p>`;
    }
}

document.getElementById('btn-save').addEventListener('click', async () => {
    if (!currentGeneratedScript || !currentFormData) return;

    const saveStatus = document.getElementById('save-status');
    saveStatus.classList.add('hidden');

    const payload = {
        topic: currentFormData.topic,
        platform: currentFormData.platform,
        language: currentFormData.language,
        script_content: currentGeneratedScript
    };

    try {
        const response = await fetch('/scripts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            saveStatus.classList.remove('hidden');
            document.getElementById('btn-load-scripts').click(); // refresh list
        }
    } catch (error) {
        console.error("Failed to save:", error);
    }
});

document.getElementById('btn-load-scripts').addEventListener('click', async () => {
    const listDiv = document.getElementById('saved-scripts-list');
    listDiv.innerHTML = '<p class="text-gray-500 text-sm italic col-span-full">Loading scripts...</p>';

    try {
        const response = await fetch('/scripts');
        const scripts = await response.json();

        if (scripts.length === 0) {
            listDiv.innerHTML = '<p class="text-gray-500 text-sm italic col-span-full">No saved scripts yet.</p>';
            return;
        }

        listDiv.innerHTML = '';
        scripts.reverse().forEach(script => {
            const date = new Date(script.created_at).toLocaleString();
            listDiv.innerHTML += `
                <div class="bg-white p-4 rounded shadow border border-gray-200 flex flex-col justify-between">
                    <div>
                        <div class="flex justify-between items-start mb-2">
                            <h3 class="font-bold text-gray-800 text-sm truncate pr-2" title="${escapeHtml(script.topic)}">${escapeHtml(script.topic)}</h3>
                            <span class="text-xs bg-blue-100 text-blue-800 py-1 px-2 rounded-full whitespace-nowrap">${escapeHtml(script.platform)}</span>
                        </div>
                        <p class="text-xs text-gray-500 mb-3">${date} • ${escapeHtml(script.language)}</p>
                        <p class="text-sm text-gray-700 line-clamp-3 mb-4 font-serif bg-gray-50 p-2 rounded border border-gray-100">${escapeHtml(script.script_content)}</p>
                    </div>
                    <div class="flex space-x-2 mt-auto">
                        <button onclick="navigator.clipboard.writeText('${escapeHtml(script.script_content).replace(/'/g, "\\'")}')" class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-800 border border-gray-300 py-1 px-2 rounded text-xs font-semibold transition">Copy</button>
                        <a href="/export/pdf/${script.id}" target="_blank" class="flex-1 bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 py-1 px-2 rounded text-xs font-semibold text-center transition">Export PDF</a>
                    </div>
                </div>
            `;
        });
    } catch (error) {
        listDiv.innerHTML = `<p class="text-red-500 text-sm col-span-full">Error loading scripts.</p>`;
    }
});

function escapeHtml(unsafe) {
    if (!unsafe) return "";
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Load scripts on initial start
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('btn-load-scripts').click();
});
