/**
 * report.js – Report tab module.
 *
 * Registers itself with App.registerTab("report", ...).
 */
(() => {
  const reportPanel = document.getElementById("report-panel");
  const queryList = document.getElementById("query-list");
  const addQueryBtn = document.getElementById("add-query-btn");
  const runReportBtn = document.getElementById("run-report-btn");
  const reportStatus = document.getElementById("report-status");
  const reportResults = document.getElementById("report-results");

  // ── Query row helpers ─────────────────────────────────────────
  function createQueryRow(value = "") {
    const row = document.createElement("div");
    row.className = "query-row";
    row.innerHTML = `
      <input type="text" class="query-input" placeholder="Enter a query…" value="${value.replace(/"/g, '&quot;')}" />
      <button class="btn-icon danger remove-query" title="Remove">&times;</button>
    `;
    return row;
  }

  // ── Render report results (without download link) ──────────────
  function renderReport(data) {
    reportResults.innerHTML = "";

    // Summary
    const summary = document.createElement("div");
    summary.className = "report-summary";
    summary.innerHTML = `
      <span class="stat"><b>${data.total}</b> total</span>
      <span class="stat"><b>${data.succeeded}</b> succeeded</span>
      <span class="stat fail"><b>${data.failed}</b> failed</span>
    `;
    reportResults.appendChild(summary);

    // Each result
    data.results.forEach((r, i) => {
      const item = document.createElement("div");
      item.className = "report-item";
      const queryLabel = document.createElement("div");
      queryLabel.className = "query-label";
      queryLabel.textContent = `Query ${i + 1}: ${r.query}`;
      item.appendChild(queryLabel);

      const resp = document.createElement("div");
      if (r.error) {
        resp.className = "response error-text";
        resp.textContent = `Error: ${r.error}`;
      } else {
        resp.className = "response";
        resp.textContent = r.response ?? "(no response)";
      }
      item.appendChild(resp);
      if (!r.error) {
        item.appendChild(App.createCopyBtn(() => resp.textContent));
      }
      reportResults.appendChild(item);
    });
  }

  // ── Append download link ──────────────────────────────────────
  function appendDownloadLink(sasUrl, blobName) {
    // Insert download link at the top of results
    const downloadDiv = document.createElement("div");
    downloadDiv.className = "report-download";
    downloadDiv.innerHTML = `
      <a href="${sasUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-primary download-link">
        ⬇ Download Report (${blobName || "report.json"})
      </a>
      <span class="download-note">Link valid for 1 hour</span>
    `;
    reportResults.insertBefore(downloadDiv, reportResults.firstChild);
  }

  // ── Progress indicator helpers ────────────────────────────────
  function showBlobProgress(message) {
    let progressDiv = reportResults.querySelector(".blob-progress");
    if (!progressDiv) {
      progressDiv = document.createElement("div");
      progressDiv.className = "blob-progress";
      reportResults.insertBefore(progressDiv, reportResults.firstChild);
    }
    progressDiv.innerHTML = `
      <div class="blob-progress-inner">
        <span class="blob-spinner"></span>
        <span class="blob-progress-text">${message}</span>
      </div>
    `;
  }

  function hideBlobProgress() {
    const progressDiv = reportResults.querySelector(".blob-progress");
    if (progressDiv) progressDiv.remove();
  }

  function showBlobError(message) {
    hideBlobProgress();
    const errorDiv = document.createElement("div");
    errorDiv.className = "blob-progress blob-progress-error";
    errorDiv.innerHTML = `
      <div class="blob-progress-inner">
        <span class="blob-progress-text">⚠ ${message}</span>
      </div>
    `;
    reportResults.insertBefore(errorDiv, reportResults.firstChild);
  }

  // ── Run report ────────────────────────────────────────────────
  async function runReport() {
    const systemPrompt = document.getElementById("system-prompt").value.trim();
    if (!systemPrompt) {
      reportStatus.textContent = "System prompt is required.";
      return;
    }
    const queries = Array.from(queryList.querySelectorAll(".query-input"))
      .map(inp => inp.value.trim())
      .filter(q => q.length > 0);
    if (queries.length === 0) {
      reportStatus.textContent = "At least one query is required.";
      return;
    }

    runReportBtn.disabled = true;
    reportStatus.textContent = "Running report…";
    reportResults.innerHTML = "";

    // Phase 1: Generate report and display results
    let reportData;
    try {
      const resp = await fetch("/api/report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ queries, system_prompt: systemPrompt }),
      });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        reportStatus.textContent = `Error: ${err.detail || resp.statusText}`;
        runReportBtn.disabled = false;
        return;
      }
      reportData = await resp.json();
      reportStatus.textContent = "Report completed.";
      renderReport(reportData);
    } catch (e) {
      reportStatus.textContent = `Network error: ${e.message}`;
      runReportBtn.disabled = false;
      return;
    }

    // Phase 2: Upload to blob storage with progress
    showBlobProgress("Uploading report to Azure Blob Storage…");
    try {
      const uploadResp = await fetch("/api/report/upload", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ report: reportData }),
      });
      if (!uploadResp.ok) {
        const err = await uploadResp.json().catch(() => ({}));
        showBlobError(`Upload failed: ${err.detail || uploadResp.statusText}`);
        runReportBtn.disabled = false;
        return;
      }
      showBlobProgress("Generating download URL…");
      const uploadData = await uploadResp.json();
      hideBlobProgress();
      appendDownloadLink(uploadData.sas_url, uploadData.blob_name);
      reportStatus.textContent = "Report completed. Download link ready.";
    } catch (e) {
      showBlobError(`Upload error: ${e.message}`);
    } finally {
      runReportBtn.disabled = false;
    }
  }

  // ── Tab registration ──────────────────────────────────────────
  App.registerTab("report", "Report", {
    init() {
      addQueryBtn.addEventListener("click", () => {
        queryList.appendChild(createQueryRow());
        const inputs = queryList.querySelectorAll(".query-input");
        inputs[inputs.length - 1].focus();
      });

      queryList.addEventListener("click", (e) => {
        const removeBtn = e.target.closest(".remove-query");
        if (!removeBtn) return;
        const rows = queryList.querySelectorAll(".query-row");
        if (rows.length <= 1) return; // keep at least one row
        removeBtn.closest(".query-row").remove();
      });

      runReportBtn.addEventListener("click", runReport);
    },
    show() {
      reportPanel.style.display = "flex";
    },
    hide() {
      reportPanel.style.display = "none";
    },
  });
})();
