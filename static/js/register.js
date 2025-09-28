import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.4/firebase-app.js";
import {
  getAuth,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  onAuthStateChanged,
  signOut,
  updateProfile
} from "https://www.gstatic.com/firebasejs/10.12.4/firebase-auth.js";

let firebaseApp;
let firebaseAuth;

function ensureFirebaseAuth() {
  const config = window.FIREBASE_CONFIG;
  if (!config || typeof config !== 'object') {
    const error = new Error('Firebase configuration missing');
    error.code = 'app/missing-firebase-config';
    throw error;
  }

  if (!firebaseApp) {
    firebaseApp = initializeApp(config);
  }

  if (!firebaseAuth) {
    firebaseAuth = getAuth(firebaseApp);
  }

  return firebaseAuth;
}

export function loginWithEmail(identifier, password) {
  return signInWithEmailAndPassword(ensureFirebaseAuth(), identifier.trim(), password);
}

export function signupWithEmail(email, password) {
  return createUserWithEmailAndPassword(ensureFirebaseAuth(), email.trim(), password);
}

export function observeAuthState(callback) {
  return onAuthStateChanged(ensureFirebaseAuth(), callback);
}

export function logout() {
  return signOut(ensureFirebaseAuth());
}

export function updateProfileInfo(profile) {
  const auth = ensureFirebaseAuth();
  const user = auth.currentUser;
  if (!user) {
    return Promise.reject(new Error('NO_AUTHENTICATED_USER'));
  }
  return updateProfile(user, profile);
}

export function getFirebaseAuth() {
  return ensureFirebaseAuth();
}
