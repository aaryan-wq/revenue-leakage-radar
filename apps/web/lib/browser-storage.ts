type StorageLike = Pick<Storage, "getItem" | "setItem" | "removeItem" | "key" | "length">;

function resolveStorage(type: "local" | "session"): StorageLike | null {
  if (typeof window === "undefined") return null;

  try {
    const storage = type === "local" ? window.localStorage : window.sessionStorage;
    if (!storage) return null;

    const testKey = "__rlr_storage_test__";
    storage.setItem(testKey, "1");
    storage.removeItem(testKey);
    return storage;
  } catch {
    return null;
  }
}

export function getLocalStorage(): StorageLike | null {
  return resolveStorage("local");
}

export function getSessionStorage(): StorageLike | null {
  return resolveStorage("session");
}

export function localStorageGetItem(key: string): string | null {
  return getLocalStorage()?.getItem(key) ?? null;
}

export function localStorageSetItem(key: string, value: string): boolean {
  try {
    getLocalStorage()?.setItem(key, value);
    return getLocalStorage() !== null;
  } catch {
    return false;
  }
}

export function localStorageRemoveItem(key: string): void {
  try {
    getLocalStorage()?.removeItem(key);
  } catch {
    // Storage unavailable or blocked.
  }
}

export function sessionStorageGetItem(key: string): string | null {
  return getSessionStorage()?.getItem(key) ?? null;
}

export function sessionStorageSetItem(key: string, value: string): boolean {
  try {
    getSessionStorage()?.setItem(key, value);
    return getSessionStorage() !== null;
  } catch {
    return false;
  }
}

export function sessionStorageRemoveItem(key: string): void {
  try {
    getSessionStorage()?.removeItem(key);
  } catch {
    // Storage unavailable or blocked.
  }
}

export function getPostHogPersistence(): "localStorage+cookie" | "cookie" {
  return getLocalStorage() ? "localStorage+cookie" : "cookie";
}
