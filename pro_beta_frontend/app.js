window.addEventListener("load", async function () {
  const target = document.getElementById("auth");
  const key = window.PRO_BETA_CLERK_KEY || "";
  const apiBase = (window.PRO_BETA_API_BASE || "").replace(/\/$/, "");

  if (!key) {
    target.innerHTML = '<p class="error">Authentication is not configured yet.</p>';
    return;
  }

  try {
    await Clerk.load({
      ui: { ClerkUI: window.__internal_ClerkUICtor },
    });

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

      const token = await Clerk.session.getToken();
      const response = await fetch(apiBase + "/api/onboard", {
        method: "POST",
        headers: {
          "Authorization": "Bearer " + token,
          "Content-Type": "application/json"
        },
        body: "{}"
      });
      const payload = await response.json();

      if (!response.ok) {
        document.getElementById("backend-status").textContent =
          "Backend connection failed: " + (payload.error || response.status);
        return;
      }

      document.getElementById("backend-status").textContent =
        payload.created
          ? "Pro Beta account created and connected."
          : "Pro Beta account connected.";
    } else {
      target.innerHTML = "<div id='sign-in'></div>";
      Clerk.mountSignIn(document.getElementById("sign-in"));
    }
  } catch (error) {
    target.innerHTML = '<p class="error">Authentication failed to initialize.</p>';
  }
});
