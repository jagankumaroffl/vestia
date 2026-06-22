import { Card, CardBody } from "@/components/ui/Card";

interface StatCardProps {
  value: string | number;
  label: string;
}

export function StatCard({ value, label }: StatCardProps) {
  return (
    <Card>
      <CardBody className="text-center">
        <p className="font-display text-3xl text-ink">{value}</p>
        <p className="eyebrow mt-1.5">{label}</p>
      </CardBody>
    </Card>
  );
}
