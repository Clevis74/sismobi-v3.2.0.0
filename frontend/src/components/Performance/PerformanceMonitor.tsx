/**
 * Performance Monitor - SISMOBI v3.2.0
 * Component para monitoramento de performance em tempo real
 */

import React, { useState, useEffect } from 'react';
import { Activity, Clock, Cpu, Zap, TrendingUp, AlertTriangle } from 'lucide-react';

interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  memoryUsage: number;
  scriptTime: number;
  largestContentfulPaint: number;
  firstContentfulPaint: number;
  cumulativeLayoutShift: number;
}

interface PerformanceMonitorProps {
  className?: string;
}

export const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({
  className = ''
}) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [isCollecting, setIsCollecting] = useState(false);

  const collectMetrics = () => {
    setIsCollecting(true);
    
    try {
      // Use Performance API
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const paint = performance.getEntriesByType('paint');
      
      // Memory usage (se disponível)
      const memoryInfo = (performance as any).memory;
      
      // Calculate metrics
      const loadTime = navigation.loadEventEnd - navigation.navigationStart;
      const renderTime = navigation.domContentLoadedEventEnd - navigation.navigationStart;
      
      const fcp = paint.find(entry => entry.name === 'first-contentful-paint')?.startTime || 0;
      const lcp = 0; // LCP precisa ser medido com PerformanceObserver
      
      setMetrics({
        loadTime: Math.round(loadTime),
        renderTime: Math.round(renderTime),
        memoryUsage: memoryInfo ? Math.round(memoryInfo.usedJSHeapSize / 1024 / 1024) : 0,
        scriptTime: Math.round(navigation.domInteractive - navigation.navigationStart),
        largestContentfulPaint: lcp,
        firstContentfulPaint: Math.round(fcp),
        cumulativeLayoutShift: 0 // CLS precisa ser medido com PerformanceObserver
      });
    } catch (error) {
      console.warn('Error collecting performance metrics:', error);
    }
    
    setIsCollecting(false);
  };

  const getMetricStatus = (metric: string, value: number): 'good' | 'needs-improvement' | 'poor' => {
    switch (metric) {
      case 'loadTime':
        if (value < 2000) return 'good';
        if (value < 4000) return 'needs-improvement';
        return 'poor';
      case 'fcp':
        if (value < 1800) return 'good';
        if (value < 3000) return 'needs-improvement';
        return 'poor';
      case 'lcp':
        if (value < 2500) return 'good';
        if (value < 4000) return 'needs-improvement';
        return 'poor';
      default:
        return 'good';
    }
  };

  const getStatusColor = (status: 'good' | 'needs-improvement' | 'poor'): string => {
    switch (status) {
      case 'good':
        return 'text-green-600';
      case 'needs-improvement':
        return 'text-yellow-600';
      case 'poor':
        return 'text-red-600';
    }
  };

  const getStatusIcon = (status: 'good' | 'needs-improvement' | 'poor') => {
    switch (status) {
      case 'good':
        return <TrendingUp className="w-4 h-4 text-green-600" />;
      case 'needs-improvement':
        return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
      case 'poor':
        return <AlertTriangle className="w-4 h-4 text-red-600" />;
    }
  };

  useEffect(() => {
    // Collect initial metrics
    collectMetrics();
    
    // Set up LCP observer
    if ('PerformanceObserver' in window) {
      try {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          
          if (lastEntry && lastEntry.entryType === 'largest-contentful-paint') {
            setMetrics(prev => prev ? {
              ...prev,
              largestContentfulPaint: Math.round(lastEntry.startTime)
            } : null);
          }
        });
        
        observer.observe({ entryTypes: ['largest-contentful-paint'] });
        
        return () => observer.disconnect();
      } catch (error) {
        console.warn('PerformanceObserver not supported:', error);
      }
    }
  }, []);

  if (!metrics) {
    return (
      <div className={`bg-white rounded-lg border border-gray-200 p-4 ${className}`}>
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Coletando métricas...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold flex items-center">
          <Activity className="w-5 h-5 mr-2 text-blue-600" />
          Monitor de Performance
        </h3>
        <button
          onClick={collectMetrics}
          disabled={isCollecting}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50"
        >
          {isCollecting ? 'Coletando...' : 'Atualizar'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Load Time */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center">
              <Clock className="w-4 h-4 mr-2 text-gray-600" />
              <span className="text-sm font-medium">Tempo de Carregamento</span>
            </div>
            {getStatusIcon(getMetricStatus('loadTime', metrics.loadTime))}
          </div>
          <div className={`text-2xl font-bold ${getStatusColor(getMetricStatus('loadTime', metrics.loadTime))}`}>
            {metrics.loadTime}ms
          </div>
        </div>

        {/* Render Time */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center">
              <Zap className="w-4 h-4 mr-2 text-gray-600" />
              <span className="text-sm font-medium">Tempo de Renderização</span>
            </div>
          </div>
          <div className="text-2xl font-bold text-blue-600">
            {metrics.renderTime}ms
          </div>
        </div>

        {/* Memory Usage */}
        {metrics.memoryUsage > 0 && (
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center">
                <Cpu className="w-4 h-4 mr-2 text-gray-600" />
                <span className="text-sm font-medium">Uso de Memória</span>
              </div>
            </div>
            <div className="text-2xl font-bold text-purple-600">
              {metrics.memoryUsage}MB
            </div>
          </div>
        )}

        {/* First Contentful Paint */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center">
              <span className="text-sm font-medium">First Contentful Paint</span>
            </div>
            {getStatusIcon(getMetricStatus('fcp', metrics.firstContentfulPaint))}
          </div>
          <div className={`text-2xl font-bold ${getStatusColor(getMetricStatus('fcp', metrics.firstContentfulPaint))}`}>
            {metrics.firstContentfulPaint}ms
          </div>
        </div>

        {/* Largest Contentful Paint */}
        {metrics.largestContentfulPaint > 0 && (
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center">
                <span className="text-sm font-medium">Largest Contentful Paint</span>
              </div>
              {getStatusIcon(getMetricStatus('lcp', metrics.largestContentfulPaint))}
            </div>
            <div className={`text-2xl font-bold ${getStatusColor(getMetricStatus('lcp', metrics.largestContentfulPaint))}`}>
              {metrics.largestContentfulPaint}ms
            </div>
          </div>
        )}

        {/* Script Time */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center">
              <span className="text-sm font-medium">Tempo de Script</span>
            </div>
          </div>
          <div className="text-2xl font-bold text-indigo-600">
            {metrics.scriptTime}ms
          </div>
        </div>
      </div>

      {/* Performance Tips */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="font-medium text-blue-900 mb-2">💡 Dicas de Performance</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Tempo de carregamento ideal: &lt; 2 segundos</li>
          <li>• First Contentful Paint ideal: &lt; 1.8 segundos</li>
          <li>• Largest Contentful Paint ideal: &lt; 2.5 segundos</li>
          <li>• Use lazy loading para componentes pesados</li>
        </ul>
      </div>
    </div>
  );
};