// Simple toast notification utility
const TOAST_DURATION = 2500;
const CONTAINER_ID = "aha-toast-container";

const TYPE_STYLES = {
  success: {
    border: "border-blue-500",
    icon: "✅",
  },
  info: {
    border: "border-blue-500",
    icon: "ℹ️",
  },
  error: {
    border: "border-red-500",
    icon: "⛔",
  },
  warning: {
    border: "border-amber-400",
    icon: "⚠️",
  },
};

const AUTH_ERROR_MESSAGES = {
  "auth/invalid-email": "อีเมลไม่ถูกต้อง",
  "auth/missing-email": "กรุณากรอกอีเมล",
  "auth/missing-input": "กรุณากรอกข้อมูลให้ครบถ้วน",
  "auth/user-disabled": "บัญชีนี้ถูกระงับการใช้งาน",
  "auth/user-not-found": "ไม่พบบัญชีผู้ใช้",
  "auth/wrong-password": "รหัสผ่านไม่ถูกต้อง",
  "auth/invalid-credential": "ข้อมูลเข้าสู่ระบบไม่ถูกต้อง",
  "auth/email-already-in-use": "อีเมลนี้ถูกใช้งานแล้ว",
  "auth/weak-password": "รหัสผ่านสั้นเกินไป",
  "auth/missing-password": "กรุณากรอกรหัสผ่าน",
  "auth/password-mismatch": "กรุณายืนยันรหัสผ่านให้ตรงกัน",
  "auth/too-many-requests": "พยายามเข้าสู่ระบบบ่อยเกินไป โปรดลองใหม่ภายหลัง",
  "auth/network-request-failed": "ไม่สามารถเชื่อมต่อเครือข่ายได้",
  "auth/operation-not-allowed": "วิธีการนี้ยังไม่เปิดใช้งาน",
  "auth/popup-closed-by-user": "คุณปิดหน้าต่างก่อนดำเนินการเสร็จ",
  "auth/requires-recent-login": "กรุณาเข้าสู่ระบบอีกครั้งเพื่อดำเนินการ",
  "auth/credential-already-in-use": "บัญชีนี้เชื่อมโยงกับบริการอื่นแล้ว",
  "app/missing-firebase-config": "ระบบยังไม่ได้ตั้งค่าการเชื่อมต่อกับ Firebase",
};

const DEFAULT_AUTH_ERROR = "เกิดข้อผิดพลาดที่ไม่ทราบสาเหตุ";

let toastContainer;

function ensureContainer() {
  if (toastContainer && document.body.contains(toastContainer)) {
    return toastContainer;
  }

  toastContainer = document.createElement("div");
  toastContainer.id = CONTAINER_ID;
  toastContainer.className = "pointer-events-none fixed top-4 right-4 z-[9999] flex w-full max-w-[360px] flex-col gap-3";
  document.body.appendChild(toastContainer);
  return toastContainer;
}

function buildToast(type, title, text) {
  const { border, icon } = TYPE_STYLES[type] ?? TYPE_STYLES.info;
  const toast = document.createElement("div");
  toast.className = `pointer-events-auto flex w-full max-w-[360px] gap-3 rounded-xl border-l-4 bg-white px-4 py-3 shadow-lg ring-1 ring-black/5 transition-all duration-200 ease-out ${border}`;
  toast.setAttribute("role", "status");
  toast.setAttribute("aria-live", "polite");
  toast.setAttribute("aria-atomic", "true");

  const iconWrap = document.createElement("div");
  iconWrap.className = "mt-0.5 text-lg";
  iconWrap.textContent = icon;

  const content = document.createElement("div");
  content.className = "flex-1 overflow-hidden text-[14px] leading-snug text-slate-700";

  if (title) {
    const heading = document.createElement("p");
    heading.className = "font-semibold text-slate-900";
    heading.textContent = title;
    content.appendChild(heading);
  }

  if (text) {
    const body = document.createElement("p");
    body.className = "mt-1 text-slate-600";
    body.textContent = text;
    content.appendChild(body);
  }

  const closeBtn = document.createElement("button");
  closeBtn.type = "button";
  closeBtn.className = "ml-2 shrink-0 rounded-full px-2 py-1 text-sm font-semibold text-slate-400 transition hover:bg-slate-100 hover:text-slate-600";
  closeBtn.setAttribute("aria-label", "ปิดการแจ้งเตือน");
  closeBtn.textContent = "×";

  toast.appendChild(iconWrap);
  toast.appendChild(content);
  toast.appendChild(closeBtn);

  return { toast, closeBtn };
}

