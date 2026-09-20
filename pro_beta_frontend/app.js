window.addEventListener("load", async function () {
  const target = document.getElementById("auth");
  const key = window.PRO_BETA_CLERK_KEY || "";

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
      target.innerHTML = "<p>Signed in.</p><div id='user-button'></div>";
      Clerk.mountUserButton(document.getElementById("user-button"));
    } else {
      target.innerHTML = "<div id='sign-in'></div>";
      Clerk.mountSignIn(document.getElementById("sign-in"));
    }
  } catch (error) {
    target.innerHTML = '<p class="error">Authentication failed to initialize.</p>';
  }
});
