import { subskills } from '@/lib/mock/data';

export default function MapperPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">80/20 Mapper</h2>
      <div className="overflow-x-auto rounded border border-slate-800">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-900">
            <tr>
              <th className="p-2">Subskill</th>
              <th className="p-2">Importance</th>
              <th className="p-2">Frequency</th>
              <th className="p-2">Bottleneck</th>
              <th className="p-2">Transfer</th>
            </tr>
          </thead>
          <tbody>
            {subskills.map((s) => (
              <tr key={s.id} className="border-t border-slate-800">
                <td className="p-2">{s.title}</td>
                <td className="p-2">{s.importance}</td>
                <td className="p-2">{s.frequency}</td>
                <td className="p-2">{s.bottleneck}</td>
                <td className="p-2">{s.transferValue}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