function animateIn(element) {
  element.style.opacity = "0";
  element.style.transform = "translateY(-6px)";
  requestAnimationFrame(() => {
    element.style.opacity = "1";
    element.style.transform = "translateY(0)";
  });
}

function animateOut(element) {
  element.style.opacity = "0";
  element.style.transform = "translateY(-6px)";
  element.style.transition = "opacity 150ms ease, transform 150ms ease";
}

export function notify(type, title, text = "") {
  const container = ensureContainer();
  const { toast, closeBtn } = buildToast(type, title, text);

  const dismiss = () => {
    if (!toast.isConnected) return;
    animateOut(toast);
    setTimeout(() => {
      if (toast.isConnected) {
        toast.remove();
      }
      if (container.childElementCount === 0 && container.parentElement) {
        container.parentElement.removeChild(container);
        toastContainer = undefined;
      }
    }, 160);
  };

  let hideTimer = setTimeout(dismiss, TOAST_DURATION);

  closeBtn.addEventListener("click", () => {
    clearTimeout(hideTimer);
    dismiss();
  });

  toast.addEventListener("mouseenter", () => {
    clearTimeout(hideTimer);
  });

  toast.addEventListener("mouseleave", () => {
    hideTimer = setTimeout(dismiss, TOAST_DURATION / 1.5);
  });

  container.appendChild(toast);
  animateIn(toast);
  return toast;
}

export const notifySuccess = (title, text = "") => notify("success", title, text);
export const notifyError = (title, text = "") => notify("error", title, text);
export const notifyInfo = (title, text = "") => notify("info", title, text);
export const notifyWarning = (title, text = "") => notify("warning", title, text);

export function getAuthErrorMessage(error) {
  if (!error) return DEFAULT_AUTH_ERROR;
  const code = typeof error.code === "string" ? error.code : "";
  if (code && AUTH_ERROR_MESSAGES[code]) {
    return AUTH_ERROR_MESSAGES[code];
  }
  const message = typeof error.message === "string" ? error.message.trim() : "";
  return message || DEFAULT_AUTH_ERROR;
}

function userIdentifier(user, fallback = "") {
  const email = (user && typeof user.email === "string") ? user.email.trim() : "";
  return email || (fallback ? fallback.trim() : "");
}

function accountSubtitle(user, fallback) {
  const identifier = userIdentifier(user, fallback);
  return identifier ? `บัญชี: ${identifier}` : "";
}

export function toastLoginSuccess(user, identifier) {
  notifySuccess("เข้าสู่ระบบสำเร็จ", accountSubtitle(user, identifier));
}

export function toastLoginError(error) {
  notifyError("เข้าสู่ระบบไม่สำเร็จ", getAuthErrorMessage(error));
}

export function toastSignupSuccess(user, identifier) {
  const subtitle = accountSubtitle(user, identifier) || "ยินดีต้อนรับสู่ AI Health Analyze";
  notifySuccess("สมัครสมาชิกสำเร็จ", subtitle);
}

export function toastSignupError(error) {
  notifyError("สมัครสมาชิกไม่สำเร็จ", getAuthErrorMessage(error));
}

export function toastLogoutSuccess() {
  notifySuccess("ออกจากระบบแล้ว", "กลับมาเมื่อไรก็ยินดีต้อนรับ");
}

export function toastLogoutError(error) {
  notifyError("ออกจากระบบไม่สำเร็จ", getAuthErrorMessage(error));
}

export function toastProfileUpdateSuccess() {
  notifySuccess("อัปเดตโปรไฟล์สำเร็จ");
}

export function toastProfileUpdateError(error) {
  notifyError("อัปเดตโปรไฟล์ไม่สำเร็จ", getAuthErrorMessage(error));
}

export function toastProfileMissingUser() {
  notifyError("อัปเดตโปรไฟล์ไม่สำเร็จ", "ไม่พบผู้ใช้ กรุณาเข้าสู่ระบบก่อน");
}

export function toastAuthenticatedInfo(user) {
  notifyInfo("เข้าสู่ระบบแล้ว", accountSubtitle(user));
}
