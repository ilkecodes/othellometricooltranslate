"use client";

import React, { useState, useEffect } from 'react';

interface Student {
  id: string;
  name: string;
  class: string;
  performance: number;
  lastActivity: string;
  missingSkills: string[];
  strengths: string[];
}

interface ExamResult {
  studentId: string;
  studentName: string;
  examName: string;
  score: number;
  completedAt: string;
  weakAreas: string[];
}

interface Analytics {
  skillsByStudent: Record<string, number>;
  topicErrors: Record<string, number>;
  progressTrend: Array<{ week: string; accuracy: number }>;
}

export default function TeacherDashboard() {
  const [activeTab, setActiveTab] = useState('students');
  const [students, setStudents] = useState<Student[]>([]);
  const [examResults, setExamResults] = useState<ExamResult[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTeacherData();
  }, []);

  const fetchTeacherData = async () => {
    setLoading(true);
    try {
      // Mock data - replace with real API calls
      setStudents([
        {
          id: '1',
          name: 'Ali Veli',
          class: '8A',
          performance: 88,
          lastActivity: '2 saat önce',
          missingSkills: ['Üçgende Açılar', 'Denklem Çözme'],
          strengths: ['Cebir', 'Sayı Problemleri']
        },
        {
          id: '2',
          name: 'Zeynep Ak',
          class: '8A',
          performance: 94,
          lastActivity: '1 saat önce',
          missingSkills: ['Geometri Problemleri'],
          strengths: ['Matematik', 'Fen Bilimleri', 'Problem Çözme']
        },
        {
          id: '3',
          name: 'Burak Can',
          class: '8B',
          performance: 76,
          lastActivity: '4 saat önce',
          missingSkills: ['Asit-Baz Dengesi', 'Fiilimsiler', 'Geometri'],
          strengths: ['Okuma Anlama']
        },
        {
          id: '4',
          name: 'Selin Yıldız',
          class: '8A',
          performance: 91,
          lastActivity: '30 dk önce',
          missingSkills: ['Kimya Problemleri', 'Dil Bilgisi'],
          strengths: ['Matematik', 'Mantık']
        }
      ]);

      setExamResults([
        { studentId: '1', studentName: 'Ali Veli', examName: 'LGS Karma v2', score: 85, completedAt: '1 saat önce', weakAreas: ['Geometri'] },
        { studentId: '2', studentName: 'Zeynep Ak', examName: 'Matematik Özel', score: 96, completedAt: '2 saat önce', weakAreas: [] },
        { studentId: '3', studentName: 'Burak Can', examName: 'LGS Karma v2', score: 72, completedAt: '3 saat önce', weakAreas: ['Kimya', 'Türkçe'] }
      ]);

      setAnalytics({
        skillsByStudent: { 'Ali Veli': 85, 'Zeynep Ak': 94, 'Burak Can': 76, 'Selin Yıldız': 91 },
        topicErrors: { 'Üçgende Açılar': 45, 'Asit-Baz Dengesi': 38, 'Fiilimsiler': 32, 'Geometri': 29 },
        progressTrend: [
          { week: 'Bu Hafta', accuracy: 83 },
          { week: 'Geçen Hafta', accuracy: 80 },
          { week: '2 Hafta Önce', accuracy: 78 },
          { week: '3 Hafta Önce', accuracy: 75 }
        ]
      });
    } catch (error) {
      console.error('Teacher data fetch error:', error);
    }
    setLoading(false);
  };

  const cardStyle = {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '1.5rem',
    marginBottom: '1.5rem',
    boxShadow: '0 4px 6px rgba(0,0,0,0.07)',
    border: '1px solid #e5e7eb'
  };

  const tabStyle = (isActive: boolean) => ({
    padding: '0.75rem 1.5rem',
    backgroundColor: isActive ? '#059669' : '#f8fafc',
    color: isActive ? 'white' : '#64748b',
    border: '1px solid #e2e8f0',
    borderBottom: isActive ? '1px solid #059669' : '1px solid #e2e8f0',
    cursor: 'pointer',
    borderRadius: '8px 8px 0 0',
    marginRight: '2px',
    fontWeight: isActive ? '600' : '400',
    transition: 'all 0.2s ease'
  });

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        backgroundColor: '#f1f5f9' 
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>👨‍🏫</div>
          <div style={{ fontSize: '1.2rem', color: '#64748b' }}>Öğretmen paneli yükleniyor...</div>
        </div>
      </div>
    );
  }

  return (
    <main style={{ 
      backgroundColor: '#f1f5f9', 
      minHeight: '100vh',
      padding: '2rem'
    }}>
      {/* Header */}
      <div style={cardStyle}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ margin: '0 0 0.5rem 0', fontSize: '2.5rem', color: '#1e293b' }}>
              👨‍🏫 Öğretmen Paneli
            </h1>
            <p style={{ margin: '0', color: '#64748b', fontSize: '1.1rem' }}>
              Öğrenci takip ve analiz merkezi
            </p>
          </div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <div style={{ textAlign: 'right', color: '#64748b', fontSize: '0.9rem' }}>
              8A Sınıfı • {students.length} öğrenci
            </div>
            <button style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#dc2626',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '500'
            }}>
              🚪 Çıkış
            </button>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '1.5rem',
          textAlign: 'center' as const,
          border: '1px solid #e5e7eb',
          boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
        }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem', color: '#059669' }}>{students.length}</div>
          <div style={{ fontWeight: '600', color: '#374151', marginBottom: '0.25rem' }}>Öğrenci Sayısı</div>
          <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>Aktif takip</div>
        </div>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '1.5rem',
          textAlign: 'center' as const,
          border: '1px solid #e5e7eb',
          boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
        }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem', color: '#0891b2' }}>
            %{Math.round(students.reduce((acc, student) => acc + student.performance, 0) / students.length)}
          </div>
          <div style={{ fontWeight: '600', color: '#374151', marginBottom: '0.25rem' }}>Sınıf Ortalaması</div>
          <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>Genel başarı</div>
        </div>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '1.5rem',
          textAlign: 'center' as const,
          border: '1px solid #e5e7eb',
          boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
        }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem', color: '#ea580c' }}>
            {students.reduce((acc, student) => acc + student.missingSkills.length, 0)}
          </div>
          <div style={{ fontWeight: '600', color: '#374151', marginBottom: '0.25rem' }}>Eksik Kazanım</div>
          <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>Toplam</div>
        </div>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '1.5rem',
          textAlign: 'center' as const,
          border: '1px solid #e5e7eb',
          boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
        }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem', color: '#7c3aed' }}>{examResults.length}</div>
          <div style={{ fontWeight: '600', color: '#374151', marginBottom: '0.25rem' }}>Tamamlanan Sınav</div>
          <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>Bu hafta</div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', borderBottom: '2px solid #e2e8f0' }}>
          <button onClick={() => setActiveTab('students')} style={tabStyle(activeTab === 'students')}>
            👥 Öğrenci Listesi
          </button>
          <button onClick={() => setActiveTab('analytics')} style={tabStyle(activeTab === 'analytics')}>
            📊 Analiz Modülü
          </button>
          <button onClick={() => setActiveTab('exams')} style={tabStyle(activeTab === 'exams')}>
            📝 Sınav Gönderme
          </button>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'students' && (
        <div style={cardStyle}>
          <h3 style={{ margin: '0 0 1.5rem 0', color: '#1e293b', fontSize: '1.5rem' }}>👥 Öğrenci Listesi</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1rem' }}>
            {students.map(student => (
              <div key={student.id} style={{
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                padding: '1rem',
                backgroundColor: '#fafafa'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <div>
                    <h4 style={{ margin: '0 0 0.25rem 0', color: '#374151' }}>{student.name}</h4>
                    <div style={{ color: '#6b7280', fontSize: '0.9rem' }}>🏫 {student.class} • ⏰ {student.lastActivity}</div>
                  </div>
                  <span style={{ 
                    backgroundColor: student.performance >= 85 ? '#dcfce7' : student.performance >= 70 ? '#fef3c7' : '#fecaca', 
                    color: student.performance >= 85 ? '#166534' : student.performance >= 70 ? '#92400e' : '#991b1b',
                    padding: '0.5rem',
                    borderRadius: '6px',
                    fontSize: '1rem',
                    fontWeight: '600'
                  }}>
                    %{student.performance}
                  </span>
                </div>
                
                <div style={{ marginBottom: '1rem' }}>
                  <div style={{ fontSize: '0.9rem', fontWeight: '600', color: '#374151', marginBottom: '0.5rem' }}>
                    ✅ Güçlü Yönleri:
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                    {student.strengths.map((strength, index) => (
                      <span key={index} style={{
                        backgroundColor: '#dcfce7',
                        color: '#166534',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.8rem'
                      }}>
                        {strength}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.9rem', fontWeight: '600', color: '#374151', marginBottom: '0.5rem' }}>
                    ⚠️ Eksik Kazanımlar: ({student.missingSkills.length})
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                    {student.missingSkills.map((skill, index) => (
                      <span key={index} style={{
                        backgroundColor: '#fef2f2',
                        color: '#991b1b',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.8rem'
                      }}>
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'analytics' && analytics && (
        <div>
          <div style={cardStyle}>
            <h3 style={{ margin: '0 0 1.5rem 0', color: '#1e293b', fontSize: '1.5rem' }}>📊 Kazanım Analizi</h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '1.5rem' }}>
              <div style={{ border: '1px solid #e5e7eb', borderRadius: '8px', padding: '1rem' }}>
                <h4 style={{ margin: '0 0 1rem 0', color: '#374151' }}>📈 Öğrenci Performans Dağılımı</h4>
                {Object.entries(analytics.skillsByStudent).map(([student, score]) => (
                  <div key={student} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <span style={{ color: '#374151' }}>{student}</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div style={{
                        width: '100px',
                        height: '8px',
                        backgroundColor: '#f3f4f6',
                        borderRadius: '4px',
                        overflow: 'hidden'
                      }}>
                        <div style={{
                          width: `${score}%`,
                          height: '100%',
                          backgroundColor: score >= 85 ? '#10b981' : score >= 70 ? '#f59e0b' : '#ef4444'
                        }}></div>
                      </div>
                      <span style={{ fontSize: '0.9rem', fontWeight: '600', color: '#374151' }}>%{score}</span>
                    </div>
                  </div>
                ))}
              </div>

              <div style={{ border: '1px solid #e5e7eb', borderRadius: '8px', padding: '1rem' }}>
                <h4 style={{ margin: '0 0 1rem 0', color: '#374151' }}>🎯 En Çok Hata Yapılan Konular</h4>
                {Object.entries(analytics.topicErrors)
                  .sort(([,a], [,b]) => b - a)
                  .slice(0, 5)
                  .map(([topic, errorCount]) => (
                  <div key={topic} style={{ 
                    backgroundColor: '#fef2f2', 
                    color: '#991b1b', 
                    padding: '0.75rem', 
                    borderRadius: '6px', 
                    marginBottom: '0.5rem',
                    fontSize: '0.9rem',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <span>📍 {topic}</span>
                    <span style={{ fontWeight: '600' }}>{errorCount} hata</span>
                  </div>
                ))}
              </div>

              <div style={{ border: '1px solid #e5e7eb', borderRadius: '8px', padding: '1rem' }}>
                <h4 style={{ margin: '0 0 1rem 0', color: '#374151' }}>📊 Gelişim Trendi</h4>
                {analytics.progressTrend.map((data, index) => (
                  <div key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                    <span style={{ color: '#374151', fontSize: '0.9rem' }}>{data.week}</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div style={{
                        width: '80px',
                        height: '6px',
                        backgroundColor: '#f3f4f6',
                        borderRadius: '3px',
                        overflow: 'hidden'
                      }}>
                        <div style={{
                          width: `${data.accuracy}%`,
                          height: '100%',
                          backgroundColor: index === 0 ? '#10b981' : '#6b7280'
                        }}></div>
                      </div>
                      <span style={{ fontSize: '0.9rem', fontWeight: '600', color: '#374151' }}>%{data.accuracy}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'exams' && (
        <div>
          <div style={cardStyle}>
            <h3 style={{ margin: '0 0 1.5rem 0', color: '#1e293b', fontSize: '1.5rem' }}>📝 Sınav Gönderme Modülü</h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
              <div style={{ border: '1px solid #e5e7eb', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🎯</div>
                <h4 style={{ margin: '0 0 0.5rem 0', color: '#374151' }}>Konu Bazlı Sınav</h4>
                <p style={{ margin: '0 0 1rem 0', color: '#6b7280', fontSize: '0.9rem' }}>Belirli kazanımlar için</p>
                <button style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: '#1e40af',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: '500'
                }}>
                  Sınav Oluştur
                </button>
              </div>

              <div style={{ border: '1px solid #e5e7eb', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚡</div>
                <h4 style={{ margin: '0 0 0.5rem 0', color: '#374151' }}>Hızlı Değerlendirme</h4>
                <p style={{ margin: '0 0 1rem 0', color: '#6b7280', fontSize: '0.9rem' }}>10 soru • 15 dakika</p>
                <button style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: '#059669',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: '500'
                }}>
                  Hızlı Sınav
                </button>
              </div>

              <div style={{ border: '1px solid #e5e7eb', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>👥</div>
                <h4 style={{ margin: '0 0 0.5rem 0', color: '#374151' }}>Sınıf Geneli</h4>
                <p style={{ margin: '0 0 1rem 0', color: '#6b7280', fontSize: '0.9rem' }}>Tüm sınıfa gönder</p>
                <button style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: '#7c3aed',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: '500'
                }}>
                  Sınıfa Gönder
                </button>
              </div>
            </div>

            <div style={cardStyle}>
              <h4 style={{ margin: '0 0 1rem 0', color: '#374151' }}>📊 Son Sınav Sonuçları</h4>
              <div style={{ display: 'grid', gap: '0.5rem' }}>
                {examResults.map((result, index) => (
                  <div key={index} style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '0.75rem',
                    border: '1px solid #e5e7eb',
                    borderRadius: '6px',
                    backgroundColor: '#fafafa'
                  }}>
                    <div>
                      <div style={{ fontWeight: '600', color: '#374151' }}>{result.studentName}</div>
                      <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>{result.examName} • {result.completedAt}</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{
                        backgroundColor: result.score >= 85 ? '#dcfce7' : result.score >= 70 ? '#fef3c7' : '#fecaca',
                        color: result.score >= 85 ? '#166534' : result.score >= 70 ? '#92400e' : '#991b1b',
                        padding: '0.25rem 0.75rem',
                        borderRadius: '4px',
                        fontSize: '0.9rem',
                        fontWeight: '600',
                        marginBottom: '0.25rem'
                      }}>
                        %{result.score}
                      </div>
                      {result.weakAreas.length > 0 && (
                        <div style={{ fontSize: '0.8rem', color: '#dc2626' }}>
                          {result.weakAreas.join(', ')}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
