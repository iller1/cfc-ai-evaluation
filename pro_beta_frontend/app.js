window.addEventListener("load", async function () {
  const target = document.getElementById("auth");
  const app = document.getElementById("workspace-app");
  const key = window.PRO_BETA_CLERK_KEY || "";
  const apiBase = (window.PRO_BETA_API_BASE || "").replace(/\/$/, "");

  const workspaceSelect = document.getElementById("workspace-select");
  const conversationSelect = document.getElementById("conversation-select");
  const status = document.getElementById("workspace-status");
  const messages = document.getElementById("messages");
  const PRO_BETA_GEMINI_KEY = "pro_beta_gemini_key";
  const PRO_BETA_GEMINI_MODEL = "pro_beta_gemini_model";
  const PRO_BETA_CLAUDE_KEY = "pro_beta_claude_key";
  const PRO_BETA_CLAUDE_MODEL = "pro_beta_claude_model";
  const PRO_BETA_OPENAI_KEY = "pro_beta_openai_key";
  const PRO_BETA_OPENAI_MODEL = "pro_beta_openai_model";

  function updateOpenAIStatus() {
    const keyPresent = Boolean(sessionStorage.getItem(PRO_BETA_OPENAI_KEY));
    const modelName =
      sessionStorage.getItem(PRO_BETA_OPENAI_MODEL) ||
      document.getElementById("openai-model").value ||
      "gpt-5.6-terra";
    document.getElementById("openai-status").textContent = keyPresent
      ? "OpenAI ready in this browser tab · " + modelName +
        " · MODEL_REPLY_UNCHECKED / CFC NOT_CONNECTED_C2 · API key not persisted by Pro Beta"
      : "OpenAI disconnected. Ordinary model replies remain MODEL_REPLY_UNCHECKED / CFC NOT_CONNECTED_C2.";
  }

  function updateClaudeStatus() {
    const keyPresent = Boolean(sessionStorage.getItem(PRO_BETA_CLAUDE_KEY));
    const modelName =
      sessionStorage.getItem(PRO_BETA_CLAUDE_MODEL) ||
      document.getElementById("claude-model").value ||
      "claude-sonnet-4-5";
    document.getElementById("claude-status").textContent = keyPresent
      ? "Claude ready in this browser tab · " + modelName +
        " · MODEL_REPLY_UNCHECKED / CFC NOT_CONNECTED_C2 · API key not persisted by Pro Beta"
      : "Claude disconnected. Ordinary model replies remain MODEL_REPLY_UNCHECKED / CFC NOT_CONNECTED_C2.";
  }

  function updateGeminiStatus() {
    const keyPresent = Boolean(sessionStorage.getItem(PRO_BETA_GEMINI_KEY));
    const modelName =
      sessionStorage.getItem(PRO_BETA_GEMINI_MODEL) ||
      document.getElementById("gemini-model").value ||
      "gemini-3.8-flash";
    document.getElementById("gemini-status").textContent = keyPresent
      ? "Gemini ready in this browser tab · " + modelName +
        " · MODEL_REPLY_UNCHECKED / CFC NOT_CONNECTED_C2 · API key not persisted by Pro Beta"
      : "Gemini disconnected. Ordinary model replies remain MODEL_REPLY_UNCHECKED / CFC NOT_CONNECTED_C2.";
  }

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
    if (!response.ok) {
      throw new Error(payload.error || String(response.status));
    }
    return payload;
  }

  function setOptions(select, rows, valueKey, labelKey) {
    select.innerHTML = "";
    for (const row of rows) {
      const option = document.createElement("option");
      option.value = row[valueKey];
      option.textContent = row[labelKey];
      select.appendChild(option);
    }
  }

  function hawmFields() {
    return {
      goal: document.getElementById("hawm-goal"),
      task: document.getElementById("hawm-task"),
      claims: document.getElementById("hawm-claims"),
      evidence: document.getElementById("hawm-evidence"),
      constraints: document.getElementById("hawm-constraints"),
      unresolved: document.getElementById("hawm-unresolved"),
      next_action: document.getElementById("hawm-next-action")
    };
  }

  function structuredCFCState() {
    const evidence = [
      {
        polarity: document.getElementById("hawm-cfc-e1-polarity").value,
        validity: document.getElementById("hawm-cfc-e1-validity").value
      }
    ];
    if (document.getElementById("hawm-cfc-e2-enabled").value === "YES") {
      evidence.push({
        polarity: document.getElementById("hawm-cfc-e2-polarity").value,
        validity: document.getElementById("hawm-cfc-e2-validity").value
      });
    }
    return {
      conclusion: document.getElementById("hawm-cfc-conclusion").value,
      required_independent_supports: Number(
        document.getElementById("hawm-cfc-required").value
      ),
      provenance_shape: document.getElementById("hawm-cfc-provenance").value,
      independence_authority: document.getElementById("hawm-cfc-independence").value,
      scope: document.getElementById("hawm-cfc-scope").value,
      evidence
    };
  }

  function applyStructuredCFCState(value) {
    const s = value || {};
    document.getElementById("hawm-cfc-conclusion").value = s.conclusion || "POSITIVE";
    document.getElementById("hawm-cfc-required").value =
      String(s.required_independent_supports || 1);
    document.getElementById("hawm-cfc-provenance").value =
      s.provenance_shape || "DISTINCT";
    document.getElementById("hawm-cfc-independence").value =
      s.independence_authority || "NONE";
    document.getElementById("hawm-cfc-scope").value = s.scope || "EXPECTED";
    const evidence = Array.isArray(s.evidence) ? s.evidence : [];
    const e1 = evidence[0] || {};
    const e2 = evidence[1] || {};
    document.getElementById("hawm-cfc-e1-polarity").value = e1.polarity || "POSITIVE";
    document.getElementById("hawm-cfc-e1-validity").value = e1.validity || "CURRENT";
    document.getElementById("hawm-cfc-e2-enabled").value = evidence.length > 1 ? "YES" : "NO";
    document.getElementById("hawm-cfc-e2-polarity").value = e2.polarity || "POSITIVE";
    document.getElementById("hawm-cfc-e2-validity").value = e2.validity || "CURRENT";
  }

  function clearHAWM() {
    for (const field of Object.values(hawmFields())) field.value = "";
    applyStructuredCFCState(null);
    document.getElementById("hawm-status").textContent = "";
    document.getElementById("hawm-cfc-result").textContent =
      "No structured HAWM CFC run yet.";
  }

  async function loadHAWM() {
    clearHAWM();
    const conversationId = conversationSelect.value;
    if (!conversationId) return;
    const snapshot = await api("/api/conversations/" + conversationId + "/hawm");
    if (!snapshot) {
      document.getElementById("hawm-status").textContent =
        "No HAWM snapshot saved yet.";
      return;
    }
    const fields = hawmFields();
    const state = snapshot.state || {};
    for (const [name, field] of Object.entries(fields)) {
      field.value = state[name] || "";
    }
    applyStructuredCFCState(state.cfc_structured);
    document.getElementById("hawm-status").textContent =
      "Loaded HAWM snapshot · " + snapshot.last_verified_state;
  }

  function renderCFC(run, targetId = "cfc-result", label = "Prepared synthetic fixture") {
    const target = document.getElementById(targetId);
    if (!run) {
      target.textContent = "No CFC run saved for this conversation yet.";
      return;
    }
    const p = run.presentation || {};
    target.textContent = [
      label,
      "Case: " + run.case_id,
      "Anchor: " + run.controller_anchor,
      "Claim state: " + (p.claim_state || "NONE"),
      "Decision: " + (p.decision || "UNKNOWN"),
      "Reason: " + (p.reason || ""),
      "Replay matches reference: " + String(run.replay_matches_reference)
    ].join("\n");
  }

  async function loadCFC() {
    const conversationId = conversationSelect.value;
    if (!conversationId) {
      renderCFC(null);
      document.getElementById("hawm-cfc-result").textContent =
        "No structured HAWM CFC run yet.";
      return;
    }
    const run = await api("/api/conversations/" + conversationId + "/cfc");
    if (run && run.case_id === "HAWM_STRUCTURED_CUSTOM") {
      renderCFC(
        run,
        "hawm-cfc-result",
        "Structured HAWM → frozen CFC"
      );
      document.getElementById("cfc-result").textContent =
        "Latest CFC run is the structured HAWM path.";
    } else {
      renderCFC(run);
      document.getElementById("hawm-cfc-result").textContent =
        "No structured HAWM CFC run yet.";
    }
  }

  async function loadMessages() {
    messages.innerHTML = "";
    const conversationId = conversationSelect.value;
    if (!conversationId) return;
    const rows = await api("/api/conversations/" + conversationId + "/messages");
    for (const row of rows) {
      const el = document.createElement("div");
      el.className = "message";
      const content = document.createElement("div");
      content.textContent = row.content;
      const meta = document.createElement("div");
      meta.className = "meta";
      const providerModel = row.provider
        ? " · " + row.provider + (row.model ? " · " + row.model : "")
        : "";
      meta.textContent =
        row.role + providerModel + " · " + row.authority + " · " + row.cfc_status;
      el.appendChild(content);
      el.appendChild(meta);
      messages.appendChild(el);
    }
  }

  async function loadConversations() {
    const workspaceId = workspaceSelect.value;
    if (!workspaceId) {
      conversationSelect.innerHTML = "";
      messages.innerHTML = "";
      return;
    }
    const rows = await api("/api/workspaces/" + workspaceId + "/conversations");
    setOptions(conversationSelect, rows, "conversation_id", "title");
    await loadMessages();
    await loadHAWM();
    await loadCFC();
  }

  async function loadWorkspaces() {
    const rows = await api("/api/workspaces");
    setOptions(workspaceSelect, rows, "workspace_id", "name");
    await loadConversations();
  }

  if (!key) {
    target.innerHTML = '<p class="error">Authentication is not configured yet.</p>';
    return;
  }

  try {
    await Clerk.load({ ui: { ClerkUI: window.__internal_ClerkUICtor } });
    target.innerHTML = "";

    if (Clerk.isSignedIn) {
      target.innerHTML = [
        "<p>Signed in.</p>",
        "<div id='user-button'></div>",
        "<p id='backend-status'>Connecting account to Pro Beta…</p>"
      ].join("");
      Clerk.mountUserButton(document.getElementById("user-button"));

      if (!apiBase) {
        document.getElementById("backend-status").textContent =
          "Backend API is not configured yet.";
        return;
      }

      const onboard = await api("/api/onboard", { method: "POST", body: "{}" });
      document.getElementById("backend-status").textContent =
        onboard.created
          ? "Pro Beta account created and connected."
          : "Pro Beta account connected.";

      app.hidden = false;
      await loadWorkspaces();

      document.getElementById("create-workspace").addEventListener("click", async () => {
        try {
          const name = document.getElementById("workspace-name").value;
          await api("/api/workspaces", {
            method: "POST",
            body: JSON.stringify({ name })
          });
          document.getElementById("workspace-name").value = "";
          status.textContent = "Workspace created.";
          await loadWorkspaces();
        } catch (error) {
          status.textContent = "Workspace error: " + error.message;
        }
      });

      document.getElementById("refresh-workspaces").addEventListener("click", loadWorkspaces);
      workspaceSelect.addEventListener("change", loadConversations);
      conversationSelect.addEventListener("change", async () => {
        await loadMessages();
        await loadHAWM();
        await loadCFC();
      });

      document.getElementById("create-conversation").addEventListener("click", async () => {
        try {
          const workspaceId = workspaceSelect.value;
          if (!workspaceId) throw new Error("CREATE_WORKSPACE_FIRST");
          const title = document.getElementById("conversation-title").value;
          await api("/api/workspaces/" + workspaceId + "/conversations", {
            method: "POST",
            body: JSON.stringify({ title })
          });
          document.getElementById("conversation-title").value = "";
          status.textContent = "Conversation created.";
          await loadConversations();
        } catch (error) {
          status.textContent = "Conversation error: " + error.message;
        }
      });

      document.getElementById("connect-gemini").addEventListener("click", () => {
        const rawKey = document.getElementById("gemini-key").value.trim();
        const modelName =
          document.getElementById("gemini-model").value.trim() ||
          "gemini-3.8-flash";
        if (!rawKey) {
          document.getElementById("gemini-status").textContent =
            "Gemini key required.";
          return;
        }
        sessionStorage.setItem(PRO_BETA_GEMINI_KEY, rawKey);
        sessionStorage.setItem(PRO_BETA_GEMINI_MODEL, modelName);
        document.getElementById("gemini-key").value = "";
        updateGeminiStatus();
      });

      document.getElementById("disconnect-gemini").addEventListener("click", () => {
        sessionStorage.removeItem(PRO_BETA_GEMINI_KEY);
        sessionStorage.removeItem(PRO_BETA_GEMINI_MODEL);
        document.getElementById("gemini-key").value = "";
        updateGeminiStatus();
      });

      document.getElementById("get-gemini-key").addEventListener("click", () => {
        window.open(
          "https://aistudio.google.com/app/apikey",
          "_blank",
          "noopener,noreferrer"
        );
      });

      updateGeminiStatus();

      document.getElementById("connect-claude").addEventListener("click", () => {
        const rawKey = document.getElementById("claude-key").value.trim();
        const modelName =
          document.getElementById("claude-model").value.trim() ||
          "claude-sonnet-4-5";
        if (!rawKey) {
          document.getElementById("claude-status").textContent =
            "Claude key required.";
          return;
        }
        sessionStorage.setItem(PRO_BETA_CLAUDE_KEY, rawKey);
        sessionStorage.setItem(PRO_BETA_CLAUDE_MODEL, modelName);
        document.getElementById("claude-key").value = "";
        updateClaudeStatus();
      });

      document.getElementById("disconnect-claude").addEventListener("click", () => {
        sessionStorage.removeItem(PRO_BETA_CLAUDE_KEY);
        sessionStorage.removeItem(PRO_BETA_CLAUDE_MODEL);
        document.getElementById("claude-key").value = "";
        updateClaudeStatus();
      });

      document.getElementById("get-claude-key").addEventListener("click", () => {
        window.open(
          "https://console.anthropic.com/settings/keys",
          "_blank",
          "noopener,noreferrer"
        );
      });

      updateClaudeStatus();

      document.getElementById("connect-openai").addEventListener("click", () => {
        const rawKey = document.getElementById("openai-key").value.trim();
        const modelName =
          document.getElementById("openai-model").value.trim() ||
          "gpt-5.6-terra";
        if (!rawKey) {
          document.getElementById("openai-status").textContent =
            "OpenAI key required.";
          return;
        }
        sessionStorage.setItem(PRO_BETA_OPENAI_KEY, rawKey);
        sessionStorage.setItem(PRO_BETA_OPENAI_MODEL, modelName);
        document.getElementById("openai-key").value = "";
        updateOpenAIStatus();
      });

      document.getElementById("disconnect-openai").addEventListener("click", () => {
        sessionStorage.removeItem(PRO_BETA_OPENAI_KEY);
        sessionStorage.removeItem(PRO_BETA_OPENAI_MODEL);
        document.getElementById("openai-key").value = "";
        updateOpenAIStatus();
      });

      document.getElementById("get-openai-key").addEventListener("click", () => {
        window.open(
          "https://platform.openai.com/api-keys",
          "_blank",
          "noopener,noreferrer"
        );
      });

      updateOpenAIStatus();

      document.getElementById("save-hawm").addEventListener("click", async () => {
        const hawmStatus = document.getElementById("hawm-status");
        try {
          const conversationId = conversationSelect.value;
          if (!conversationId) throw new Error("CREATE_CONVERSATION_FIRST");
          const fields = hawmFields();
          const state = {};
          for (const [name, field] of Object.entries(fields)) {
            state[name] = field.value.trim();
          }
          state.cfc_structured = structuredCFCState();
          await api("/api/conversations/" + conversationId + "/hawm", {
            method: "POST",
            body: JSON.stringify({
              state,
              last_verified_state: "USER_WORKING_STATE"
            })
          });
          hawmStatus.textContent = "HAWM snapshot saved.";
          await loadHAWM();
        } catch (error) {
          hawmStatus.textContent = "HAWM error: " + error.message;
        }
      });

      document.getElementById("run-hawm-cfc").addEventListener("click", async () => {
        const result = document.getElementById("hawm-cfc-result");
        const hawmStatus = document.getElementById("hawm-status");
        try {
          const conversationId = conversationSelect.value;
          if (!conversationId) throw new Error("CREATE_CONVERSATION_FIRST");

          const state = structuredCFCState();
          if (
            state.provenance_shape === "SHARED_LINEAGE" &&
            state.independence_authority === "VERIFIED"
          ) {
            throw new Error("SHARED_LINEAGE_CANNOT_BE_VERIFIED_INDEPENDENT");
          }

          const fields = hawmFields();
          const savedState = {};
          for (const [name, field] of Object.entries(fields)) {
            savedState[name] = field.value.trim();
          }
          savedState.cfc_structured = state;

          await api("/api/conversations/" + conversationId + "/hawm", {
            method: "POST",
            body: JSON.stringify({
              state: savedState,
              last_verified_state: "USER_WORKING_STATE"
            })
          });

          result.textContent = "Running structured HAWM through frozen CFC…";
          const run = await api(
            "/api/conversations/" + conversationId + "/cfc-from-hawm",
            { method: "POST", body: "{}" }
          );
          renderCFC(
            run,
            "hawm-cfc-result",
            "Structured HAWM → frozen CFC"
          );
          hawmStatus.textContent =
            "HAWM snapshot saved and structured CFC check completed.";
        } catch (error) {
          result.textContent = "HAWM → CFC error: " + error.message;
        }
      });

      document.getElementById("export-report").addEventListener("click", async () => {
        const reportStatus = document.getElementById("report-status");
        try {
          const conversationId = conversationSelect.value;
          if (!conversationId) throw new Error("CREATE_CONVERSATION_FIRST");
          reportStatus.textContent = "Generating audit report…";
          const payload = await api(
            "/api/conversations/" + conversationId + "/report",
            { method: "POST", body: "{}" }
          );
          const markdown = payload.markdown || "";
          const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
          const url = URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url;
          link.download = "cfc-hawm-audit-report-" + conversationId + ".md";
          document.body.appendChild(link);
          link.click();
          link.remove();
          URL.revokeObjectURL(url);

          const record = payload.report_record || {};
          const doc = payload.document || {};
          const run = doc.cfc_run || {};
          const presentation = run.presentation || {};
          reportStatus.textContent = [
            "Audit report generated",
            "Report ID: " + (record.report_id || ""),
            "Status: " + (record.status || ""),
            "CFC anchor: " + (run.controller_anchor || "NONE"),
            "Decision: " + (presentation.decision || "NONE"),
            "Boundary: free-text HAWM and ordinary model replies are not CFC-verified"
          ].join("\n");
        } catch (error) {
          reportStatus.textContent = "Report error: " + error.message;
        }
      });

      document.getElementById("run-cfc").addEventListener("click", async () => {
        const result = document.getElementById("cfc-result");
        try {
          const conversationId = conversationSelect.value;
          if (!conversationId) throw new Error("CREATE_CONVERSATION_FIRST");
          result.textContent = "Running frozen CFC prepared fixture…";
          const run = await api("/api/conversations/" + conversationId + "/cfc", {
            method: "POST",
            body: JSON.stringify({
              case_id: document.getElementById("cfc-case").value
            })
          });
          renderCFC(run);
        } catch (error) {
          result.textContent = "CFC error: " + error.message;
        }
      });

      document.getElementById("send-gemini").addEventListener("click", async () => {
        const geminiStatus = document.getElementById("gemini-status");
        try {
          const conversationId = conversationSelect.value;
          if (!conversationId) throw new Error("CREATE_CONVERSATION_FIRST");
          const input = document.getElementById("message-input");
          const content = input.value.trim();
          if (!content) throw new Error("MESSAGE_EMPTY");
          const apiKey = sessionStorage.getItem(PRO_BETA_GEMINI_KEY) || "";
          if (!apiKey) throw new Error("GEMINI_API_KEY_REQUIRED");
          const modelName =
            sessionStorage.getItem(PRO_BETA_GEMINI_MODEL) ||
            document.getElementById("gemini-model").value ||
            "gemini-3.8-flash";
          const mode = document.getElementById("gemini-mode").value;
          geminiStatus.textContent =
            "Calling Gemini · ordinary reply remains MODEL_REPLY_UNCHECKED / CFC NOT_CONNECTED_C2…";
          const result = await api(
            "/api/conversations/" + conversationId + "/gemini-chat",
            {
              method: "POST",
              body: JSON.stringify({
                text: content,
                mode,
                model: modelName,
                api_key: apiKey
              })
            }
          );
          input.value = "";
          geminiStatus.textContent = [
            "Gemini reply saved",
            "Provider: " + result.provider,
            "Model: " + result.model,
            "Authority: " + result.authority,
            "CFC: " + result.cfc_status,
            "API key persisted: " + String(result.api_key_persisted),
            "Truncated: " + String(result.truncated)
          ].join("\n");
          await loadMessages();
        } catch (error) {
          geminiStatus.textContent = "Gemini error: " + error.message;
        }
      });

      document.getElementById("send-claude").addEventListener("click", async () => {
        const claudeStatus = document.getElementById("claude-status");
        try {
          const conversationId = conversationSelect.value;
          if (!conversationId) throw new Error("CREATE_CONVERSATION_FIRST");
          const input = document.getElementById("message-input");
          const content = input.value.trim();
          if (!content) throw new Error("MESSAGE_EMPTY");
          const apiKey = sessionStorage.getItem(PRO_BETA_CLAUDE_KEY) || "";
          if (!apiKey) throw new Error("CLAUDE_API_KEY_REQUIRED");
          const modelName =
            sessionStorage.getItem(PRO_BETA_CLAUDE_MODEL) ||
            document.getElementById("claude-model").value ||
            "claude-sonnet-4-5";
          const mode = document.getElementById("gemini-mode").value;
          claudeStatus.textContent =
            "Calling Claude · ordinary reply remains MODEL_REPLY_UNCHECKED / CFC NOT_CONNECTED_C2…";
          const result = await api(
            "/api/conversations/" + conversationId + "/claude-chat",
            {
              method: "POST",
              body: JSON.stringify({
                text: content,
                mode,
                model: modelName,
                api_key: apiKey
              })
            }
          );
          input.value = "";
          claudeStatus.textContent = [
            "Claude reply saved",
            "Provider: " + result.provider,
            "Model: " + result.model,
            "Authority: " + result.authority,
            "CFC: " + result.cfc_status,
            "API key persisted: " + String(result.api_key_persisted),
            "Truncated: " + String(result.truncated)
          ].join("\n");
          await loadMessages();
        } catch (error) {
          claudeStatus.textContent = "Claude error: " + error.message;
        }
      });

      document.getElementById("send-openai").addEventListener("click", async () => {
        const openaiStatus = document.getElementById("openai-status");
        try {
          const conversationId = conversationSelect.value;
          if (!conversationId) throw new Error("CREATE_CONVERSATION_FIRST");
          const input = document.getElementById("message-input");
          const content = input.value.trim();
          if (!content) throw new Error("MESSAGE_EMPTY");
          const apiKey = sessionStorage.getItem(PRO_BETA_OPENAI_KEY) || "";
          if (!apiKey) throw new Error("OPENAI_API_KEY_REQUIRED");
          const modelName =
            sessionStorage.getItem(PRO_BETA_OPENAI_MODEL) ||
            document.getElementById("openai-model").value ||
            "gpt-5.6-terra";
          const mode = document.getElementById("gemini-mode").value;
          openaiStatus.textContent =
            "Calling OpenAI · ordinary reply remains MODEL_REPLY_UNCHECKED / CFC NOT_CONNECTED_C2…";
          const result = await api(
            "/api/conversations/" + conversationId + "/openai-chat",
            {
              method: "POST",
              body: JSON.stringify({
                text: content,
                mode,
                model: modelName,
                api_key: apiKey
              })
            }
          );
          input.value = "";
          openaiStatus.textContent = [
            "OpenAI reply saved",
            "Provider: " + result.provider,
            "Model: " + result.model,
            "Authority: " + result.authority,
            "CFC: " + result.cfc_status,
            "API key persisted: " + String(result.api_key_persisted),
            "Truncated: " + String(result.truncated)
          ].join("\n");
          await loadMessages();
        } catch (error) {
          openaiStatus.textContent = "OpenAI error: " + error.message;
        }
      });

      document.getElementById("compare-models").addEventListener("click", async () => {
        const compareStatus = document.getElementById("compare-status");
        try {
          const conversationId = conversationSelect.value;
          if (!conversationId) throw new Error("CREATE_CONVERSATION_FIRST");
          const input = document.getElementById("message-input");
          const content = input.value.trim();
          if (!content) throw new Error("MESSAGE_EMPTY");

          const geminiKey = sessionStorage.getItem(PRO_BETA_GEMINI_KEY) || "";
          const claudeKey = sessionStorage.getItem(PRO_BETA_CLAUDE_KEY) || "";
          const openaiKey = sessionStorage.getItem(PRO_BETA_OPENAI_KEY) || "";
          if (!geminiKey || !claudeKey || !openaiKey) {
            throw new Error("CONNECT_ALL_THREE_PROVIDER_KEYS_FIRST");
          }

          const mode = document.getElementById("gemini-mode").value;
          const geminiModel =
            sessionStorage.getItem(PRO_BETA_GEMINI_MODEL) ||
            document.getElementById("gemini-model").value ||
            "gemini-3.8-flash";
          const claudeModel =
            sessionStorage.getItem(PRO_BETA_CLAUDE_MODEL) ||
            document.getElementById("claude-model").value ||
            "claude-sonnet-4-5";
          const openaiModel =
            sessionStorage.getItem(PRO_BETA_OPENAI_MODEL) ||
            document.getElementById("openai-model").value ||
            "gpt-5.6-terra";

          compareStatus.textContent =
            "Running same-prompt comparison across Gemini, Claude and OpenAI…";

          const result = await api(
            "/api/conversations/" + conversationId + "/compare-models",
            {
              method: "POST",
              body: JSON.stringify({
                text: content,
                mode,
                gemini_api_key: geminiKey,
                claude_api_key: claudeKey,
                openai_api_key: openaiKey,
                gemini_model: geminiModel,
                claude_model: claudeModel,
                openai_model: openaiModel
              })
            }
          );

          input.value = "";
          const lines = [
            result.benchmark_type,
            "Authority: " + result.authority,
            "CFC: " + result.cfc_status,
            "API keys persisted: " + String(result.api_keys_persisted)
          ];
          for (const row of result.results || []) {
            lines.push(
              row.provider + " · " + row.model + " · " +
              row.elapsed_ms + " ms · " +
              row.authority + " · " + row.cfc_status
            );
          }
          compareStatus.textContent = lines.join("\n");
          await loadMessages();
        } catch (error) {
          compareStatus.textContent = "Comparison error: " + error.message;
        }
      });

      document.getElementById("send-message").addEventListener("click", async () => {
        try {
          const conversationId = conversationSelect.value;
          if (!conversationId) throw new Error("CREATE_CONVERSATION_FIRST");
          const input = document.getElementById("message-input");
          const content = input.value.trim();
          if (!content) throw new Error("MESSAGE_EMPTY");
          await api("/api/conversations/" + conversationId + "/messages", {
            method: "POST",
            body: JSON.stringify({ content, mode: "STANDARD" })
          });
          input.value = "";
          status.textContent = "Message saved.";
          await loadMessages();
        } catch (error) {
          status.textContent = "Message error: " + error.message;
        }
      });
    } else {
      target.innerHTML = "<div id='sign-in'></div>";
      Clerk.mountSignIn(document.getElementById("sign-in"));
    }
  } catch (error) {
    target.innerHTML = '<p class="error">Authentication failed to initialize.</p>';
  }
});
