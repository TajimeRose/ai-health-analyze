import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.4/firebase-app.js";
import {
  getAuth,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  onAuthStateChanged,
  signOut,
  updateProfile
} from "https://www.gstatic.com/firebasejs/10.12.4/firebase-auth.js";

if (!window.FIREBASE_CONFIG) {
  console.error('FIREBASE_CONFIG not found. Did /firebase-config.js load?');
  throw new Error('Firebase config missing');
}

const app = initializeApp(window.FIREBASE_CONFIG);
export const auth = getAuth(app);

export function loginWithEmail(identifier, password) {
  return signInWithEmailAndPassword(auth, identifier.trim(), password);
}

export function signupWithEmail(email, password) {
  return createUserWithEmailAndPassword(auth, email.trim(), password);
}

export function observeAuthState(callback) {
  return onAuthStateChanged(auth, callback);
}

export function logout() {
  return signOut(auth);
}

export function updateProfileInfo(profile) {
  const user = auth.currentUser;
  if (!user) {
    return Promise.reject(new Error('NO_AUTHENTICATED_USER'));
  }
  return updateProfile(user, profile);
}
