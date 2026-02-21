import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

type Props = {
  score: number;
};

export default function SimilarityGauge({ score }: Props) {
  const data = [{ value: score }, { value: 100 - score }];

  return (
    <div className="relative w-40.5 h-40.5">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            innerRadius={68}
            outerRadius={81}
            startAngle={90}
            endAngle={-270}
            dataKey="value"
            stroke="none"
            cornerRadius={50}
          >
            <Cell fill="#1E3A8A" />
            <Cell fill="#D2D8E8" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>

      <div className="absolute inset-0 flex flex-col items-center justify-center gap-1">
        <span className="text-gray-900 typo-body_med20">닮음 지수</span>
        <span className="text-primary-900 typo-h2_bold24">{score}점</span>
      </div>
    </div>
  );
}
