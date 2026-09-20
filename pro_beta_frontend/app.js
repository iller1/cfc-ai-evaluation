window.addEventListener("load", async function () {
  const target = document.getElementById("auth");
  const app = document.getElementById("workspace-app");
  const key = window.PRO_BETA_CLERK_KEY || "";
  const apiBase = (window.PRO_BETA_API_BASE || "").replace(/\/$/, "");

  const workspaceSelect = document.getElementById("workspace-select");
  const conversationSelect = document.getElementById("conversation-select");
  const status = document.getElementById("workspace-status");
  const messages = document.getElementById("messages");

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
      meta.textContent = row.role + " · " + row.authority + " · " + row.cfc_status;
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
      conversationSelect.addEventListener("change", loadMessages);

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
