import * as React from "react";
import { cn } from "@/lib/utils";

type ScrollAreaOrientation = "vertical" | "horizontal" | "both";

const overflowByOrientation: Record<ScrollAreaOrientation, string> = {
  vertical: "overflow-x-hidden overflow-y-auto",
  horizontal: "overflow-x-auto overflow-y-hidden",
  both: "overflow-auto"
};

export interface ScrollAreaProps extends React.HTMLAttributes<HTMLDivElement> {
  orientation?: ScrollAreaOrientation;
  viewportClassName?: string;
}

export const ScrollArea = React.forwardRef<HTMLDivElement, ScrollAreaProps>(
  ({ className, viewportClassName, orientation = "vertical", children, ...props }, ref) => (
    <div className={cn("relative overflow-hidden", className)}>
      <div
        ref={ref}
        className={cn(
          "no-scrollbar h-full w-full rounded-[inherit] overscroll-contain",
          overflowByOrientation[orientation],
          viewportClassName
        )}
        {...props}
      >
        {children}
      </div>
    </div>
  )
);
ScrollArea.displayName = "ScrollArea";
