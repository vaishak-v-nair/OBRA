import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-medium transition-colors disabled:pointer-events-none disabled:opacity-50 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-ring [&_svg]:size-4",
  { variants: { variant: {
    default: "bg-primary text-primary-foreground hover:bg-primary/90",
    outline: "border border-border bg-surface hover:bg-muted",
    ghost: "hover:bg-muted text-secondary hover:text-foreground",
  }, size: { default: "h-10 px-4", sm: "h-9 px-3", icon: "size-10" } },
    defaultVariants: { variant: "default", size: "default" } },
);
function Button({ className, variant, size, asChild = false, ...props }:
  React.ComponentProps<"button"> & VariantProps<typeof buttonVariants> & { asChild?: boolean }) {
  const Comp = asChild ? Slot : "button";
  return <Comp data-slot="button" className={cn(buttonVariants({ variant, size, className }))} {...props} />;
}
export { Button, buttonVariants };
