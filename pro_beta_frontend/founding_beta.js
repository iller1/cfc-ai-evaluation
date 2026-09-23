window.addEventListener("load", async function () {
  const target = document.getElementById("auth");
  const app = document.getElementById("beta-app");
  const key = window.PRO_BETA_CLERK_KEY || "";
  const apiBase = (window.PRO_BETA_API_BASE || "").replace(/\/$/, "");
  const workspaceSelect = document.getElementById("fb-workspace-select");
  let lastCfc = null;

  async function api(path, options = {}) {
    const token = await Clerk.session.getToken();
    const response = await fetch(apiBase + path, {
      ...options,
      headers: {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        ...(options.headers || {})
      }
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || String(response.status));
    return payload;
  }

  function structuredState() {
    const evidence = [{
      polarity: document.getElementById("fb-cfc-e1-polarity").value,
      validity: document.getElementById("fb-cfc-e1-validity").value
    }];
    if (document.getElementById("fb-cfc-e2-enabled").value === "YES") {
      evidence.push({
        polarity: document.getElementById("fb-cfc-e2-polarity").value,
        validity: document.getElementById("fb-cfc-e2-validity").value
      });
    }
    return {
      conclusion: document.getElementById("fb-cfc-conclusion").value,
      required_independent_supports: Number(document.getElementById("fb-cfc-required").value),
      provenance_shape: document.getElementById("fb-cfc-provenance").value,
      independence_authority: document.getElementById("fb-cfc-independence").value,
      scope: document.getElementById("fb-cfc-scope").value,
      evidence
    };
  }

  async function loadWorkspaces() {
    const rows = await api("/api/workspaces");
    workspaceSelect.innerHTML = "";
    for (const row of rows) {
      const option = document.createElement("option");
      option.value = row.workspace_id;
      option.textContent = row.name;
      workspaceSelect.appendChild(option);
    }
    await loadHistory();
  }

  function renderHistory(rows) {
    const target = document.getElementById("fb-history");
    if (!rows.length) {
      target.textContent = "No Founding Beta measurements yet.";
      return;
    }
    target.textContent = rows.slice().reverse().slice(0, 20).map((row) => [
      row.created_at,
      row.system_version + " · " + row.workflow_type + " · " + row.case_id,
      "CFC " + row.cfc_result + " · " + row.reason_code,
      "Human " + row.human_assessment + " · " + row.final_action,
      "Problem " + row.problem_type,
      row.comment ? "Comment " + row.comment : ""
    ].filter(Boolean).join("\n")).join("\n\n---\n\n");
  }

  async function loadHistory() {
    const workspaceId = workspaceSelect.value;
    if (!workspaceId) {
      renderHistory([]);
      return;
    }
    renderHistory(await api("/api/workspaces/" + workspaceId + "/beta-measurements"));
  }

  if (!key) {
    target.innerHTML = '<p>Authentication is not configured.</p>';
    return;
  }

  await Clerk.load({ ui: { ClerkUI: window.__internal_ClerkUICtor } });
  target.innerHTML = "";
  if (!Clerk.isSignedIn) {
    Clerk.mountSignIn(target);
    return;
  }

  target.innerHTML = "<p>Signed in.</p><div id='fb-user-button'></div>";
  Clerk.mountUserButton(document.getElementById("fb-user-button"));
  if (!apiBase) {
    target.innerHTML += "<p>Backend API is not configured.</p>";
    return;
  }

  await api("/api/onboard", { method: "POST", body: "{}" });
  app.hidden = false;
  await loadWorkspaces();

  document.getElementById("fb-create-workspace").addEventListener("click", async () => {
    const name = document.getElementById("fb-workspace-name").value.trim();
    await api("/api/workspaces", { method: "POST", body: JSON.stringify({ name }) });
    document.getElementById("fb-workspace-name").value = "";
    await loadWorkspaces();
  });

  document.getElementById("fb-refresh-workspaces").addEventListener("click", loadWorkspaces);
  workspaceSelect.addEventListener("change", loadHistory);
  document.getElementById("fb-refresh-history").addEventListener("click", loadHistory);

  document.getElementById("fb-run-cfc").addEventListener("click", async () => {
    const workspaceId = workspaceSelect.value;
    if (!workspaceId) throw new Error("CREATE_WORKSPACE_FIRST");
    const target = document.getElementById("fb-cfc-result");
    try {
      const result = await api(
        "/api/workspaces/" + workspaceId + "/beta-cfc-check",
        {
          method: "POST",
          body: JSON.stringify({ cfc_structured: structuredState() })
        }
      );
      lastCfc = result;
      const p = result.presentation || {};
      const decision = p.decision || "UNKNOWN";
      const reason = p.reason || ((p.false_gates || []).join(",") || "NO_REASON_CODE");
      document.getElementById("fb-reason-code").value = reason;
      document.getElementById("fb-hawm-state").value =
        (p.claim_state || "UNKNOWN") + "_PRESENTED";
      const mapped = result.mapped_input || {};
      const mappedEvidence = Array.isArray(mapped.evidence)
        ? mapped.evidence.map((row, index) =>
            "E" + (index + 1) + "=" + (row.polarity || "UNKNOWN") + "/" + (row.validity || "UNKNOWN")
          ).join(", ")
        : "UNKNOWN";
      target.textContent = [
        "Anchor: " + result.controller_anchor,
        "Decision: " + decision,
        "Claim state: " + (p.claim_state || "UNKNOWN"),
        "Reason: " + reason,
        "Mapped input: supports=" + String(mapped.required_independent_supports ?? "UNKNOWN") +
          " · scope=" + String(mapped.scope || "UNKNOWN") +
          " · provenance=" + String(mapped.provenance_shape || "UNKNOWN") +
          " · independence=" + String(mapped.independence_authority || "UNKNOWN") +
          " · evidence=" + mappedEvidence,
        "Customer content persisted: " + String(result.persisted_customer_content)
      ].join("\n");
    } catch (error) {
      target.textContent = "CFC error: " + error.message;
    }
  });

  document.getElementById("fb-delete-measurements").addEventListener("click", async () => {
    const workspaceId = workspaceSelect.value;
    const status = document.getElementById("fb-measurement-status");
    try {
      if (!workspaceId) throw new Error("CREATE_WORKSPACE_FIRST");
      const confirmed = window.confirm(
        "Delete all Founding Beta measurement records for this workspace? This cannot be undone."
      );
      if (!confirmed) return;
      const result = await api(
        "/api/workspaces/" + workspaceId + "/beta-measurements",
        { method: "DELETE" }
      );
      status.textContent =
        "Deleted measurement records: " + result.deleted_measurements +
        " · customer content deleted: " + result.customer_content_deleted;
      lastCfc = null;
      await loadHistory();
    } catch (error) {
      status.textContent = "Delete error: " + error.message;
    }
  });

  document.getElementById("fb-save-measurement").addEventListener("click", async () => {
    const workspaceId = workspaceSelect.value;
    const status = document.getElementById("fb-measurement-status");
    try {
      if (!workspaceId) throw new Error("CREATE_WORKSPACE_FIRST");
      if (!lastCfc) throw new Error("RUN_CFC_FIRST");
      const p = lastCfc.presentation || {};
      const decision = p.decision || "UNRESOLVED";
      if (!["ALLOW","STOP","UNRESOLVED"].includes(decision)) {
        throw new Error("CFC_DECISION_NOT_MEASURABLE");
      }
      const caseIdInput = document.getElementById("fb-case-id");
      const caseId = caseIdInput.value.trim();
      if (!caseId) {
        caseIdInput.focus();
        throw new Error("CASE_ID_REQUIRED: enter a non-sensitive case ID such as TEST-001");
      }
      const payload = {
        system_version: document.getElementById("fb-system-version").value.trim(),
        workflow_type: document.getElementById("fb-workflow-type").value,
        case_id: caseId,
        cfc_result: decision,
        reason_code: document.getElementById("fb-reason-code").value.trim(),
        hawm_state: document.getElementById("fb-hawm-state").value.trim(),
        human_assessment: document.getElementById("fb-human-assessment").value,
        final_action: document.getElementById("fb-final-action").value,
        problem_type: document.getElementById("fb-problem-type").value,
        comment: document.getElementById("fb-comment").value.trim()
      };
      const saved = await api(
        "/api/workspaces/" + workspaceId + "/beta-measurements",
        { method: "POST", body: JSON.stringify(payload) }
      );
      document.getElementById("fb-comment").value = "";
      status.textContent =
        "Measurement recorded: " + saved.measurement_id +
        " · NO CUSTOMER CONTENT BY DEFAULT";
      await loadHistory();
    } catch (error) {
      status.textContent = "Measurement error: " + error.message;
    }
  });
});
