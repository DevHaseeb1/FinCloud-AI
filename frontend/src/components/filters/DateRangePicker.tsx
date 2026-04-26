"use client";

import * as React from "react";
import { addDays, format } from "date-fns";
import { Calendar as CalendarIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";

type Range = { from?: Date; to?: Date };

export function DateRangePicker({
  value,
  onChange,
}: {
  value?: Range;
  onChange: (range: Range) => void;
}) {
  const [open, setOpen] = React.useState(false);

  const label =
    value?.from && value?.to
      ? `${format(value.from, "MMM d, yyyy")} - ${format(value.to, "MMM d, yyyy")}`
      : value?.from
        ? `${format(value.from, "MMM d, yyyy")} - …`
        : "Pick a date range";

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger
        className={cn(
          "inline-flex h-9 items-center justify-start rounded-md border bg-background px-3 text-sm font-normal shadow-xs hover:bg-accent hover:text-accent-foreground",
          !value?.from && "text-muted-foreground",
        )}
      >
        <CalendarIcon className="mr-2 size-4" />
        {label}
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <Calendar
          mode="range"
          selected={value as any}
          onSelect={(r: any) => onChange(r ?? {})}
          numberOfMonths={2}
          defaultMonth={value?.from ?? addDays(new Date(), -30)}
        />
      </PopoverContent>
    </Popover>
  );
}

