"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface ExamBundle {
  id: string;
  title: string;
  description: string;
  version: string;
  total_questions: number;
  subjects: string[];
  distribution: Record<string, number>;
  source_stats: Record<string, number>;
  difficulty_stats: Record<string, number>;
  generated_date: string;
  available: boolean;
}

interface BundlesResponse {
  bundles: ExamBundle[];
}

export default function ExamBundlesPage() {
  const [bundles, setBundles] = useState<ExamBundle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    setToken(storedToken);

    if (!storedToken) {
      setError("Not authenticated. Please log in.");
      setLoading(false);
      return;
    }

    fetchBundles(storedToken);
  }, []);

  const fetchBundles = async (token: string) => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/exams/bundles`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data: BundlesResponse = await res.json();
      setBundles(data.bundles);
      setLoading(false);
    } catch (err) {
      setError(`Failed to load exam bundles: ${err instanceof Error ? err.message : "Unknown error"}`);
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <main style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem" }}>
        <h1>Exam Bundles Not Available</h1>
        <p>Please log in to access exam bundles.</p>
        <Link href="/auth/login">Login</Link>
      </main>
    );
  }

  if (loading) {
    return (
      <main style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem" }}>
        <h1>LGS Exam Bundles</h1>
        <p>Loading exam bundles...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem" }}>
        <h1>LGS Exam Bundles</h1>
        <div style={{ color: "red", marginBottom: "1rem" }}>Error: {error}</div>
        <Link href="/student/dashboard">← Back to Dashboard</Link>
      </main>
    );
  }

  return (
    <main style={{ 
      maxWidth: "1200px", 
      margin: "0 auto", 
      padding: "2rem",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      minHeight: "100vh"
    }}>
      <div style={{ 
        marginBottom: "3rem", 
        padding: "2rem",
        background: "rgba(255, 255, 255, 0.95)",
        borderRadius: "20px",
        boxShadow: "0 20px 40px rgba(0, 0, 0, 0.1)",
        textAlign: "center",
        backdropFilter: "blur(10px)"
      }}>
        <div style={{ 
          fontSize: "3rem", 
          marginBottom: "1rem",
          background: "linear-gradient(45deg, #667eea, #764ba2)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          fontWeight: "800"
        }}>
          🎯 LGS Sınav Paketleri
        </div>
        <p style={{ 
          color: "#555", 
          fontSize: "1.2rem",
          margin: "0",
          fontWeight: "300",
          letterSpacing: "0.5px"
        }}>
          Orijinal ve AI destekli sorulardan oluşan eksiksiz LGS deneme sınavları
        </p>
      </div>

      {bundles.length === 0 ? (
        <div style={{ textAlign: "center", padding: "3rem" }}>
          <h2>Sınav Paketi Bulunmuyor</h2>
          <p>Sınav paketleri hazırlanıyor. Lütfen daha sonra tekrar kontrol edin.</p>
        </div>
      ) : (
        <div style={{ display: "grid", gap: "2rem" }}>
          {bundles.map((bundle) => (
            <div
              key={bundle.id}
              style={{
                background: bundle.available 
                  ? "linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)"
                  : "linear-gradient(135deg, #f1f3f4 0%, #e8eaed 100%)",
                borderRadius: "24px",
                padding: "2.5rem",
                boxShadow: "0 16px 32px rgba(0, 0, 0, 0.1)",
                border: "1px solid rgba(255, 255, 255, 0.2)",
                transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                position: "relative",
                overflow: "hidden"
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = "translateY(-4px)";
                e.currentTarget.style.boxShadow = "0 24px 48px rgba(0, 0, 0, 0.15)";
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "0 16px 32px rgba(0, 0, 0, 0.1)";
              }}
            >
              {/* Header */}
              <div style={{ marginBottom: "2rem", position: "relative" }}>
                <div style={{ 
                  position: "absolute",
                  top: "-1rem",
                  right: "-1rem",
                  width: "100px",
                  height: "100px",
                  background: "linear-gradient(45deg, #667eea, #764ba2)",
                  borderRadius: "50%",
                  opacity: "0.1",
                  zIndex: "1"
                }} />
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                  <h2 style={{ 
                    margin: 0, 
                    background: "linear-gradient(45deg, #667eea, #764ba2)",
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                    fontSize: "1.8rem",
                    fontWeight: "700",
                    letterSpacing: "-0.5px"
                  }}>{bundle.title}</h2>
                  <div style={{ display: "flex", gap: "0.75rem", zIndex: "2" }}>
                    <span style={{ 
                      padding: "0.5rem 1rem", 
                      background: "linear-gradient(45deg, #28a745, #20c997)", 
                      color: "white", 
                      borderRadius: "20px", 
                      fontSize: "0.85rem",
                      fontWeight: "600",
                      boxShadow: "0 4px 12px rgba(40, 167, 69, 0.3)"
                    }}>
                      v{bundle.version}
                    </span>
                    {bundle.available && (
                      <span style={{ 
                        padding: "0.5rem 1rem", 
                        background: "linear-gradient(45deg, #17a2b8, #138496)", 
                        color: "white", 
                        borderRadius: "20px", 
                        fontSize: "0.85rem",
                        fontWeight: "600",
                        boxShadow: "0 4px 12px rgba(23, 162, 184, 0.3)",
                        animation: "pulse 2s infinite"
                      }}>
                        ✨ Aktif
                      </span>
                    )}
                  </div>
                </div>
                <p style={{ 
                  margin: 0, 
                  color: "#666", 
                  fontSize: "1rem",
                  lineHeight: "1.6",
                  fontWeight: "400"
                }}>{bundle.description}</p>
              </div>

              {/* LGS Bölümleri */}
              <div style={{ marginBottom: "2rem" }}>
                <h3 style={{
                  background: "linear-gradient(45deg, #667eea, #764ba2)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  fontSize: "1.3rem",
                  fontWeight: "700",
                  margin: "0 0 1rem 0",
                  letterSpacing: "-0.5px"
                }}>📚 LGS Bölümleri</h3>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem" }}>
                  {/* Sözel Bölüm */}
                  {(bundle.distribution["Türkçe"] || bundle.distribution["Sosyal Bilgiler"] || bundle.distribution["Din Kültürü ve Ahlak Bilgisi"]) && (
                    <div style={{
                      background: "linear-gradient(135deg, #667eea, #764ba2)",
                      borderRadius: "16px",
                      padding: "1.5rem",
                      color: "white",
                      boxShadow: "0 8px 24px rgba(102, 126, 234, 0.3)",
                      transition: "transform 0.2s ease"
                    }}
                    onMouseOver={(e) => e.currentTarget.style.transform = "translateY(-2px)"}
                    onMouseOut={(e) => e.currentTarget.style.transform = "translateY(0)"}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
                        <span style={{ fontSize: "1.3rem" }}>📚</span>
                        <h4 style={{ margin: "0", fontSize: "1.1rem", fontWeight: "700" }}>Sözel Bölüm</h4>
                      </div>
                      <div style={{ fontSize: "1.8rem", fontWeight: "800", marginBottom: "0.5rem" }}>
                        50 Soru
                      </div>
                      <div style={{ fontSize: "0.85rem", opacity: "0.9", lineHeight: "1.4" }}>
                        Türkçe, Sosyal, Din K., İngilizce<br/>
                        <strong>⏱️ 75 dakika (Sabah oturumu)</strong>
                      </div>
                    </div>
                  )}
                  
                  {/* Sayısal Bölüm */}
                  {(bundle.distribution["Matematik"] || bundle.distribution["Fen Bilimleri"]) && (
                    <div style={{
                      background: "linear-gradient(135deg, #f093fb, #f5576c)",
                      borderRadius: "16px",
                      padding: "1.5rem",
                      color: "white",
                      boxShadow: "0 8px 24px rgba(245, 87, 108, 0.3)",
                      transition: "transform 0.2s ease"
                    }}
                    onMouseOver={(e) => e.currentTarget.style.transform = "translateY(-2px)"}
                    onMouseOut={(e) => e.currentTarget.style.transform = "translateY(0)"}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
                        <span style={{ fontSize: "1.3rem" }}>🔢</span>
                        <h4 style={{ margin: "0", fontSize: "1.1rem", fontWeight: "700" }}>Sayısal Bölüm</h4>
                      </div>
                      <div style={{ fontSize: "1.8rem", fontWeight: "800", marginBottom: "0.5rem" }}>
                        40 Soru
                      </div>
                      <div style={{ fontSize: "0.85rem", opacity: "0.9", lineHeight: "1.4" }}>
                        Matematik, Fen Bilimleri<br/>
                        <strong>⏱️ 80 dakika (Öğlen oturumu)</strong>
                      </div>
                    </div>
                  )}
                  
                  {/* Yabancı Dil */}
                  {bundle.distribution["İngilizce"] && (
                    <div style={{
                      background: "linear-gradient(135deg, #4facfe, #00f2fe)",
                      borderRadius: "16px",
                      padding: "1.5rem",
                      color: "white",
                      boxShadow: "0 8px 24px rgba(79, 172, 254, 0.3)",
                      transition: "transform 0.2s ease"
                    }}
                    onMouseOver={(e) => e.currentTarget.style.transform = "translateY(-2px)"}
                    onMouseOut={(e) => e.currentTarget.style.transform = "translateY(0)"}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
                        <span style={{ fontSize: "1.3rem" }}>🌍</span>
                        <h4 style={{ margin: "0", fontSize: "1.1rem", fontWeight: "700" }}>Yabancı Dil</h4>
                      </div>
                      <div style={{ fontSize: "1.8rem", fontWeight: "800", marginBottom: "0.5rem" }}>
                        10 Soru
                      </div>
                      <div style={{ fontSize: "0.85rem", opacity: "0.9", lineHeight: "1.4" }}>
                        İngilizce (Sözel Bölüm dahil)<br/>
                        <strong>⏱️ Sözel oturumda</strong>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Stats Grid */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1.5rem", marginBottom: "2rem" }}>
                {/* Total Questions */}
                <div style={{ 
                  padding: "1.5rem", 
                  background: "linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)", 
                  borderRadius: "16px",
                  border: "1px solid rgba(33, 150, 243, 0.1)",
                  transition: "transform 0.2s ease"
                }}>
                  <div style={{ display: "flex", alignItems: "center", marginBottom: "0.75rem" }}>
                    <span style={{ fontSize: "1.5rem", marginRight: "0.5rem" }}>📊</span>
                    <h4 style={{ margin: 0, color: "#1976d2", fontWeight: "600", fontSize: "0.95rem" }}>Toplam Soru</h4>
                  </div>
                  <p style={{ 
                    margin: 0, 
                    fontSize: "2rem", 
                    fontWeight: "800",
                    color: "#1976d2",
                    letterSpacing: "-1px"
                  }}>{bundle.total_questions}</p>
                </div>

                {/* Subject Distribution */}
                <div style={{ padding: "1rem", backgroundColor: "#f8f9fa", borderRadius: "6px" }}>
                  <h4 style={{ margin: "0 0 0.5rem 0", color: "#28a745" }}>📚 Subject Distribution</h4>
                  <div style={{ fontSize: "0.9rem" }}>
                    {Object.entries(bundle.distribution).map(([subject, count]) => (
                      <div key={subject} style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.25rem" }}>
                        <span>{subject.replace("Kültürü ve Ahlak Bilgisi", "Kültürü")}:</span>
                        <strong>{count}</strong>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Source Mix */}
                <div style={{ padding: "1rem", backgroundColor: "#f8f9fa", borderRadius: "6px" }}>
                  <h4 style={{ margin: "0 0 0.5rem 0", color: "#dc3545" }}>🏷️ Question Sources</h4>
                  <div style={{ fontSize: "0.9rem" }}>
                    {Object.entries(bundle.source_stats).map(([source, count]) => {
                      const percentage = Math.round((count / bundle.total_questions) * 100);
                      return (
                        <div key={source} style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.25rem" }}>
                          <span>
                            {source === 'LGS' ? '📄 Original LGS' : '🥛 MILK AI'} :
                          </span>
                          <strong>{count} ({percentage}%)</strong>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Difficulty Distribution */}
                <div style={{ padding: "1rem", backgroundColor: "#f8f9fa", borderRadius: "6px" }}>
                  <h4 style={{ margin: "0 0 0.5rem 0", color: "#ffc107" }}>🎯 Difficulty Levels</h4>
                  <div style={{ fontSize: "0.9rem" }}>
                    {Object.entries(bundle.difficulty_stats).map(([difficulty, count]) => {
                      if (difficulty === 'Unknown') return null;
                      const percentage = Math.round((count / bundle.total_questions) * 100);
                      const emoji = difficulty === 'Kolay' ? '🟢' : difficulty === 'Orta' ? '🟡' : '🔴';
                      return (
                        <div key={difficulty} style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.25rem" }}>
                          <span>{emoji} {difficulty}:</span>
                          <strong>{count} ({percentage}%)</strong>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Action Button */}
              <div style={{ textAlign: "center", paddingTop: "2rem", marginTop: "2rem", borderTop: "1px solid rgba(0, 0, 0, 0.06)" }}>
                {bundle.available ? (
                  <Link
                    href={`/exams/bundle/${bundle.id}`}
                    style={{
                      display: "inline-block",
                      padding: "1.25rem 2.5rem",
                      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                      color: "white",
                      textDecoration: "none",
                      borderRadius: "50px",
                      fontWeight: "700",
                      fontSize: "1.1rem",
                      transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                      boxShadow: "0 8px 24px rgba(102, 126, 234, 0.3)",
                      letterSpacing: "0.5px",
                      textTransform: "uppercase"
                    }}
                    onMouseOver={(e) => {
                      e.currentTarget.style.transform = "translateY(-2px)";
                      e.currentTarget.style.boxShadow = "0 12px 32px rgba(102, 126, 234, 0.4)";
                    }}
                    onMouseOut={(e) => {
                      e.currentTarget.style.transform = "translateY(0)";
                      e.currentTarget.style.boxShadow = "0 8px 24px rgba(102, 126, 234, 0.3)";
                    }}
                  >
                    🚀 Sınavı Başlat
                  </Link>
                ) : (
                  <button
                    disabled
                    style={{
                      padding: "1.25rem 2.5rem",
                      background: "linear-gradient(135deg, #9e9e9e 0%, #757575 100%)",
                      color: "white",
                      border: "none",
                      borderRadius: "50px",
                      fontWeight: "700",
                      fontSize: "1.1rem",
                      cursor: "not-allowed",
                      opacity: "0.6",
                      letterSpacing: "0.5px",
                      textTransform: "uppercase"
                    }}
                  >
                    Yakında
                  </button>
                )}
              </div>
              
              <div style={{ marginTop: "1rem", textAlign: "center" }}>
                <small style={{ color: "#666" }}>
                  Oluşturulma Tarihi: {new Date(bundle.generated_date).toLocaleDateString('tr-TR')}
                </small>
              </div>
            </div>
          ))}
        </div>
      )}

      <div style={{ marginTop: "3rem", textAlign: "center" }}>
        <Link href="/student/dashboard" style={{ color: "#007bff", textDecoration: "none" }}>
          ← Panele Dön
        </Link>
      </div>
    </main>
  );
}