"use client";

import { useEffect, useState } from "react";

interface BundleAnalytics {
  total_bundles: number;
  total_sessions: number;
  total_completions: number;
  average_score: number;
  bundle_usage: Record<string, any>;
}

export default function AdminExamBundles() {
  const [analytics, setAnalytics] = useState<BundleAnalytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    setToken(storedToken);

    if (storedToken) {
      loadAnalytics(storedToken);
    }
  }, []);

  const loadAnalytics = async (token: string) => {
    setLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/admin/analytics/bundles`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (res.ok) {
        const data = await res.json();
        setAnalytics(data);
      }
    } catch (err) {
      console.error("Failed to load analytics:", err);
    } finally {
      setLoading(false);
    }
  };

  const generateNewBundle = async () => {
    if (!token) return;
    
    setGenerating(true);
    setError(null);
    setSuccess(null);

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/admin/bundles/generate`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Generation failed");
      }

      await res.json();
      setSuccess("New exam bundle generated successfully!");
      
      // Refresh analytics
      loadAnalytics(token);
    } catch (err) {
      setError(`Generation failed: ${err instanceof Error ? err.message : "Unknown error"}`);
    } finally {
      setGenerating(false);
    }
  };

  if (!token) {
    return (
      <main style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem" }}>
        <h1>Admin - Sınav Paketleri</h1>
        <p>Bu sayfaya erişmek için admin olarak giriş yapın.</p>
      </main>
    );
  }

  return (
    <main style={{ maxWidth: "1000px", margin: "0 auto", padding: "2rem" }}>
      <div style={{ marginBottom: "2rem", borderBottom: "1px solid #ddd", paddingBottom: "1rem" }}>
              <h1>📚 Sınav Paketi Yönetimi</h1>
        <p style={{ color: "#666", margin: "0.5rem 0" }}>
          Karma orijinal ve AI soruları ile LGS sınav paketleri oluşturun ve yönetin
        </p>
      </div>

      {error && (
        <div style={{
          padding: "1rem",
          backgroundColor: "#f8d7da",
          color: "#721c24",
          border: "1px solid #f5c6cb",
          borderRadius: "4px",
          marginBottom: "1rem",
        }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {success && (
        <div style={{
          padding: "1rem",
          backgroundColor: "#d4edda",
          color: "#155724",
          border: "1px solid #c3e6cb",
          borderRadius: "4px",
          marginBottom: "1rem",
        }}>
          <strong>Success:</strong> {success}
        </div>
      )}

      {/* Bundle Generation */}
      <div style={{
        marginBottom: "2rem",
        padding: "1.5rem",
        backgroundColor: "#f8f9fa",
        borderRadius: "8px",
        border: "1px solid #dee2e6",
      }}>
        <h2>🚀 Yeni Paket Oluştur</h2>
        <p style={{ color: "#666", marginBottom: "1rem" }}>
          Mevcut konfigürasyon ile yeni LGS sınav paketi oluşturun:
        </p>
        
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
          gap: "1rem",
          marginBottom: "1rem",
          fontSize: "0.9rem",
        }}>
          <div><strong>📚 Sözel Bölüm (50 soru):</strong></div>
          <div>• Türkçe: 20 soru</div>
          <div>• Sosyal Bilgiler: 10 soru</div>
          <div>• Din Kültürü: 10 soru</div>
          <div>• İngilizce: 10 soru</div>
          <div><strong>🔢 Sayısal Bölüm (40 soru):</strong></div>
          <div>• Matematik: 20 soru</div>
          <div>• Fen Bilimleri: 20 soru</div>
        </div>

                <button
          onClick={generateNewBundle}
          disabled={generating}
          style={{
            padding: "1rem 2rem",
            backgroundColor: generating ? "#ccc" : "#007bff",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: generating ? "not-allowed" : "pointer",
            fontWeight: "bold",
            fontSize: "1rem",
          }}
        >
          {generating ? "Oluşturuluyor..." : "🎯 Yeni Sınav Paketi Oluştur"}
        </button>

        <div style={{ marginTop: "1rem", fontSize: "0.9rem", color: "#666" }}>
          <strong>Not:</strong> Oluşturma işlemi tamamlanması 2-3 dakika sürer.<br/>
          <strong>Gerçek LGS Formatı:</strong> Sözel Bölüm 50 soru (75dk), Sayısal Bölüm 40 soru (80dk)<br/>
          <strong>Puanlama:</strong> 3 yanlış = 1 doğruyu götürür. Toplam 90 soru karma orijinal + MILK.
        </div>
      </div>

      {/* Analytics */}
      <div style={{
        marginBottom: "2rem",
        padding: "1.5rem",
        backgroundColor: "#ffffff",
        borderRadius: "8px",
        border: "1px solid #dee2e6",
      }}>
        <h2>📊 Paket Analitiği</h2>
        
        {loading ? (
          <p>Analitik verileri yükleniyor...</p>
        ) : analytics ? (
          <div>
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: "1rem",
              marginBottom: "1.5rem",
            }}>
              <div style={{ padding: "1rem", backgroundColor: "#e3f2fd", borderRadius: "6px" }}>
                <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#1976d2" }}>
                  {analytics.total_bundles}
                </div>
                <div style={{ color: "#666" }}>Toplam Paket</div>
              </div>
              
              <div style={{ padding: "1rem", backgroundColor: "#f3e5f5", borderRadius: "6px" }}>
                <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#7b1fa2" }}>
                  {analytics.total_sessions}
                </div>
                <div style={{ color: "#666" }}>Sınav Oturumu</div>
              </div>
              
              <div style={{ padding: "1rem", backgroundColor: "#e8f5e8", borderRadius: "6px" }}>
                <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#388e3c" }}>
                  {analytics.total_completions}
                </div>
                <div style={{ color: "#666" }}>Tamamlanan</div>
              </div>
              
              <div style={{ padding: "1rem", backgroundColor: "#fff3e0", borderRadius: "6px" }}>
                <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#f57c00" }}>
                  {analytics.average_score}%
                </div>
                <div style={{ color: "#666" }}>Ort Puan</div>
              </div>
            </div>

            {/* Bundle Usage Details */}
            <div>
              <h3>Paket Kullanım Detayları</h3>
              {Object.keys(analytics.bundle_usage).length > 0 ? (
                <div style={{ overflowX: "auto" }}>
                  <table style={{ width: "100%", borderCollapse: "collapse" }}>
                    <thead>
                      <tr style={{ backgroundColor: "#f8f9fa" }}>
                        <th style={{ padding: "0.75rem", textAlign: "left", border: "1px solid #dee2e6" }}>Paket ID</th>
                        <th style={{ padding: "0.75rem", textAlign: "left", border: "1px solid #dee2e6" }}>Oturum</th>
                        <th style={{ padding: "0.75rem", textAlign: "left", border: "1px solid #dee2e6" }}>Tamamlanan</th>
                        <th style={{ padding: "0.75rem", textAlign: "left", border: "1px solid #dee2e6" }}>Ort Puan</th>
                        <th style={{ padding: "0.75rem", textAlign: "left", border: "1px solid #dee2e6" }}>Son Kullanım</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(analytics.bundle_usage).map(([bundleId, usage]) => (
                        <tr key={bundleId}>
                          <td style={{ padding: "0.75rem", border: "1px solid #dee2e6" }}>{bundleId}</td>
                          <td style={{ padding: "0.75rem", border: "1px solid #dee2e6" }}>{usage.sessions}</td>
                          <td style={{ padding: "0.75rem", border: "1px solid #dee2e6" }}>{usage.completions}</td>
                          <td style={{ padding: "0.75rem", border: "1px solid #dee2e6" }}>{usage.average_score}%</td>
                          <td style={{ padding: "0.75rem", border: "1px solid #dee2e6" }}>
                            {usage.last_used ? new Date(usage.last_used).toLocaleDateString() : "Hiçbir zaman"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p style={{ color: "#666" }}>Henüz paket kullanım verisi mevcut değil.</p>
              )}
            </div>
          </div>
        ) : (
          <p style={{ color: "#666" }}>Analitik veriler yüklenemiyor.</p>
        )}
      </div>

      {/* Quick Actions */}
      <div style={{
        padding: "1.5rem",
        backgroundColor: "#f8f9fa",
        borderRadius: "8px",
        border: "1px solid #dee2e6",
      }}>
        <h2>⚡ Hızlı İşlemler</h2>
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
          <button
            onClick={() => window.open("/exams/bundles", "_blank")}
            style={{
              padding: "0.75rem 1rem",
              backgroundColor: "#007bff",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            📝 Paketleri Önizle
          </button>
          
          <button
            onClick={() => loadAnalytics(token!)}
            disabled={loading}
            style={{
              padding: "0.75rem 1rem",
              backgroundColor: "#17a2b8",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            🔄 Analitiği Yenile
          </button>
        </div>
      </div>

      <div style={{ marginTop: "2rem", textAlign: "center" }}>
        <a href="/admin/dashboard" style={{ color: "#007bff", textDecoration: "none" }}>
          ← Admin Paneline Dön
        </a>
      </div>
    </main>
  );
}