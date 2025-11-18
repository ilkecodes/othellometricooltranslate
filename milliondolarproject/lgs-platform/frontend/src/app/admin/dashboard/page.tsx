"use client";

import React, { useState, useEffect } from 'react';

interface Teacher {
  id: string;
  name: string;
  subject: string;
  class: string;
  performance: number;
  studentCount: number;
}

interface Student {
  id: string;
  name: string;
  class: string;
  teacher: string;
  performance: number;
  lastActivity: string;
  missingSkills: number;
}

interface PerformanceData {
  dailySolutions: number;
  weeklySolutions: number;
  averageSuccess: number;
  weakSubjects: string[];
  mostMissedSkills: string[];
}

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('teachers');
  
  // Pre-loaded static data for demo purposes
  const teachers: Teacher[] = [
    { id: '1', name: 'Ahmet Yılmaz', subject: 'Matematik', class: '8A', performance: 92, studentCount: 24 },
    { id: '2', name: 'Fatma Kaya', subject: 'Fen Bilimleri', class: '8B', performance: 89, studentCount: 26 },
    { id: '3', name: 'Mehmet Demir', subject: 'Türkçe', class: '8C', performance: 94, studentCount: 25 },
    { id: '4', name: 'Ayşe Özkan', subject: 'Matematik', class: '8D', performance: 87, studentCount: 23 }
  ];
  
  const students: Student[] = [
    { id: '1', name: 'Ali Veli', class: '8A', teacher: 'Ahmet Yılmaz', performance: 88, lastActivity: '2 saat önce', missingSkills: 3 },
    { id: '2', name: 'Zeynep Ak', class: '8B', teacher: 'Fatma Kaya', performance: 94, lastActivity: '1 saat önce', missingSkills: 1 },
    { id: '3', name: 'Burak Can', class: '8C', teacher: 'Mehmet Demir', performance: 76, lastActivity: '4 saat önce', missingSkills: 7 },
    { id: '4', name: 'Selin Yıldız', class: '8A', teacher: 'Ahmet Yılmaz', performance: 91, lastActivity: '30 dk önce', missingSkills: 2 }
  ];
  
  const performance: PerformanceData = {
    dailySolutions: 1247,
    weeklySolutions: 8341,
    averageSuccess: 83,
    weakSubjects: ['Geometri', 'Kimya', 'Dil Bilgisi'],
    mostMissedSkills: ['Üçgende Açılar', 'Asit-Baz Dengesi', 'Fiilimsiler']
  };
  
  const loading = false; // No loading needed for static data

  useEffect(() => {
    console.log('AdminDashboard mounted, data is pre-loaded');
    // Data is already pre-loaded in state, no need to fetch
  }, []);

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
    backgroundColor: isActive ? '#1e40af' : '#f8fafc',
    color: isActive ? 'white' : '#64748b',
    border: '1px solid #e2e8f0',
    borderBottom: isActive ? '1px solid #1e40af' : '1px solid #e2e8f0',
    cursor: 'pointer',
    borderRadius: '8px 8px 0 0',
    marginRight: '2px',
    fontWeight: isActive ? '600' : '400',
    transition: 'all 0.2s ease'
  });

  const statCardStyle = {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '1.5rem',
    textAlign: 'center' as const,
    border: '1px solid #e5e7eb',
    boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
  };

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
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚙️</div>
          <div style={{ fontSize: '1.2rem', color: '#64748b' }}>Veriler yükleniyor...</div>
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
              🏢 Admin Paneli
            </h1>
            <p style={{ margin: '0', color: '#64748b', fontSize: '1.1rem' }}>
              Platform yönetim merkezi
            </p>
          </div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <div style={{ textAlign: 'right', color: '#64748b', fontSize: '0.9rem' }}>
              Son güncelleme: {new Date().toLocaleTimeString('tr-TR')}
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

      {/* Performance Stats Overview */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
          <div style={statCardStyle}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem', color: '#059669' }}>{performance.dailySolutions}</div>
            <div style={{ fontWeight: '600', color: '#374151', marginBottom: '0.25rem' }}>Günlük Çözüm</div>
            <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>Son 24 saat</div>
          </div>
          <div style={statCardStyle}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem', color: '#0891b2' }}>{performance.weeklySolutions}</div>
            <div style={{ fontWeight: '600', color: '#374151', marginBottom: '0.25rem' }}>Haftalık Çözüm</div>
            <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>Son 7 gün</div>
          </div>
          <div style={statCardStyle}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem', color: '#7c3aed' }}>%{performance.averageSuccess}</div>
            <div style={{ fontWeight: '600', color: '#374151', marginBottom: '0.25rem' }}>Ortalama Başarı</div>
            <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>Platform geneli</div>
          </div>
          <div style={statCardStyle}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem', color: '#ea580c' }}>{teachers.length}</div>
            <div style={{ fontWeight: '600', color: '#374151', marginBottom: '0.25rem' }}>Aktif Öğretmen</div>
            <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>Tüm branşlar</div>
          </div>
        </div>

      {/* Tab Navigation */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', borderBottom: '2px solid #e2e8f0' }}>
          <button onClick={() => setActiveTab('teachers')} style={tabStyle(activeTab === 'teachers')}>
            👨‍🏫 Öğretmen Yönetimi
          </button>
          <button onClick={() => setActiveTab('students')} style={tabStyle(activeTab === 'students')}>
            👩‍🎓 Öğrenci Yönetimi
          </button>
          <button onClick={() => setActiveTab('analytics')} style={tabStyle(activeTab === 'analytics')}>
            📊 İlerleme & Performans
          </button>
          <button onClick={() => setActiveTab('exams')} style={tabStyle(activeTab === 'exams')}>
            📝 Sınav Yönetimi
          </button>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'teachers' && (
        <div style={cardStyle}>
          <h3 style={{ margin: '0 0 1.5rem 0', color: '#1e293b', fontSize: '1.5rem' }}>👨‍🏫 Öğretmen Yönetimi</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
            {teachers.map(teacher => (
              <div key={teacher.id} style={{
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                padding: '1rem',
                backgroundColor: '#fafafa'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <h4 style={{ margin: '0', color: '#374151' }}>{teacher.name}</h4>
                  <span style={{ 
                    backgroundColor: teacher.performance >= 90 ? '#dcfce7' : '#fef3c7', 
                    color: teacher.performance >= 90 ? '#166534' : '#92400e',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '4px',
                    fontSize: '0.8rem'
                  }}>
                    %{teacher.performance}
                  </span>
                </div>
                <div style={{ color: '#6b7280', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
                  📚 {teacher.subject} • {teacher.class}
                </div>
                <div style={{ color: '#6b7280', fontSize: '0.9rem' }}>
                  👥 {teacher.studentCount} öğrenci
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'students' && (
        <div style={cardStyle}>
          <h3 style={{ margin: '0 0 1.5rem 0', color: '#1e293b', fontSize: '1.5rem' }}>👩‍🎓 Öğrenci Yönetimi</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '1rem' }}>
            {students.map(student => (
              <div key={student.id} style={{
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                padding: '1rem',
                backgroundColor: '#fafafa'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <h4 style={{ margin: '0', color: '#374151' }}>{student.name}</h4>
                  <span style={{ 
                    backgroundColor: student.performance >= 85 ? '#dcfce7' : student.performance >= 70 ? '#fef3c7' : '#fecaca', 
                    color: student.performance >= 85 ? '#166534' : student.performance >= 70 ? '#92400e' : '#991b1b',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '4px',
                    fontSize: '0.8rem'
                  }}>
                    %{student.performance}
                  </span>
                </div>
                <div style={{ color: '#6b7280', fontSize: '0.9rem', marginBottom: '0.25rem' }}>
                  🏫 {student.class} • 👨‍🏫 {student.teacher}
                </div>
                <div style={{ color: '#6b7280', fontSize: '0.9rem', marginBottom: '0.25rem' }}>
                  ⏰ Son aktivite: {student.lastActivity}
                </div>
                <div style={{ color: '#dc2626', fontSize: '0.9rem' }}>
                  ⚠️ {student.missingSkills} eksik kazanım
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'analytics' && (
        <div>
          <div style={cardStyle}>
            <h3 style={{ margin: '0 0 1.5rem 0', color: '#1e293b', fontSize: '1.5rem' }}>📊 İlerleme & Performans Paneli</h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem' }}>
              <div style={{ border: '1px solid #e5e7eb', borderRadius: '8px', padding: '1rem' }}>
                <h4 style={{ margin: '0 0 1rem 0', color: '#374151' }}>📈 Çözüm İstatistikleri</h4>
                <div style={{ marginBottom: '0.75rem' }}>
                  <div style={{ color: '#6b7280', fontSize: '0.9rem' }}>Günlük ortalama</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '600', color: '#059669' }}>{performance.dailySolutions} soru</div>
                </div>
                <div>
                  <div style={{ color: '#6b7280', fontSize: '0.9rem' }}>Haftalık toplam</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '600', color: '#0891b2' }}>{performance.weeklySolutions} soru</div>
                </div>
              </div>

              <div style={{ border: '1px solid #e5e7eb', borderRadius: '8px', padding: '1rem' }}>
                <h4 style={{ margin: '0 0 1rem 0', color: '#374151' }}>⚠️ Zayıf Konular</h4>
                {performance.weakSubjects.map((subject, index) => (
                  <div key={index} style={{ 
                    backgroundColor: '#fef2f2', 
                    color: '#991b1b', 
                    padding: '0.5rem', 
                    borderRadius: '4px', 
                    marginBottom: '0.5rem',
                    fontSize: '0.9rem'
                  }}>
                    📍 {subject}
                  </div>
                ))}
              </div>

              <div style={{ border: '1px solid #e5e7eb', borderRadius: '8px', padding: '1rem' }}>
                <h4 style={{ margin: '0 0 1rem 0', color: '#374151' }}>🎯 En Çok Yanlış Yapılan</h4>
                {performance.mostMissedSkills.map((skill, index) => (
                  <div key={index} style={{ 
                    backgroundColor: '#fffbeb', 
                    color: '#92400e', 
                    padding: '0.5rem', 
                    borderRadius: '4px', 
                    marginBottom: '0.5rem',
                    fontSize: '0.9rem'
                  }}>
                    ❌ {skill}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'exams' && (
        <div style={cardStyle}>
          <h3 style={{ margin: '0 0 1.5rem 0', color: '#1e293b', fontSize: '1.5rem' }}>📝 Sınav Yönetimi</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
            <div style={{ border: '1px solid #e5e7eb', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🎯</div>
              <h4 style={{ margin: '0 0 0.5rem 0', color: '#374151' }}>Otomatik Sınav Oluştur</h4>
              <p style={{ margin: '0 0 1rem 0', color: '#6b7280', fontSize: '0.9rem' }}>Konu ve zorluk seviyesine göre</p>
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
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>👨‍🏫</div>
              <h4 style={{ margin: '0 0 0.5rem 0', color: '#374151' }}>Öğretmen Ataması</h4>
              <p style={{ margin: '0 0 1rem 0', color: '#6b7280', fontSize: '0.9rem' }}>Sınav sorumlusu belirleme</p>
              <button style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: '#059669',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: '500'
              }}>
                Atama Yap
              </button>
            </div>

            <div style={{ border: '1px solid #e5e7eb', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📊</div>
              <h4 style={{ margin: '0 0 0.5rem 0', color: '#374151' }}>Sonuç Analizi</h4>
              <p style={{ margin: '0 0 1rem 0', color: '#6b7280', fontSize: '0.9rem' }}>Detaylı performans raporu</p>
              <button style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: '#7c3aed',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: '500'
              }}>
                Raporları Gör
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
