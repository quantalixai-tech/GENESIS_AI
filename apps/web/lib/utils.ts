/**
 * cn() — merge Tailwind classes with clsx + tailwind-merge.
 *
 * This is the canonical utility for the @genesis/ui package.
 * All components import from here: import { cn } from "@/lib/utils"
 */

import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
