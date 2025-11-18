export default function Home() {
  return (
    <main style={{ maxWidth: "1200px", margin: "0 auto", padding: "2rem" }}>
      <h1>LGS Uyarlanabilir Platform</h1>
      <p>LGS sınav hazırlığı için uyarlanabilir öğrenme platformuna hoşgeldiniz.</p>

      <section style={{ marginTop: "2rem" }}>
        <h2>Hızlı Giriş</h2>
        <div style={{ background: "#f5f5f5", padding: "1rem", borderRadius: "4px", marginTop: "1rem" }}>
          <p><strong>Test Hesabı:</strong></p>
          <p>E-posta: <code>test@lgs.local</code></p>
          <p>Şifre: <code>herhangi bir şey</code> (test için herhangi bir şifre çalışır)</p>
          <p style={{ marginTop: "1rem" }}>
            <a href="/student/dashboard" style={{ 
              display: "inline-block",
              padding: "0.5rem 1rem",
              backgroundColor: "#007bff",
              color: "white",
              textDecoration: "none",
              borderRadius: "4px"
            }}>
              Öğrenci Paneline Git
            </a>
          </p>
        </div>
      </section>

      <section style={{ marginTop: "2rem" }}>
        <h2>Başlarken</h2>
        <ul>
          <li>
            <a href="/student/dashboard">Öğrenci Paneli</a> - İlerlemenizi ve sınavlarınızı görüntüleyin
          </li>
          <li>
            <a href="/teacher/dashboard">Öğretmen Paneli</a> - Sınıfları ve ödevleri yönetin
          </li>
          <li>
            <a href="/admin/dashboard">Admin Paneli</a> - Sistem yönetimi
          </li>
        </ul>
      </section>

      <section style={{ marginTop: "2rem" }}>
        <h2>Özellikler</h2>
        <ul>
          <li>Uyarlanabilir sınav sistemi</li>
          <li>Gerçek zamanlı ilerleme takibi</li>
          <li>Müfredat yapısı (dersler, üniteler, konular, öğrenme çıktıları)</li>
          <li>Öğrenci ve öğretmen panelleri</li>
          <li>Sistem yönetimi için admin araçları</li>
          <li>PDF'den yüklenmiş 108 Türkçe Sözel Bölüm sorusu</li>
        </ul>
      </section>
    </main>
  );
}
