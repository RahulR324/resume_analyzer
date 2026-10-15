document.addEventListener("click", async (event) => {
  const button = event.target.closest(".js-copy");
  if (!button) return;
  let text = button.getAttribute("data-copy") || "";
  const elId = button.getAttribute("data-copy-el");
  if (elId) {
    const node = document.getElementById(elId);
    text = node ? node.innerText : text;
  }
  try {
    await navigator.clipboard.writeText(text);
    const previous = button.textContent;
    button.textContent = "Copied";
    setTimeout(() => {
      button.textContent = previous;
    }, 1400);
  } catch (err) {
    button.textContent = "Copy failed";
  }
});
function togglePassword(btn, e) {
  if (e) {
    e.preventDefault();
    e.stopPropagation();
  }
  const wrapper = btn.closest(".password-wrapper");
  if (!wrapper) return;
  const input = wrapper.querySelector("input");
  if (!input) return;

  const eyeShow = btn.querySelector(".eye-show");
  const eyeHide = btn.querySelector(".eye-hide");

  if (input.type === "password") {
    input.type = "text";
    if (eyeShow) eyeShow.style.display = "none";
    if (eyeHide) eyeHide.style.display = "block";
    btn.setAttribute("aria-label", "Hide password");
  } else {
    input.type = "password";
    if (eyeShow) eyeShow.style.display = "block";
    if (eyeHide) eyeHide.style.display = "none";
    btn.setAttribute("aria-label", "Show password");
  }
}
window.togglePassword = togglePassword;

document.addEventListener("click", (event) => {
  const toggleBtn = event.target.closest(".password-toggle");
  if (toggleBtn) {
    togglePassword(toggleBtn, event);
    return;
  }

  const navToggle = event.target.closest("#navToggle");
  const navLinks = document.getElementById("navLinks");
  if (navToggle && navLinks) {
    const isOpen = navLinks.classList.toggle("is-open");
    navToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    return;
  }

  if (navLinks && navLinks.classList.contains("is-open") && !event.target.closest("#navLinks")) {
    navLinks.classList.remove("is-open");
    const toggle = document.getElementById("navToggle");
    if (toggle) toggle.setAttribute("aria-expanded", "false");
  }
});

