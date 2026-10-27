"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";

export function FloatingInput({
  id,
  label,
  value,
  onChange,
  placeholder,
  type = "text",
  icon,
  error,
  required,
  disabled = false,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: string;
  icon?: string;
  error?: string;
  required?: boolean;
  disabled?: boolean;
}) {
  const [focused, setFocused] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const hasValue = value.length > 0;
  const isPassword = type === "password";
  const effectiveType = isPassword && showPassword ? "text" : type;

  return (
    <div className="relative">
      <div className={cn(
        "relative rounded-xl border-2 bg-card transition-all",
        focused ? "border-primary ring-2 ring-primary/20" : "border-border",
        error && "border-destructive ring-0 bg-destructive/5",
        disabled && "opacity-60 bg-muted"
      )}>
        {icon && (
          <span className={cn(
            "material-symbols-outlined absolute left-3.5 top-1/2 -translate-y-1/2 text-[18px] transition-colors",
            focused ? "text-primary" : "text-muted-foreground",
            error && "text-destructive"
          )}>
            {icon}
          </span>
        )}
        <input
          id={id}
          type={effectiveType}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder={focused ? placeholder : ""}
          disabled={disabled}
          className={cn(
            "w-full bg-transparent py-3.5 text-sm outline-none",
            icon ? "pl-11" : "pl-4",
            isPassword ? "pr-11" : "pr-4",
            disabled && "cursor-not-allowed"
          )}
        />
        {isPassword && (
          <button
            type="button"
            tabIndex={-1}
            onClick={() => setShowPassword((s) => !s)}
            className={cn(
              "absolute right-3 top-1/2 -translate-y-1/2 p-1 transition-colors",
              "text-muted-foreground hover:text-primary",
              error && "text-destructive hover:text-destructive"
            )}
            aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
          >
            <span className="material-symbols-outlined text-[18px]">
              {showPassword ? "visibility_off" : "visibility"}
            </span>
          </button>
        )}
        <label
          htmlFor={id}
          className={cn(
            "absolute left-0 transition-all pointer-events-none",
            icon ? "left-11" : "left-4",
            (focused || hasValue)
              ? "-top-2.5 text-[10px] font-bold bg-card px-1.5 text-primary"
              : "top-1/2 -translate-y-1/2 text-sm text-muted-foreground",
            error && "text-destructive"
          )}
        >
          {label}{required && <span className="text-destructive ml-0.5">*</span>}
        </label>
      </div>
      {error && (
        <div className="flex items-center gap-1.5 mt-1.5 text-destructive">
          <span className="material-symbols-outlined text-[14px]">error</span>
          <p className="text-xs font-medium">{error}</p>
        </div>
      )}
    </div>
  );
}
