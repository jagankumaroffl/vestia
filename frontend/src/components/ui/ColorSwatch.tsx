import { colorSwatch, isLightColor, titleCase } from "@/utils/colorUtils";
import { cn } from "@/utils/cn";

interface ColorSwatchProps {
  name: string;
  size?: number;
  className?: string;
}

export function ColorSwatch({ name, size = 14, className }: ColorSwatchProps) {
  return (
    <span
      title={titleCase(name)}
      className={cn(
        "inline-block rounded-full shrink-0",
        isLightColor(name) && "ring-1 ring-line",
        className
      )}
      style={{
        width: size,
        height: size,
        backgroundColor: colorSwatch(name),
      }}
    />
  );
}
