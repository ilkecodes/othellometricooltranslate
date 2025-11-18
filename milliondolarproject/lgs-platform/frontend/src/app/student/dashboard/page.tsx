"use client";

import { useEffect, useState } from "react";
import { enhancedApiClient } from "@/lib/api";

interface StudentDashboard {
  performance_summary: {
    overall_score: number;
    recent_questions_solved: number;
    recent_correct_ratio: number;
    current_streak: number;
    total_study_time: number;
  };
  subject_mastery: Record<string, number>;
  weak_topics: Array<{ 
    topicId: number; 
    topicName: string; 
    masteryScore: number;
    recommendations: string[];
  }>;
  recommendations: {
    study_suggestions: string[];
    video_recommendations: Array<{
      title: string;
      url: string;
      subject: string;
      duration: string;
    }>;
    practice_areas: string[];
  };
  adaptive_difficulty: {
    current_level: string;
    next_adjustment: string;
    performance_trend: string;
  };
  achievements: Array<{
    id: string;
    title: string;
    description: string;
    earned_date: string;
    icon: string;
  }>;
}

export default function StudentDashboard() {
  const [dashboard, setDashboard] = useState<StudentDashboard | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'performance' | 'recommendations' | 'achievements'>('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState("test@lgs.local");
  const [password, setPassword] = useState("anything");
  const [loggingIn, setLoggingIn] = useState(false);
  const [token, setToken] = useState<string | null>(null);

  const api = enhancedApiClient;

  useEffect(() => {
    const storedToken = localStorage.getItem("access_token");
    if (storedToken) {
      setToken(storedToken);
    }
  }, []);

  const fetchDashboard = async () => {
    // Skip token check for simplified backend
    try {
      setLoading(true);
      setError(null);
      const response = await api.getStudentDashboard();
      // Extract data from response if it's wrapped
      const data = response?.data ? response.data : response;
      setDashboard(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Load dashboard without token requirement for simplified backend
    fetchDashboard();
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoggingIn(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8002/api/v1/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Login error response:", errorText);
        throw new Error(`Login failed: ${response.status}`);
      }

      const data = await response.json();
      localStorage.setItem("access_token", data.access_token);
      setToken(data.access_token);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Login failed";
      setError(errorMsg);
    } finally {
      setLoggingIn(false);
    }
  };

  // Dashboard working - no auth required for simplified backend
  /*
  if (!token) {
    return (
      <main style={{ maxWidth: "400px", margin: "100px auto", padding: "2rem" }}>
        <h1>Öğrenci Girişi</h1>
        
        <form onSubmit={handleLogin} style={{ marginTop: "2rem" }}>
          <div style={{ marginBottom: "1rem" }}>
            <label style={{ display: "block", marginBottom: "0.5rem" }}>
              E-posta:
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "0.5rem",
                fontSize: "1rem",
                boxSizing: "border-box",
              }}
            />
          </div>

          <div style={{ marginBottom: "1rem" }}>
            <label style={{ display: "block", marginBottom: "0.5rem" }}>
              Şifre:
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "0.5rem",
                fontSize: "1rem",
                boxSizing: "border-box",
              }}
            />
          </div>

          {error && !token && (
            <div style={{ color: "red", marginBottom: "1rem" }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loggingIn}
            style={{
              width: "100%",
              padding: "0.75rem",
              fontSize: "1rem",
              backgroundColor: "#007bff",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: loggingIn ? "not-allowed" : "pointer",
              opacity: loggingIn ? 0.6 : 1,
            }}
          >
            {loggingIn ? "Giriş yapılıyor..." : "Giriş Yap"}
          </button>
        </form>

        <div style={{ marginTop: "2rem", fontSize: "0.9rem", color: "#666" }}>
          <p><a href="/">← Ana Sayfaya Dön</a></p>
        </div>
      </main>
    );
  }
  */

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⏳</div>
          <div>Öğrenci paneli yükleniyor...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <div style={{ color: 'red', fontSize: '1.2rem', marginBottom: '1rem' }}>❌ {error}</div>
        <button onClick={fetchDashboard} style={{
          padding: '0.5rem 1rem',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}>
          Tekrar Dene
        </button>
      </div>
    );
  }

  const tabStyle = (isActive: boolean) => ({
    padding: '0.75rem 1.5rem',
    backgroundColor: isActive ? '#007bff' : '#f8f9fa',
    color: isActive ? 'white' : '#495057',
    border: '1px solid #dee2e6',
    borderBottom: isActive ? '1px solid #007bff' : '1px solid #dee2e6',
    cursor: 'pointer',
    borderRadius: '8px 8px 0 0',
    marginRight: '2px'
  });

  const cardStyle = {
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '1.5rem',
    marginBottom: '1.5rem',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    border: '1px solid #dee2e6'
  };

  const statCardStyle = {
    ...cardStyle,
    textAlign: 'center' as const,
    padding: '2rem'
  };

  // Mock dashboard data if none exists
  const mockDashboard: StudentDashboard = {
    performance_summary: {
      overall_score: 75,
      recent_questions_solved: 45,
      recent_correct_ratio: 0.73,
      current_streak: 8,
      total_study_time: 1200
    },
    subject_mastery: {
      "Matematik": 0.82,
      "Fen Bilimleri": 0.71,
      "Türkçe": 0.89,
      "İngilizce": 0.65
    },
    weak_topics: [
      {
        topicId: 1,
        topicName: "Rasyonel Sayılar",
        masteryScore: 0.45,
        recommendations: ["Video izle", "Pratik yap"]
      }
    ],
    recommendations: {
      study_suggestions: ["Matematik odaklı çalış", "Günlük 30 dakika pratik yap"],
      video_recommendations: [
        {
          title: "Rasyonel Sayılar Temelleri",
          url: "#",
          subject: "Matematik",
          duration: "15 dakika"
        }
      ],
      practice_areas: ["Rasyonel sayılar", "Cebirsel ifadeler"]
    },
    adaptive_difficulty: {
      current_level: "Orta",
      next_adjustment: "Hafif artış",
      performance_trend: "Yükseliş"
    },
    achievements: [
      {
        id: "1",
        title: "İlk 100 Soru",
        description: "100 soruyu başarıyla tamamladın!",
        earned_date: "2025-11-15",
        icon: "🎯"
      }
    ]
  };

  const displayDashboard = dashboard || mockDashboard;

  if (token && displayDashboard) {
    return (
      <main style={{ 
        maxWidth: "1400px", 
        margin: "0 auto", 
        padding: "2rem", 
        backgroundColor: '#f8f9fa', 
        minHeight: '100vh' 
      }}>
        <div style={{ 
          backgroundColor: 'white', 
          padding: '2rem', 
          borderRadius: '12px', 
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)', 
          marginBottom: '2rem' 
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h1 style={{ margin: '0 0 0.5rem 0', fontSize: '2.5rem', color: '#333' }}>
                📚 Öğrenci Paneli
              </h1>
              <p style={{ margin: '0', color: '#666', fontSize: '1.1rem' }}>
                Kişiselleştirilmiş öğrenme deneyimim
              </p>
            </div>
            <button
              onClick={() => {
                localStorage.removeItem("access_token");
                setToken(null);
              }}
              style={{
                padding: "0.75rem 1.5rem",
                backgroundColor: "#dc3545",
                color: "white",
                border: "none",
                borderRadius: "8px",
                cursor: "pointer",
                fontSize: '1rem'
              }}
            >
              🚪 Çıkış Yap
            </button>
          </div>
        </div>

        {/* Primary Action - Prominent Exam Access Banner */}
        <div style={{ marginBottom: '3rem' }}>
          <div style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            borderRadius: '16px',
            padding: '2rem',
            color: 'white',
            boxShadow: '0 8px 32px rgba(102, 126, 234, 0.3)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            position: 'relative',
            overflow: 'hidden'
          }}>
            {/* Background decoration */}
            <div style={{
              position: 'absolute',
              top: '-50px',
              right: '-50px',
              width: '150px',
              height: '150px',
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              borderRadius: '50%',
              zIndex: 0
            }}></div>
            
            <div style={{ position: 'relative', zIndex: 1 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                    <span style={{ fontSize: '2.5rem' }}>⚡</span>
                    <div>
                      <h2 style={{ margin: '0', fontSize: '1.8rem', fontWeight: '700' }}>Hemen Sınav Çöz</h2>
                      <p style={{ margin: '0', opacity: 0.9, fontSize: '1rem' }}>Bugün için önerilen kişisel sınavın hazır!</p>
                    </div>
                  </div>
                  
                  <div style={{ 
                    backgroundColor: 'rgba(255, 255, 255, 0.15)', 
                    borderRadius: '8px', 
                    padding: '0.75rem 1rem',
                    marginBottom: '1.5rem',
                    border: '1px solid rgba(255, 255, 255, 0.2)'
                  }}>
                    <p style={{ margin: '0', fontSize: '0.95rem', opacity: 0.95 }}>
                      💡 Bu sınav, senin eksik kazanımlara göre oluşturuldu. Bugünkü hedefine ulaşmak için sadece 15 soru!
                    </p>
                  </div>
                </div>
              </div>
              
              <a 
                href="/exams/bundles"
                style={{
                  display: 'block',
                  width: '100%',
                  padding: '1rem 2rem',
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  color: '#4c1d95',
                  textDecoration: 'none',
                  borderRadius: '12px',
                  fontSize: '1.2rem',
                  fontWeight: '700',
                  textAlign: 'center' as const,
                  boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)',
                  border: '2px solid transparent',
                  transition: 'all 0.3s ease',
                  transform: 'translateY(0)'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.backgroundColor = 'white';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 6px 24px rgba(0, 0, 0, 0.15)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.1)';
                }}
              >
                🚀 SINAVA BAŞLA
              </a>
              
              <div style={{ 
                textAlign: 'center', 
                marginTop: '1rem', 
                opacity: 0.8, 
                fontSize: '0.9rem' 
              }}>
                ✨ Hazır olduğunda başla! Zamanın sınırsız.
              </div>
            </div>
          </div>
        </div>

        {/* Daily Goals Section */}
        <div style={{ marginBottom: '2rem' }}>
          <div style={cardStyle}>
            <h3 style={{ margin: '0 0 1.5rem 0', color: '#333', fontSize: '1.4rem' }}>🎯 Günlük Görevler</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
              <div style={{
                padding: '1rem',
                border: '2px solid #e8f5e8',
                borderRadius: '8px',
                backgroundColor: '#f8fff8'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <h4 style={{ margin: '0', color: '#2d5a2d', fontSize: '1rem' }}>📚 Matematik Çalışması</h4>
                  <span style={{ fontSize: '1.2rem' }}>✅</span>
                </div>
                <p style={{ margin: '0', color: '#666', fontSize: '0.9rem' }}>Bugünkü hedef: 10 soru çöz</p>
                <div style={{ 
                  width: '100%', 
                  height: '6px', 
                  backgroundColor: '#e2e8f0', 
                  borderRadius: '3px',
                  marginTop: '0.75rem',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    width: '100%',
                    height: '100%',
                    backgroundColor: '#10b981'
                  }}></div>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#059669', marginTop: '0.25rem', fontWeight: '500' }}>
                  12/10 soru tamamlandı!
                </div>
              </div>

              <div style={{
                padding: '1rem',
                border: '2px solid #fef3c7',
                borderRadius: '8px',
                backgroundColor: '#fffbeb'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <h4 style={{ margin: '0', color: '#92400e', fontSize: '1rem' }}>🧪 Fen Bilimleri</h4>
                  <span style={{ fontSize: '1.2rem' }}>🔄</span>
                </div>
                <p style={{ margin: '0', color: '#666', fontSize: '0.9rem' }}>Eksik konu: Asit-Baz Dengesi</p>
                <div style={{ 
                  width: '100%', 
                  height: '6px', 
                  backgroundColor: '#e2e8f0', 
                  borderRadius: '3px',
                  marginTop: '0.75rem',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    width: '60%',
                    height: '100%',
                    backgroundColor: '#f59e0b'
                  }}></div>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#92400e', marginTop: '0.25rem', fontWeight: '500' }}>
                  3/5 soru tamamlandı
                </div>
              </div>

              <div style={{
                padding: '1rem',
                border: '2px solid #fecaca',
                borderRadius: '8px',
                backgroundColor: '#fef2f2'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <h4 style={{ margin: '0', color: '#991b1b', fontSize: '1rem' }}>📖 Türkçe</h4>
                  <span style={{ fontSize: '1.2rem' }}>⏰</span>
                </div>
                <p style={{ margin: '0', color: '#666', fontSize: '0.9rem' }}>Öğretmen ataması: Fiilimsiler</p>
                <div style={{ 
                  width: '100%', 
                  height: '6px', 
                  backgroundColor: '#e2e8f0', 
                  borderRadius: '3px',
                  marginTop: '0.75rem',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    width: '0%',
                    height: '100%',
                    backgroundColor: '#ef4444'
                  }}></div>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#991b1b', marginTop: '0.25rem', fontWeight: '500' }}>
                  Başlamadın - Hadi başla!
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', borderBottom: '1px solid #dee2e6' }}>
            <button onClick={() => setActiveTab('overview')} style={tabStyle(activeTab === 'overview')}>
              📊 İlerleme Raporu
            </button>
            <button onClick={() => setActiveTab('performance')} style={tabStyle(activeTab === 'performance')}>
              📈 Performans Analizi
            </button>
            <button onClick={() => setActiveTab('recommendations')} style={tabStyle(activeTab === 'recommendations')}>
              💡 Kişisel Öneriler
            </button>
            <button onClick={() => setActiveTab('achievements')} style={tabStyle(activeTab === 'achievements')}>
              🏆 Başarı Rozetleri
            </button>
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div>
            {/* Performance Summary */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
              <div style={statCardStyle}>
                <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>📊</div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#007bff' }}>
                  {displayDashboard?.performance_summary?.overall_score || 0}%
                </div>
                <div style={{ color: '#666' }}>Genel Puan</div>
              </div>
              <div style={statCardStyle}>
                <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>✅</div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#28a745' }}>
                  {displayDashboard?.performance_summary?.recent_questions_solved || 0}
                </div>
                <div style={{ color: '#666' }}>Çözülen Soru</div>
              </div>
              <div style={statCardStyle}>
                <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>🎯</div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#17a2b8' }}>
                  {((displayDashboard?.performance_summary?.recent_correct_ratio || 0) * 100).toFixed(1)}%
                </div>
                <div style={{ color: '#666' }}>Doğruluk Oranı</div>
              </div>
              <div style={statCardStyle}>
                <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>🔥</div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ffc107' }}>
                  {displayDashboard?.performance_summary?.current_streak || 0}
                </div>
                <div style={{ color: '#666' }}>Seri Doğru</div>
              </div>
            </div>

            {/* Subject Mastery */}
            <div style={cardStyle}>
              <h2 style={{ marginTop: '0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                📚 Ders Hakimiyeti
              </h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                {Object.entries(displayDashboard?.subject_mastery || {}).map(([subject, mastery]) => (
                  <div key={subject} style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
                    <div style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>{subject}</div>
                    <div style={{ 
                      width: '100%', 
                      backgroundColor: '#e9ecef', 
                      borderRadius: '10px', 
                      height: '8px',
                      marginBottom: '0.5rem'
                    }}>
                      <div style={{
                        width: `${mastery * 100}%`,
                        backgroundColor: mastery > 0.8 ? '#28a745' : mastery > 0.6 ? '#ffc107' : '#dc3545',
                        height: '100%',
                        borderRadius: '10px'
                      }}></div>
                    </div>
                    <div style={{ fontSize: '0.9rem', color: '#666' }}>
                      {(mastery * 100).toFixed(0)}% tamamlandı
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Performance Tab */}
        {activeTab === 'performance' && (
          <div>
            <div style={cardStyle}>
              <h2 style={{ marginTop: '0' }}>📈 Detaylı Performans Analizi</h2>
              <div style={{ padding: '2rem', textAlign: 'center', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📊</div>
                <div>Detaylı performans analizi burada görüntülenecek</div>
              </div>
            </div>
          </div>
        )}

        {/* Recommendations Tab */}
        {activeTab === 'recommendations' && (
          <div>
            <div style={cardStyle}>
              <h2 style={{ marginTop: '0' }}>💡 Öneriler</h2>
              <div style={{ marginBottom: '2rem' }}>
                <h3>Çalışma Önerileri</h3>
                {displayDashboard?.recommendations?.study_suggestions?.map((suggestion, index) => (
                  <div key={index} style={{ 
                    padding: '1rem', 
                    backgroundColor: '#e7f3ff', 
                    borderRadius: '6px', 
                    marginBottom: '0.5rem',
                    borderLeft: '4px solid #007bff'
                  }}>
                    {suggestion}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Achievements Tab */}
        {activeTab === 'achievements' && (
          <div>
            <div style={cardStyle}>
              <h2 style={{ marginTop: '0' }}>🏆 Başarılarım</h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
                {displayDashboard?.achievements?.map((achievement) => (
                  <div key={achievement.id} style={{
                    padding: '1.5rem',
                    backgroundColor: '#fff3cd',
                    borderRadius: '8px',
                    textAlign: 'center',
                    border: '2px solid #ffc107'
                  }}>
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>{achievement.icon}</div>
                    <div style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>{achievement.title}</div>
                    <div style={{ color: '#666', marginBottom: '1rem' }}>{achievement.description}</div>
                    <div style={{ fontSize: '0.9rem', color: '#999' }}>
                      {new Date(achievement.earned_date).toLocaleDateString('tr-TR')}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    );
  }

  return null;
}
