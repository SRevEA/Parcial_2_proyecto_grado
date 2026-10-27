"use client";

import { useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";

export interface ChipOption<T extends string = string> {
  key: T;
  label: string;
  icon?: string | null;
  color?: string | null;
}

interface BaseProps<T extends string> {
  label: string;
  icon: string;
  options: ChipOption<T>[];
  iconMap?: Record<string, string>;
  styleMap?: Record<string, { bg: string; text: string; border: string }>;
  colorMap?: Record<string, string | null>;
  searchable?: boolean;
  placeholder?: string;
  required?: boolean;
  error?: string;
  className?: string;
  hideLabel?: boolean;
  floatingLabel?: boolean;
}

type SingleProps<T extends string> = BaseProps<T> & {
  multiSelect?: false;
  value: T;
  onChange: (value: T) => void;
};

type MultiProps<T extends string> = BaseProps<T> & {
  multiSelect: true;
  value: T[];
  onChange: (value: T[]) => void;
};

type ChipSelectorProps<T extends string> = SingleProps<T> | MultiProps<T>;

export function ChipSelector<T extends string>(props: ChipSelectorProps<T>) {
  const {
    label,
    icon,
    options,
    iconMap,
    styleMap,
    colorMap,
    searchable = false,
    placeholder = "Seleccionar...",
    required = false,
    error,
    className,
    hideLabel = false,
    floatingLabel = false,
  } = props;

  const isMulti = props.multiSelect === true;
  const singleValue = !isMulti ? (props.value as T) : ("" as T);
  const multiValue = isMulti ? (props.value as T[]) : [];

  const [open, setOpen] = useState(false);
  const [openUpward, setOpenUpward] = useState(false);
  const [search, setSearch] = useState("");
  const ref = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
        setSearch("");
      }
    }
    if (open) document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  useEffect(() => {
    if (open && searchable && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [open, searchable]);

  useEffect(() => {
    if (!open || !ref.current) return;
    const caja = ref.current.getBoundingClientRect();
    const alto = Math.min(options.length, 6) * 44 + (searchable ? 56 : 0) + 24;
    setOpenUpward(window.innerHeight - caja.bottom < alto && caja.top > alto);
  }, [open, options.length, searchable]);

  const style = !isMulti ? styleMap?.[singleValue] : undefined;
  const currentOption = !isMulti ? options.find((o) => o.key === singleValue) : undefined;
  const currentColor = !isMulti ? (colorMap?.[singleValue] || currentOption?.color) : undefined;

  const selectedCount = multiValue.length;
  const hasMultiSelection = selectedCount > 0;

  const filteredOptions =
    searchable && search
      ? options.filter((opt) => opt.label.toLowerCase().includes(search.toLowerCase()))
      : options;

  const handleSelect = (key: T) => {
    if (isMulti) {
      const next = multiValue.includes(key)
        ? multiValue.filter((v) => v !== key)
        : [...multiValue, key];
      (props as MultiProps<T>).onChange(next);
    } else {
      (props as SingleProps<T>).onChange(key);
      setOpen(false);
      setSearch("");
    }
  };

  const clearMulti = (e: React.MouseEvent) => {
    e.stopPropagation();
    (props as MultiProps<T>).onChange([]);
  };

  const hasSelection = isMulti ? hasMultiSelection : !!currentOption;
  const showFloatingLabelFloated = floatingLabel && (hasSelection || open);

  return (
    <div ref={ref} className={cn("relative", className)}>
      {!hideLabel && !floatingLabel && (
        <div className="flex items-center gap-2 mb-2">
          <p
            className={cn(
              "text-[10px] font-black uppercase tracking-widest",
              error ? "text-destructive" : "text-muted-foreground"
            )}
          >
            {label}
            {required && <span className="text-destructive ml-0.5">*</span>}
          </p>
        </div>
      )}
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className={cn(
          "w-full flex items-center justify-between gap-2 px-4 py-3 rounded-xl border-2 transition-all text-left",
          "hover:shadow-md active:scale-[0.99]",
          error && "border-destructive ring-0 bg-destructive/5",
          !error && isMulti && hasMultiSelection && "border-primary/60 bg-primary/5",
          !error && !isMulti && style
            ? `${style.bg} ${style.text} ${style.border}`
            : !error && !(isMulti && hasMultiSelection) && "bg-card border-border hover:border-primary/40"
        )}
      >
        <div className="flex items-center gap-2.5 min-w-0">
          <span
            className={cn(
              "material-symbols-outlined text-[18px]",
              !isMulti && style ? style.text : "",
              isMulti && hasMultiSelection ? "text-primary" : "",
              floatingLabel && !hasSelection && "text-muted-foreground"
            )}
            style={!isMulti && currentColor ? { color: currentColor } : undefined}
          >
            {!isMulti ? iconMap?.[singleValue] || currentOption?.icon || icon : icon}
          </span>
          {isMulti ? (
            <span
              className={cn(
                "font-bold text-sm truncate",
                hasMultiSelection ? "text-foreground" : "text-muted-foreground"
              )}
            >
              {floatingLabel && !hasMultiSelection
                ? ""
                : hasMultiSelection
                ? selectedCount === 1
                  ? options.find((o) => o.key === multiValue[0])?.label || placeholder
                  : `${selectedCount} seleccionados`
                : placeholder}
            </span>
          ) : (
            <span className={cn("font-bold text-sm truncate", !currentOption && "text-muted-foreground")}>
              {floatingLabel && !currentOption ? "" : currentOption?.label || placeholder}
            </span>
          )}
        </div>
        <div className="flex items-center gap-1 shrink-0">
          {isMulti && hasMultiSelection && (
            <span
              role="button"
              onClick={clearMulti}
              className="p-1 hover:text-destructive transition-colors text-muted-foreground"
              aria-label="Limpiar"
            >
              <span className="material-symbols-outlined text-[16px]">close</span>
            </span>
          )}
          <span className="material-symbols-outlined text-[16px] opacity-50">
            {open ? "expand_less" : "expand_more"}
          </span>
        </div>
      </button>
      {floatingLabel && (
        <label
          className={cn(
            "absolute pointer-events-none transition-all",
            showFloatingLabelFloated
              ? "-top-2.5 left-3 text-[10px] font-bold bg-card px-1.5 text-primary z-10"
              : "top-1/2 -translate-y-1/2 left-11 text-sm text-muted-foreground",
            error && "text-destructive"
          )}
        >
          {label}
          {required && <span className="text-destructive ml-0.5">*</span>}
        </label>
      )}

      {open && (
        <div
          className={cn(
            "absolute left-0 right-0 z-50 bg-card border border-border rounded-xl shadow-xl shadow-black/10 dark:shadow-black/40 overflow-hidden animate-in fade-in-0 zoom-in-95 duration-150",
            openUpward ? "bottom-full mb-2" : "top-full mt-2"
          )}
        >
          {searchable && (
            <div className="p-2 border-b border-border">
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[16px] text-muted-foreground">
                  search
                </span>
                <input
                  ref={searchInputRef}
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Buscar..."
                  className="w-full pl-9 pr-3 py-2 text-sm bg-muted/50 border-0 rounded-lg outline-none focus:ring-2 focus:ring-primary/30"
                />
              </div>
            </div>
          )}
          <div className="p-1.5 max-h-[240px] overflow-y-auto custom-scrollbar">
            {filteredOptions.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">No se encontraron resultados</p>
            ) : (
              filteredOptions.map((opt) => {
                const optStyle = styleMap?.[opt.key];
                const isSelected = isMulti
                  ? multiValue.includes(opt.key)
                  : singleValue === opt.key;
                const optColor = colorMap?.[opt.key] || opt.color;
                return (
                  <button
                    key={opt.key}
                    type="button"
                    onClick={() => handleSelect(opt.key)}
                    className={cn(
                      "w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm transition-colors",
                      isSelected
                        ? "bg-primary/10 text-primary font-bold"
                        : "hover:bg-muted text-foreground"
                    )}
                  >
                    <span
                      className={cn(
                        "material-symbols-outlined text-[16px]",
                        isSelected ? "text-primary" : optStyle ? optStyle.text : "text-muted-foreground"
                      )}
                      style={!isSelected && optColor ? { color: optColor } : undefined}
                    >
                      {isSelected
                        ? isMulti
                          ? "check_box"
                          : "check_circle"
                        : isMulti
                        ? "check_box_outline_blank"
                        : iconMap?.[opt.key] || opt.icon || "radio_button_unchecked"}
                    </span>
                    {optStyle ? (
                      <span
                        className={cn(
                          "px-2 py-0.5 rounded text-[11px] font-bold border",
                          optStyle.bg,
                          optStyle.text,
                          optStyle.border
                        )}
                      >
                        {opt.label}
                      </span>
                    ) : (
                      <span className="flex-1 text-left">{opt.label}</span>
                    )}
                  </button>
                );
              })
            )}
          </div>
          {isMulti && hasMultiSelection && (
            <div className="border-t border-border p-1.5">
              <button
                type="button"
                onClick={() => (props as MultiProps<T>).onChange([])}
                className="w-full text-[11px] text-muted-foreground hover:text-destructive py-1 transition-colors uppercase tracking-wider font-medium"
              >
                Limpiar selección
              </button>
            </div>
          )}
        </div>
      )}
      {error && (
        <div className="flex items-center gap-1.5 mt-1.5 text-destructive">
          <span className="material-symbols-outlined text-[14px]">error</span>
          <p className="text-xs font-medium">{error}</p>
        </div>
      )}
    </div>
  );
}
