import React, { useState, useEffect } from 'react';
import { Navbar } from './components/layout/Navbar';
import { Sidebar, TabType } from './components/layout/Sidebar';
import { Overview } from './pages/Overview';
import { ProjectExplorer } from './pages/ProjectExplorer';
import { ProjectDetail } from './pages/ProjectDetail';
import { RiskIntelligence } from './pages/RiskIntelligence';
import { EarlyWarnings } from './pages/EarlyWarnings';
import { Benchmarking } from './pages/Benchmarking';
import { AIAssistant } from './pages/AIAssistant';
import { DataManagement } from './pages/DataManagement';
import { ModelPerformance } from './pages/ModelPerformance';
import { fetchAlerts } from './services/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [alertCount, setAlertCount] = useState<number>(0);

  // Poll active alerts count
  const loadAlertCount = async () => {
    try {
      const res = await fetchAlerts({ status: 'NEW', limit: 1 });
      setAlertCount(res.total);
    } catch (e) {
      // ignore in offline mode
    }
  };

  useEffect(() => {
    loadAlertCount();
    const interval = setInterval(loadAlertCount, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectProject = (projectId: string) => {
    setSelectedProjectId(projectId);
  };

  const handleBackToProjects = () => {
    setSelectedProjectId(null);
  };

  const handleBenchmarkFromProject = (projectId: string) => {
    setSelectedProjectId(null);
    setActiveTab('benchmarking');
  };

  return (
    <div className="flex h-screen flex-col bg-[#0B132B] text-slate-100 overflow-hidden">
      {/* Top Header Bar */}
      <Navbar
        unreadAlertCount={alertCount}
        onAlertClick={() => {
          setSelectedProjectId(null);
          setActiveTab('alerts');
        }}
      />

      {/* Main Workspace: Sidebar + Content */}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          activeTab={activeTab}
          onTabChange={(tab) => {
            setActiveTab(tab);
            setSelectedProjectId(null);
          }}
          alertCount={alertCount}
        />

        {/* Content Viewport */}
        <main className="flex-1 overflow-y-auto p-6 bg-[#080E21]">
          {selectedProjectId ? (
            <ProjectDetail
              projectId={selectedProjectId}
              onBack={handleBackToProjects}
              onBenchmark={handleBenchmarkFromProject}
            />
          ) : (
            <>
              {activeTab === 'overview' && (
                <Overview
                  onSelectProject={handleSelectProject}
                  onNavigateToAlerts={() => setActiveTab('alerts')}
                  onNavigateToProjects={() => setActiveTab('projects')}
                />
              )}
              {activeTab === 'projects' && (
                <ProjectExplorer onSelectProject={handleSelectProject} />
              )}
              {activeTab === 'risk' && (
                <RiskIntelligence onSelectProject={handleSelectProject} />
              )}
              {activeTab === 'alerts' && (
                <EarlyWarnings onSelectProject={handleSelectProject} />
              )}
              {activeTab === 'benchmarking' && (
                <Benchmarking onSelectProject={handleSelectProject} />
              )}
              {activeTab === 'assistant' && (
                <AIAssistant onSelectProject={handleSelectProject} />
              )}
              {activeTab === 'data' && <DataManagement />}
              {activeTab === 'models' && <ModelPerformance />}
            </>
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
