
import React, { useState, useMemo } from 'react';
import { 
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, Line
} from 'recharts';
import { 
  TrendingUp, 
  DollarSign, 
  Percent, 
  Calendar, 
  Settings2,
  Hotel,
  Activity,
  BarChart3,
  Coins,
  ShieldAlert,
  Zap,
  CheckCircle2
} from 'lucide-react';
import { HISTORICAL_DATA, INITIAL_INVESTMENT } from './constants';
import { formatCurrency, formatPercentage, generateProjections, calculateAnnualAggregates } from './utils/finance';
import { SummaryCard } from './components/SummaryCard';

type Scenario = 'pessimistic' | 'moderate' | 'optimistic';

const App: React.FC = () => {
  const [ipcRate, setIpcRate] = useState(4.5);
  const [growthFactor, setGrowthFactor] = useState(2.0);
  const [yearsToProject, setYearsToProject] = useState(10);
  const [viewMode, setViewMode] = useState<'value' | 'percent'>('value');
  const [timeGranularity, setTimeGranularity] = useState<'monthly' | 'yearly'>('yearly');
  const [selectedScenario, setSelectedScenario] = useState<Scenario>('moderate');

  const historicalAnnual = useMemo(() => calculateAnnualAggregates(), []);
  
  const { annual: projectionsAnnual, monthly: projectionsMonthly } = useMemo(() => 
    generateProjections(ipcRate, growthFactor, yearsToProject), 
    [ipcRate, growthFactor, yearsToProject]
  );

  const avgYield = useMemo(() => {
    const total2025 = historicalAnnual[2025] || 0;
    return total2025 / INITIAL_INVESTMENT;
  }, [historicalAnnual]);

  const cumulativeRevenueFrom2026 = useMemo(() => {
    return projectionsAnnual
      .filter(p => p.year !== "2025")
      .reduce((acc, p) => acc + p[selectedScenario], 0);
  }, [projectionsAnnual, selectedScenario]);

  const cumulativeYieldFrom2026 = useMemo(() => {
    return cumulativeRevenueFrom2026 / INITIAL_INVESTMENT;
  }, [cumulativeRevenueFrom2026]);

  const chartData = useMemo(() => {
    if (timeGranularity === 'yearly') {
      const history = Object.entries(historicalAnnual).map(([year, val]) => ({
        label: year,
        actual: val,
        pessimistic: year === "2025" ? val : null,
        moderate: year === "2025" ? val : null,
        optimistic: year === "2025" ? val : null
      }));
      
      const future = projectionsAnnual.filter(p => p.year !== "2025").map(p => ({
        label: p.year,
        actual: null,
        pessimistic: p.pessimistic,
        moderate: p.moderate,
        optimistic: p.optimistic
      }));
      
      return [...history, ...future];
    } else {
      const history = HISTORICAL_DATA.map(d => ({
        label: d.date,
        actual: d.value,
        pessimistic: d.date === '2025-12' ? d.value : null,
        moderate: d.date === '2025-12' ? d.value : null,
        optimistic: d.date === '2025-12' ? d.value : null
      }));
      
      const future = projectionsMonthly.map(p => ({
        label: p.date,
        actual: null,
        pessimistic: p.pessimistic,
        moderate: p.moderate,
        optimistic: p.optimistic
      }));
      
      return [...history, ...future];
    }
  }, [historicalAnnual, projectionsAnnual, projectionsMonthly, timeGranularity]);

  const scenarioLabels: Record<Scenario, string> = {
    pessimistic: 'Escenario Pesimista',
    moderate: 'Escenario Moderado',
    optimistic: 'Escenario Optimista'
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
      {/* Cabecera */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-indigo-600 p-2 rounded-lg">
              <Hotel className="text-white w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">Análisis de Inversión HOTEL NAO CARTAGENA</h1>
              <p className="text-xs text-slate-500 font-medium italic">Proyecciones analizadas bajo <span className="font-bold text-indigo-600">{scenarioLabels[selectedScenario]}</span></p>
            </div>
          </div>
          <div className="flex items-center gap-4">
             <div className="hidden md:flex flex-col items-end">
                <span className="text-xs text-slate-400 font-bold uppercase tracking-tight">Inversión Inicial</span>
                <span className="text-sm font-bold text-indigo-600">{formatCurrency(INITIAL_INVESTMENT)}</span>
             </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        
        {/* Sección KPI */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <SummaryCard 
            title="Ingresos Reales (2025)" 
            value={formatCurrency(historicalAnnual[2025] || 0)} 
            subtitle="Cierre último año histórico"
            icon={<DollarSign className="w-5 h-5" />}
            trend="up"
          />
          <SummaryCard 
            title="Rendimiento Actual" 
            value={formatPercentage(avgYield)} 
            subtitle="ROI actual vs Inversión"
            icon={<Percent className="w-5 h-5" />}
          />
          <SummaryCard 
            title={`Proyección Final (${2025 + yearsToProject})`} 
            value={formatCurrency(projectionsAnnual[projectionsAnnual.length - 1]?.[selectedScenario] || 0)} 
            subtitle={scenarioLabels[selectedScenario]}
            icon={<TrendingUp className="w-5 h-5" />}
            trend="up"
          />
          <SummaryCard 
            title={`Total Acumulado (2026-${2025 + yearsToProject})`} 
            value={formatCurrency(cumulativeRevenueFrom2026)} 
            subtitle={`${scenarioLabels[selectedScenario]} (Rent: ${formatPercentage(cumulativeYieldFrom2026)})`}
            icon={<Coins className="w-5 h-5" />}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Panel de Controles */}
          <div className="lg:col-span-1 space-y-6">
            <section className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <div className="flex items-center gap-2 mb-6 text-slate-800">
                <Settings2 className="w-5 h-5 text-indigo-500" />
                <h2 className="font-bold uppercase text-xs tracking-widest text-slate-400">Panel de Control</h2>
              </div>
              
              <div className="space-y-6">
                {/* Selector de Escenario */}
                <div>
                  <label className="text-xs font-bold text-slate-500 uppercase block mb-3">Modelado de Escenario Principal</label>
                  <div className="grid grid-cols-1 gap-2">
                    <button 
                      onClick={() => setSelectedScenario('pessimistic')}
                      className={`flex items-center gap-3 px-4 py-3 rounded-xl border transition-all text-sm font-bold ${selectedScenario === 'pessimistic' ? 'bg-rose-50 border-rose-200 text-rose-700 shadow-sm' : 'bg-white border-slate-100 text-slate-500 hover:bg-slate-50'}`}
                    >
                      <ShieldAlert className={`w-4 h-4 ${selectedScenario === 'pessimistic' ? 'text-rose-500' : 'text-slate-300'}`} />
                      Pesimista
                    </button>
                    <button 
                      onClick={() => setSelectedScenario('moderate')}
                      className={`flex items-center gap-3 px-4 py-3 rounded-xl border transition-all text-sm font-bold ${selectedScenario === 'moderate' ? 'bg-indigo-50 border-indigo-200 text-indigo-700 shadow-sm' : 'bg-white border-slate-100 text-slate-500 hover:bg-slate-50'}`}
                    >
                      <CheckCircle2 className={`w-4 h-4 ${selectedScenario === 'moderate' ? 'text-indigo-500' : 'text-slate-300'}`} />
                      Moderado
                    </button>
                    <button 
                      onClick={() => setSelectedScenario('optimistic')}
                      className={`flex items-center gap-3 px-4 py-3 rounded-xl border transition-all text-sm font-bold ${selectedScenario === 'optimistic' ? 'bg-emerald-50 border-emerald-200 text-emerald-700 shadow-sm' : 'bg-white border-slate-100 text-slate-500 hover:bg-slate-50'}`}
                    >
                      <Zap className={`w-4 h-4 ${selectedScenario === 'optimistic' ? 'text-emerald-500' : 'text-slate-300'}`} />
                      Optimista
                    </button>
                  </div>
                  <p className="text-[10px] text-slate-400 mt-2 font-medium">Este ajuste afecta los totales de las tarjetas superiores.</p>
                </div>

                <div className="pt-4 border-t border-slate-100">
                  <div className="flex justify-between mb-2">
                    <label className="text-sm font-semibold text-slate-700">IPC Anual Esperado</label>
                    <span className="text-sm font-bold text-indigo-600">{ipcRate}%</span>
                  </div>
                  <input 
                    type="range" min="0" max="15" step="0.1"
                    value={ipcRate} 
                    onChange={(e) => setIpcRate(parseFloat(e.target.value))}
                    className="w-full h-2 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                  />
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <label className="text-sm font-semibold text-slate-700">Crecimiento Orgánico</label>
                    <span className="text-sm font-bold text-indigo-600">{growthFactor}%</span>
                  </div>
                  <input 
                    type="range" min="-5" max="10" step="0.5"
                    value={growthFactor} 
                    onChange={(e) => setGrowthFactor(parseFloat(e.target.value))}
                    className="w-full h-2 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                  />
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <label className="text-sm font-semibold text-slate-700">Años de Proyección</label>
                    <span className="text-sm font-bold text-indigo-600">{yearsToProject} años</span>
                  </div>
                  <input 
                    type="range" min="1" max="25" step="1"
                    value={yearsToProject} 
                    onChange={(e) => setYearsToProject(parseInt(e.target.value))}
                    className="w-full h-2 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                  />
                </div>

                <div className="pt-4 border-t border-slate-100">
                  <div className="flex flex-col gap-4">
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-bold text-slate-500 uppercase">Unidad de medida</label>
                      <div className="flex bg-slate-100 p-1 rounded-lg">
                        <button 
                          onClick={() => setViewMode('value')}
                          className={`px-3 py-1 text-xs rounded-md transition-all font-bold ${viewMode === 'value' ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-500'}`}
                        >
                          $ COP
                        </button>
                        <button 
                          onClick={() => setViewMode('percent')}
                          className={`px-3 py-1 text-xs rounded-md transition-all font-bold ${viewMode === 'percent' ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-500'}`}
                        >
                          % ROI
                        </button>
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <label className="text-xs font-bold text-slate-500 uppercase">Frecuencia Visual</label>
                      <div className="flex bg-slate-100 p-1 rounded-lg">
                        <button 
                          onClick={() => setTimeGranularity('yearly')}
                          className={`px-3 py-1 text-xs rounded-md transition-all font-bold ${timeGranularity === 'yearly' ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-500'}`}
                        >
                          Anual
                        </button>
                        <button 
                          onClick={() => setTimeGranularity('monthly')}
                          className={`px-3 py-1 text-xs rounded-md transition-all font-bold ${timeGranularity === 'monthly' ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-500'}`}
                        >
                          Mensual
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          </div>

          {/* Área de Gráficos */}
          <div className="lg:col-span-2 space-y-8">
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                <div>
                  <h2 className="text-lg font-bold text-slate-800">Proyección de rentabilidad</h2>
                  <p className="text-sm text-slate-500">
                    Historial (2021-2025) vs Escenarios Proyectados (2026+)
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <div className="flex items-center gap-1.5 text-[10px] font-bold text-slate-500 bg-slate-50 px-2 py-1 rounded">
                    <div className="w-2 h-2 bg-indigo-600 rounded-full"></div> Real
                  </div>
                  <div className={`flex items-center gap-1.5 text-[10px] font-bold px-2 py-1 rounded transition-all ${selectedScenario === 'moderate' ? 'bg-emerald-100 text-emerald-700 scale-105' : 'bg-slate-50 text-slate-500'}`}>
                    <div className="w-2 h-2 bg-emerald-500 rounded-full"></div> Moderado
                  </div>
                  <div className={`flex items-center gap-1.5 text-[10px] font-bold px-2 py-1 rounded transition-all ${selectedScenario === 'optimistic' ? 'bg-amber-100 text-amber-700 scale-105' : 'bg-slate-50 text-slate-500'}`}>
                    <div className="w-2 h-2 bg-amber-500 rounded-full"></div> Optimista
                  </div>
                  <div className={`flex items-center gap-1.5 text-[10px] font-bold px-2 py-1 rounded transition-all ${selectedScenario === 'pessimistic' ? 'bg-rose-100 text-rose-700 scale-105' : 'bg-slate-50 text-slate-500'}`}>
                    <div className="w-2 h-2 bg-rose-500 rounded-full"></div> Pesimista
                  </div>
                </div>
              </div>

              <div className="h-[450px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
                    <defs>
                      <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.2}/>
                        <stop offset="95%" stopColor="#4f46e5" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorOpt" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.1}/>
                        <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis 
                      dataKey="label" 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{fontSize: 9, fill: '#64748b', fontWeight: 600}}
                      interval={timeGranularity === 'monthly' ? 8 : 0}
                      padding={{ left: 10, right: 10 }}
                    />
                    <YAxis 
                      axisLine={false} 
                      tickLine={false} 
                      tickFormatter={(val) => `$${(val / 1000000).toFixed(0)}M`}
                      tick={{fontSize: 10, fill: '#64748b', fontWeight: 500}}
                    />
                    <Tooltip 
                      contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 15px 30px -5px rgb(0 0 0 / 0.15)', padding: '12px'}}
                      formatter={(val: number) => [viewMode === 'value' ? formatCurrency(val) : formatPercentage(val / INITIAL_INVESTMENT), 'Valor']}
                      labelStyle={{ fontWeight: 'bold', marginBottom: '8px', color: '#1e293b' }}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="actual" 
                      stroke="#4f46e5" 
                      strokeWidth={4} 
                      fillOpacity={1} 
                      fill="url(#colorActual)" 
                      connectNulls={true}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="pessimistic" 
                      stroke="#ef4444" 
                      strokeWidth={selectedScenario === 'pessimistic' ? 4 : 2} 
                      strokeDasharray={selectedScenario === 'pessimistic' ? "0" : "4 4"} 
                      dot={false} 
                      connectNulls={true}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="moderate" 
                      stroke="#10b981" 
                      strokeWidth={selectedScenario === 'moderate' ? 5 : 3} 
                      fillOpacity={0} 
                      dot={false} 
                      connectNulls={true}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="optimistic" 
                      stroke="#f59e0b" 
                      strokeWidth={selectedScenario === 'optimistic' ? 4 : 2} 
                      fillOpacity={0.5} 
                      fill="url(#colorOpt)" 
                      dot={false} 
                      connectNulls={true}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-indigo-500" />
                  <h2 className="text-lg font-bold text-slate-800">Tabla Detallada de Rentabilidad</h2>
                </div>
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest bg-slate-50 px-3 py-1 rounded-full">
                  Cifras en {viewMode === 'value' ? 'Pesos (COP)' : 'Rendimiento %'}
                </div>
              </div>
              <div className="overflow-x-auto max-h-[500px] overflow-y-auto custom-scrollbar">
                <table className="w-full text-left">
                  <thead className="sticky top-0 bg-white z-10">
                    <tr className="border-b border-slate-100 bg-slate-50">
                      <th className="py-3 px-4 font-bold text-slate-600 text-xs uppercase tracking-tighter">{timeGranularity === 'yearly' ? 'Año' : 'Período'}</th>
                      <th className={`py-3 px-4 font-bold text-xs uppercase tracking-tighter ${selectedScenario === 'pessimistic' ? 'text-indigo-600 bg-indigo-50' : 'text-slate-600'}`}>Pesimista</th>
                      <th className={`py-3 px-4 font-bold text-xs uppercase tracking-tighter ${selectedScenario === 'moderate' ? 'text-indigo-600 bg-indigo-50' : 'text-slate-600'}`}>Moderado</th>
                      <th className={`py-3 px-4 font-bold text-xs uppercase tracking-tighter ${selectedScenario === 'optimistic' ? 'text-indigo-600 bg-indigo-50' : 'text-slate-600'}`}>Optimista</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {(timeGranularity === 'yearly' ? projectionsAnnual : projectionsMonthly).map((p: any) => (
                      <tr key={p.year || p.date} className="hover:bg-indigo-50/30 transition-colors group">
                        <td className="py-4 px-4 font-bold text-slate-700 text-sm group-hover:text-indigo-600">{p.year || p.date}</td>
                        <td className={`py-4 px-4 text-xs font-semibold ${selectedScenario === 'pessimistic' ? 'bg-indigo-50/30 font-bold text-rose-700' : 'text-rose-600 italic'}`}>
                          {viewMode === 'value' ? formatCurrency(p.pessimistic) : formatPercentage(p.pessimistic / (INITIAL_INVESTMENT / (timeGranularity === 'yearly' ? 1 : 12)))}
                        </td>
                        <td className={`py-4 px-4 text-xs font-bold ${selectedScenario === 'moderate' ? 'bg-indigo-50/30 text-indigo-700 text-sm' : 'text-slate-600'}`}>
                          {viewMode === 'value' ? formatCurrency(p.moderate) : formatPercentage(p.moderate / (INITIAL_INVESTMENT / (timeGranularity === 'yearly' ? 1 : 12)))}
                        </td>
                        <td className={`py-4 px-4 text-xs font-extrabold ${selectedScenario === 'optimistic' ? 'bg-indigo-50/30 text-emerald-700' : 'text-emerald-600'}`}>
                          {viewMode === 'value' ? formatCurrency(p.optimistic) : formatPercentage(p.optimistic / (INITIAL_INVESTMENT / (timeGranularity === 'yearly' ? 1 : 12)))}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 mt-12 py-10">
        <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center gap-6 text-slate-400 text-xs font-medium">
          <p>© 2025 Dashboard Hotelero de Alto Rendimiento. Todos los derechos reservados.</p>
          <div className="flex gap-8">
            <span className="flex items-center gap-1.5 text-indigo-500 font-bold"><Activity className="w-4 h-4" /> Datos de Alta Precisión</span>
            <a href="#" className="hover:text-indigo-600 transition-colors uppercase tracking-widest">Documentación</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
