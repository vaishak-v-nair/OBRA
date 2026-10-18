"use client";
import { useSyncExternalStore } from "react";
function subscribe(callback: () => void) { window.addEventListener("hashchange", callback); return () => window.removeEventListener("hashchange", callback); }
function snapshot() { return window.location.hash; }
function serverSnapshot() { return ""; }
export function useHash() { return useSyncExternalStore(subscribe, snapshot, serverSnapshot); }
