import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  LabelList,
  Cell,
  type LabelProps,
} from 'recharts';

type DataType = {
  name: string;
  value: number;
  color: string;
};

type Props = {
  data: DataType[];
};

export default function SimilarityChart({ data }: Props) {
  return (
    <div className="w-67.5 h-67.5 outline-none focus:outline-none focus:ring-0">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{ top: 10, right: 0, left: -30, bottom: 0 }}
        >
          <XAxis
            dataKey="name"
            axisLine={true}
            tickLine={false}
            tick={{ fill: '#000000', fontSize: 12 }}
          />
          <YAxis
            domain={[0, 100]}
            axisLine={true}
            tickLine={true}
            tick={{ fill: '#000000', fontSize: 12 }}
          />

          <Bar dataKey="value" radius={[0, 0, 0, 0]} barSize={50}>
            {/* 막대별 색 */}
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}

            {/* 상단 텍스트 */}
            <LabelList
              dataKey="value"
              position="top"
              content={(props: LabelProps) => {
                const { x = 0, y = 0, width = 0, value = 0, index = 0 } = props;

                return (
                  <text
                    x={Number(x) + Number(width) / 2}
                    y={Number(y) - 8}
                    textAnchor="middle"
                    fill={data[index].color}
                    fontSize={12}
                    fontWeight={500}
                  >
                    {Number(value).toFixed(1)}
                  </text>
                );
              }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
