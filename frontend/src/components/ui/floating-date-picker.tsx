"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverTrigger, PopoverContent } from "@/components/ui/popover";

export function FloatingDatePicker({
  id,
  label,
  value,
  onChange,
  icon = "calendar_today",
  error,
  required,
  disabled = false,
  disabledDates,
  placeholder = "Seleccionar fecha...",
  className,
}: {
  id: string;
  label: string;
  value: Date | undefined;
  onChange: (date: Date | undefined) => void;
  icon?: string;
  error?: string;
  required?: boolean;
  disabled?: boolean;
  disabledDates?: (date: Date) => boolean;
  placeholder?: string;
  className?: string;
}) {
  const [open, setOpen] = useState(false);
  const hasValue = !!value;

  return (
    <div className={cn("relative", className)}>
      <Popover open={open} onOpenChange={disabled ? undefined : setOpen}>
        <PopoverTrigger asChild>
          <button
            id={id}
            type="button"
            disabled={disabled}
            className={cn(
              "relative w-full flex items-center rounded-xl border-2 bg-card transition-all text-left",
              open ? "border-primary ring-2 ring-primary/20" : "border-border",
              error && "border-destructive ring-0 bg-destructive/5",
              disabled && "opacity-60 bg-muted cursor-not-allowed"
            )}
          >
            <span className={cn(
              "material-symbols-outlined absolute left-3.5 top-1/2 -translate-y-1/2 text-[18px] transition-colors",
              open ? "text-primary" : "text-muted-foreground",
              error && "text-destructive"
            )}>
              {icon}
            </span>
            <span className={cn(
              "w-full py-3.5 pl-11 pr-4 text-sm",
              !hasValue && "text-muted-foreground"
            )}>
              {hasValue
                ? value.toLocaleDateString("es-CO", { day: "2-digit", month: "long", year: "numeric" })
                : (open ? placeholder : "\u00A0")
              }
            </span>
            <label
              className={cn(
                "absolute left-11 transition-all pointer-events-none",
                (open || hasValue)
                  ? "-top-2.5 text-[10px] font-bold bg-card px-1.5 text-primary"
                  : "top-1/2 -translate-y-1/2 text-sm text-muted-foreground",
                error && "text-destructive"
              )}
            >
              {label}{required && <span className="text-destructive ml-0.5">*</span>}
            </label>
          </button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start" sideOffset={8}>
          <Calendar
            mode="single"
            selected={value}
            onSelect={(date) => {
              onChange(date);
              setOpen(false);
            }}
            disabled={disabledDates}
            className="rounded-lg"
          />
        </PopoverContent>
      </Popover>
      {error && (
        <div className="flex items-center gap-1.5 mt-1.5 text-destructive">
          <span className="material-symbols-outlined text-[14px]">error</span>
          <p className="text-xs font-medium">{error}</p>
        </div>
      )}
    </div>
  );
}

export function FloatingTimePicker({
  id,
  label,
  value,
  onChange,
  icon = "schedule",
  error,
  required,
  disabled = false,
}: {
  id: string;
  label: string;
  value: number | undefined;
  onChange: (hour: number) => void;
  icon?: string;
  error?: string;
  required?: boolean;
  disabled?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const hasValue = value != null;

  return (
    <div className="relative">
      <Popover open={open} onOpenChange={disabled ? undefined : setOpen}>
        <PopoverTrigger asChild>
          <button
            id={id}
            type="button"
            disabled={disabled}
            className={cn(
              "relative w-full flex items-center rounded-xl border-2 bg-card transition-all text-left",
              open ? "border-primary ring-2 ring-primary/20" : "border-border",
              error && "border-destructive ring-0 bg-destructive/5",
              disabled && "opacity-60 bg-muted cursor-not-allowed"
            )}
          >
            <span className={cn(
              "material-symbols-outlined absolute left-3.5 top-1/2 -translate-y-1/2 text-[18px] transition-colors",
              open ? "text-primary" : "text-muted-foreground",
              error && "text-destructive"
            )}>
              {icon}
            </span>
            <span className={cn(
              "w-full py-3.5 pl-11 pr-4 text-sm",
              !hasValue && "text-muted-foreground"
            )}>
              {hasValue ? `${String(value).padStart(2, "0")}:00` : (open ? "Seleccionar hora..." : "\u00A0")}
            </span>
            <label
              className={cn(
                "absolute left-11 transition-all pointer-events-none",
                (open || hasValue)
                  ? "-top-2.5 text-[10px] font-bold bg-card px-1.5 text-primary"
                  : "top-1/2 -translate-y-1/2 text-sm text-muted-foreground",
                error && "text-destructive"
              )}
            >
              {label}{required && <span className="text-destructive ml-0.5">*</span>}
            </label>
          </button>
        </PopoverTrigger>
        <PopoverContent className="w-48 p-2" align="start" sideOffset={8}>
          <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mb-2 px-1">
            {label}
          </p>
          <div className="grid grid-cols-4 gap-1 max-h-48 overflow-y-auto custom-scrollbar">
            {Array.from({ length: 24 }, (_, i) => (
              <button
                key={i}
                type="button"
                onClick={() => {
                  onChange(i);
                  setOpen(false);
                }}
                className={cn(
                  "px-1 py-1.5 rounded-md text-xs font-semibold transition-all",
                  value === i
                    ? "bg-primary text-white shadow-sm"
                    : "hover:bg-muted text-foreground"
                )}
              >
                {String(i).padStart(2, "0")}:00
              </button>
            ))}
          </div>
        </PopoverContent>
      </Popover>
      {error && (
        <div className="flex items-center gap-1.5 mt-1.5 text-destructive">
          <span className="material-symbols-outlined text-[14px]">error</span>
          <p className="text-xs font-medium">{error}</p>
        </div>
      )}
    </div>
  );
}
