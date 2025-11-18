"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

interface QuestionOption {
  key: string;
  text: string;
}

interface BundleQuestion {
  id: string;
  question_number: number;
  stem: string;
  options: QuestionOption[];
  correct_answer: string;
  subject: string;
  difficulty_level: string;
  kazanim_code: string;
  stamp: string;
  source: string;
  confidence: number;
  explanation: string;
}

interface ExamState {
  currentQuestionIndex: number;
  answers: Record<string, string>; // questionId -> selectedAnswer
  startTime: number;
  completed: boolean;
  score: number;
  sessionId: string | null;
}

interface ExamSession {
  session_id: string;
  bundle_id: string;
  user_id: number;
  started_at: string;
  status: string;
  time_limit_minutes: number;
  instructions: string;
}

export default function BundleExamPage() {
  const params = useParams();
  const bundleId = params.id as string;

  const [questions, setQuestions] = useState<BundleQuestion[]>([]);
  const [session, setSession] = useState<ExamSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [examState, setExamState] = useState<ExamState>({
    currentQuestionIndex: 0,
    answers: {},
    startTime: Date.now(),
    completed: false,
    score: 0,
    sessionId: null,
  });

  useEffect(() => {
    const storedToken = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    setToken(storedToken);

    if (!storedToken) {
      setError("Not authenticated. Please log in.");
      setLoading(false);
      return;
    }

    startExamSession(storedToken);
  }, [bundleId]);

  const startExamSession = async (token: string) => {
    try {
      // Start exam session
      const sessionRes = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/exams/bundles/${bundleId}/sessions`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!sessionRes.ok) {
        throw new Error(`Failed to start session: ${sessionRes.status}`);
      }

      const sessionData: ExamSession = await sessionRes.json();
      setSession(sessionData);

      // Get bundle questions
      const questionsRes = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/exams/bundles/${bundleId}/questions?shuffle=true`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!questionsRes.ok) {
        throw new Error(`Failed to load questions: ${questionsRes.status}`);
      }

      const questionsData = await questionsRes.json();
      setQuestions(questionsData.questions);
      
      setExamState(prev => ({
        ...prev,
        sessionId: sessionData.session_id,
        startTime: Date.now()
      }));

      setLoading(false);
    } catch (err) {
      setError(`Failed to start exam: ${err instanceof Error ? err.message : "Unknown error"}`);
      setLoading(false);
    }
  };

  const submitAnswer = async (questionId: string, selectedAnswer: string) => {
    if (!session || !token) return;

    try {
      await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/exams/sessions/${session.session_id}/answers`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question_id: questionId,
            selected_answer: selectedAnswer,
            time_spent_seconds: Math.floor((Date.now() - examState.startTime) / 1000),
          }),
        }
      );
    } catch (err) {
      console.error("Failed to submit answer:", err);
    }
  };

  const handleSelectOption = (optionKey: string) => {
    const currentQuestion = questions[examState.currentQuestionIndex];
    
    setExamState((prev) => ({
      ...prev,
      answers: {
        ...prev.answers,
        [currentQuestion.id]: optionKey,
      },
    }));

    // Submit answer to backend
    submitAnswer(currentQuestion.id, optionKey);
  };

  const handleNext = () => {
    if (examState.currentQuestionIndex < questions.length - 1) {
      setExamState((prev) => ({
        ...prev,
        currentQuestionIndex: prev.currentQuestionIndex + 1,
      }));
    }
  };

  const handlePrevious = () => {
    if (examState.currentQuestionIndex > 0) {
      setExamState((prev) => ({
        ...prev,
        currentQuestionIndex: prev.currentQuestionIndex - 1,
      }));
    }
  };

  const handleSubmit = async () => {
    const answeredCount = Object.keys(examState.answers).length;
    if (!confirm(`You have answered ${answeredCount} out of ${questions.length} questions. Submit exam?`)) {
      return;
    }

    if (!session || !token) return;

    try {
      // Complete exam session
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/exams/sessions/${session.session_id}/complete`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!res.ok) {
        throw new Error("Failed to complete exam");
      }

      // Calculate local score for immediate feedback
      const correctAnswers = questions.filter(q => {
        const userAnswer = examState.answers[q.id];
        return userAnswer === q.correct_answer;
      }).length;

      const score = Math.round((correctAnswers / questions.length) * 100);

      setExamState((prev) => ({
        ...prev,
        completed: true,
        score,
      }));
    } catch (err) {
      setError(`Failed to submit exam: ${err instanceof Error ? err.message : "Unknown error"}`);
    }
  };

  if (!token) {
    return (
      <main style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem" }}>
        <h1>Exam Not Available</h1>
        <p>Please log in to take an exam.</p>
        <Link href="/auth/login">Login</Link>
      </main>
    );
  }

  if (loading) {
    return (
      <main style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem" }}>
        <h1>🎯 LGS Exam Bundle</h1>
        <div style={{ textAlign: "center", padding: "3rem" }}>
          <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>📚</div>
          <p>Starting your exam session...</p>
          <p style={{ color: "#666", fontSize: "0.9rem" }}>Loading questions and preparing exam environment</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem" }}>
        <h1>🎯 LGS Exam Bundle</h1>
        <div style={{ color: "red", marginBottom: "1rem", padding: "1rem", border: "1px solid #dc3545", borderRadius: "4px" }}>
          <strong>Error:</strong> {error}
        </div>
        <Link href="/exams/bundles">← Back to Exam Bundles</Link>
      </main>
    );
  }

  if (questions.length === 0) {
    return (
      <main style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem" }}>
        <h1>🎯 LGS Exam Bundle</h1>
        <p>No questions available in this bundle.</p>
        <Link href="/exams/bundles">← Back to Exam Bundles</Link>
      </main>
    );
  }

  // Exam completed view
  if (examState.completed) {
    const correctAnswers = questions.filter(q => {
      const userAnswer = examState.answers[q.id];
      return userAnswer === q.correct_answer;
    }).length;

    // Subject breakdown
    const subjectStats = questions.reduce((acc, q) => {
      const subject = q.subject;
      if (!acc[subject]) acc[subject] = { total: 0, correct: 0 };
      acc[subject].total++;
      if (examState.answers[q.id] === q.correct_answer) {
        acc[subject].correct++;
      }
      return acc;
    }, {} as Record<string, { total: number; correct: number }>);

    // Source breakdown
    const sourceStats = questions.reduce((acc, q) => {
      const source = q.stamp;
      if (!acc[source]) acc[source] = { total: 0, correct: 0 };
      acc[source].total++;
      if (examState.answers[q.id] === q.correct_answer) {
        acc[source].correct++;
      }
      return acc;
    }, {} as Record<string, { total: number; correct: number }>);

    return (
      <main style={{ 
        maxWidth: "900px", 
        margin: "0 auto", 
        padding: "2rem",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        minHeight: "100vh"
      }}>
        <div style={{
          background: "rgba(255, 255, 255, 0.95)",
          borderRadius: "24px",
          padding: "3rem",
          boxShadow: "0 24px 48px rgba(0, 0, 0, 0.15)",
          backdropFilter: "blur(10px)"
        }}>
          <div style={{ textAlign: "center", marginBottom: "3rem" }}>
            <div style={{ fontSize: "4rem", marginBottom: "1rem" }}>🎉</div>
            <h1 style={{
              background: "linear-gradient(45deg, #667eea, #764ba2)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              fontSize: "2.5rem",
              fontWeight: "800",
              margin: "0 0 1rem 0",
              letterSpacing: "-1px"
            }}>Sınav Tamamlandı!</h1>
            <div style={{
              fontSize: "4rem",
              background: "linear-gradient(45deg, #28a745, #20c997)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              fontWeight: "900",
              letterSpacing: "-2px"
            }}>
              {examState.score}%
            </div>
          </div>

          <div style={{ display: "grid", gap: "2rem", marginBottom: "3rem" }}>
            <div style={{
              background: "linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.8) 100%)",
              borderRadius: "16px",
              padding: "2rem",
              boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)",
              border: "1px solid rgba(255, 255, 255, 0.3)"
            }}>
              <h2 style={{
                background: "linear-gradient(45deg, #667eea, #764ba2)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                fontSize: "1.5rem",
                fontWeight: "700",
                margin: "0 0 1.5rem 0",
                display: "flex",
                alignItems: "center",
                gap: "0.5rem"
              }}>📊 Genel Sonuçlar</h2>
              <div style={{ 
                display: "grid", 
                gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", 
                gap: "1.5rem" 
              }}>
                <div style={{
                  background: "linear-gradient(135deg, #28a745, #20c997)",
                  color: "white",
                  padding: "1rem",
                  borderRadius: "12px",
                  textAlign: "center"
                }}>
                  <div style={{ fontSize: "0.9rem", opacity: "0.9", marginBottom: "0.25rem" }}>Puan</div>
                  <div style={{ fontSize: "1.5rem", fontWeight: "700" }}>{examState.score}%</div>
                </div>
                <div style={{
                  background: "linear-gradient(135deg, #17a2b8, #138496)",
                  color: "white",
                  padding: "1rem",
                  borderRadius: "12px",
                  textAlign: "center"
                }}>
                  <div style={{ fontSize: "0.9rem", opacity: "0.9", marginBottom: "0.25rem" }}>Doğru</div>
                  <div style={{ fontSize: "1.5rem", fontWeight: "700" }}>{correctAnswers}</div>
                </div>
                <div style={{
                  background: "linear-gradient(135deg, #dc3545, #c82333)",
                  color: "white",
                  padding: "1rem",
                  borderRadius: "12px",
                  textAlign: "center"
                }}>
                  <div style={{ fontSize: "0.9rem", opacity: "0.9", marginBottom: "0.25rem" }}>Yanlış</div>
                  <div style={{ fontSize: "1.5rem", fontWeight: "700" }}>{Object.keys(examState.answers).length - correctAnswers}</div>
                </div>
                <div style={{
                  background: "linear-gradient(135deg, #ffc107, #e0a800)",
                  color: "white",
                  padding: "1rem",
                  borderRadius: "12px",
                  textAlign: "center"
                }}>
                  <div style={{ fontSize: "0.9rem", opacity: "0.9", marginBottom: "0.25rem" }}>Toplam</div>
                  <div style={{ fontSize: "1.5rem", fontWeight: "700" }}>{questions.length}</div>
                </div>
              </div>
            </div>

            {/* Subject Breakdown */}
            <div style={{
              background: "linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.8) 100%)",
              borderRadius: "16px",
              padding: "2rem",
              boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)",
              border: "1px solid rgba(255, 255, 255, 0.3)"
            }}>
              <h3 style={{
                background: "linear-gradient(45deg, #667eea, #764ba2)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                fontSize: "1.5rem",
                fontWeight: "700",
                margin: "0 0 1.5rem 0",
                display: "flex",
                alignItems: "center",
                gap: "0.5rem"
              }}>📚 Ders Performansı</h3>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1rem" }}>
                {Object.entries(subjectStats).map(([subject, stats]) => {
                  const percentage = Math.round((stats.correct / stats.total) * 100);
                  return (
                    <div key={subject} style={{
                      background: "linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(248, 250, 252, 0.6) 100%)",
                      borderRadius: "12px",
                      padding: "1.25rem",
                      border: "1px solid rgba(255, 255, 255, 0.5)",
                      boxShadow: "0 4px 16px rgba(0, 0, 0, 0.1)",
                      transition: "transform 0.2s ease-in-out",
                      cursor: "default"
                    }}>
                      <div style={{ fontWeight: "700", marginBottom: "0.5rem", color: "#2d3748", fontSize: "1.1rem" }}>{subject}</div>
                      <div style={{ fontSize: "1rem", color: "#4a5568", fontWeight: "600" }}>
                        <span style={{ color: percentage >= 70 ? "#28a745" : percentage >= 50 ? "#ffc107" : "#dc3545" }}>
                          {stats.correct}/{stats.total} ({percentage}%)
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Source Performance */}
            <div style={{
              background: "linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.8) 100%)",
              borderRadius: "16px",
              padding: "2rem",
              boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)",
              border: "1px solid rgba(255, 255, 255, 0.3)"
            }}>
              <h3 style={{
                background: "linear-gradient(45deg, #667eea, #764ba2)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                fontSize: "1.5rem",
                fontWeight: "700",
                margin: "0 0 1.5rem 0",
                display: "flex",
                alignItems: "center",
                gap: "0.5rem"
              }}>🏷️ Soru Kaynağı Performansı</h3>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem" }}>
                {Object.entries(sourceStats).map(([source, stats]) => {
                  const percentage = Math.round((stats.correct / stats.total) * 100);
                  const emoji = source === 'LGS' ? '📄' : '🥛';
                  const label = source === 'LGS' ? 'Orijinal LGS' : 'MILK AI';
                  return (
                    <div key={source} style={{
                      background: "linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(248, 250, 252, 0.6) 100%)",
                      borderRadius: "12px",
                      padding: "1.25rem",
                      border: "1px solid rgba(255, 255, 255, 0.5)",
                      boxShadow: "0 4px 16px rgba(0, 0, 0, 0.1)",
                      transition: "transform 0.2s ease-in-out",
                      cursor: "default"
                    }}>
                      <div style={{ fontWeight: "700", marginBottom: "0.5rem", color: "#2d3748", fontSize: "1.1rem" }}>{emoji} {label}</div>
                      <div style={{ fontSize: "1rem", color: "#4a5568", fontWeight: "600" }}>
                        <span style={{ color: percentage >= 70 ? "#28a745" : percentage >= 50 ? "#ffc107" : "#dc3545" }}>
                          {stats.correct}/{stats.total} ({percentage}%)
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
        </div>

          <div style={{ textAlign: "center" }}>
            <Link
              href="/exams/bundles"
              style={{
                display: "inline-block",
                padding: "1rem 2rem",
                background: "linear-gradient(135deg, #667eea, #764ba2)",
                color: "white",
                textDecoration: "none",
                borderRadius: "12px",
                fontWeight: "700",
                marginRight: "1rem",
                boxShadow: "0 4px 16px rgba(102, 126, 234, 0.3)",
                border: "none",
                transition: "all 0.2s ease-in-out",
                fontSize: "1rem",
                letterSpacing: "0.5px"
              }}
            >
              🎯 Yeni Sınava Geç
            </Link>
            <Link
              href="/student/dashboard"
              style={{
                display: "inline-block",
                padding: "1rem 2rem",
                background: "linear-gradient(135deg, #6c757d, #495057)",
                color: "white",
                textDecoration: "none",
                borderRadius: "12px",
                fontWeight: "700",
                boxShadow: "0 4px 16px rgba(108, 117, 125, 0.3)",
                border: "none",
                transition: "all 0.2s ease-in-out",
                fontSize: "1rem",
                letterSpacing: "0.5px"
              }}
            >
              🏠 Panele Dön
            </Link>
          </div>
        </div>
      </main>
    );
  }

  // Exam taking interface
  const currentQuestion = questions[examState.currentQuestionIndex];
  const selectedAnswer = examState.answers[currentQuestion.id];
  const answeredCount = Object.keys(examState.answers).length;
  const elapsedMinutes = Math.floor((Date.now() - examState.startTime) / 1000 / 60);

  return (
    <main style={{ 
      maxWidth: "1000px", 
      margin: "0 auto", 
      padding: "2rem",
      background: "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
      minHeight: "100vh"
    }}>
      {/* Header */}
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "2rem",
        padding: "2rem",
        background: "rgba(255, 255, 255, 0.95)",
        borderRadius: "20px",
        boxShadow: "0 16px 32px rgba(0, 0, 0, 0.1)",
        backdropFilter: "blur(10px)",
      }}>
        <div>
          <h1 style={{ 
            margin: 0,
            background: "linear-gradient(45deg, #667eea, #764ba2)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            fontSize: "2.2rem",
            fontWeight: "800",
            letterSpacing: "-0.5px"
          }}>🎯 LGS Karma Deneme</h1>
          {session && (
            <p style={{ margin: "0.5rem 0", color: "#666", fontSize: "0.9rem" }}>
              {session.instructions}
            </p>
          )}
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: "0.9rem", color: "#666" }}>
            Soru {examState.currentQuestionIndex + 1} / {questions.length}
          </div>
          <div style={{ fontSize: "0.9rem", color: "#666" }}>
            Geçen Süre: {elapsedMinutes} dk
          </div>
          <div style={{ fontSize: "0.8rem", color: "#999", marginTop: "0.25rem" }}>
            {/* LGS Format Info */}
            📖 Sözel: 75dk (50 soru) | 🔢 Sayısal: 80dk (40 soru)
          </div>
          {/* Subject and Section Info */}
          {currentQuestion && (
            <div style={{ 
              marginTop: "0.5rem",
              padding: "0.5rem 1rem",
              borderRadius: "20px",
              fontSize: "0.85rem",
              fontWeight: "600",
              background: 
                currentQuestion.subject === "İngilizce" ? "linear-gradient(135deg, #4facfe, #00f2fe)" :
                (currentQuestion.subject === "Matematik" || currentQuestion.subject === "Fen Bilimleri") ? "linear-gradient(135deg, #f093fb, #f5576c)" :
                "linear-gradient(135deg, #667eea, #764ba2)",
              color: "white",
              boxShadow: "0 4px 12px rgba(0, 0, 0, 0.2)"
            }}>
              {currentQuestion.subject === "İngilizce" ? "🌍 Yabancı Dil" :
               (currentQuestion.subject === "Matematik" || currentQuestion.subject === "Fen Bilimleri") ? "🔢 Sayısal" :
               "📚 Sözel"} - {currentQuestion.subject}
            </div>
          )}
        </div>
      </div>

      {/* Progress */}
      <div style={{
        marginBottom: "2rem",
        padding: "1.5rem",
        background: "rgba(255, 255, 255, 0.9)",
        borderRadius: "16px",
        boxShadow: "0 8px 24px rgba(0, 0, 0, 0.08)",
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
          <span>İlerleme: {answeredCount} / {questions.length} cevaplanmış</span>
          <span>%{Math.round((answeredCount / questions.length) * 100)} tamamlandı</span>
        </div>
        <div style={{
          width: "100%",
          height: "10px",
          background: "linear-gradient(90deg, #e9ecef 0%, #f8f9fa 100%)",
          borderRadius: "20px",
          overflow: "hidden",
          boxShadow: "inset 0 2px 4px rgba(0, 0, 0, 0.1)"
        }}>
          <div style={{
            width: `${(answeredCount / questions.length) * 100}%`,
            height: "100%",
            background: "linear-gradient(90deg, #667eea 0%, #764ba2 100%)",
            transition: "width 0.3s ease",
            borderRadius: "20px",
            boxShadow: "0 2px 8px rgba(102, 126, 234, 0.3)"
          }} />
        </div>
      </div>

      {/* Quick Question Navigator by Sections */}
      <div style={{
        marginBottom: "2rem",
        padding: "1.5rem",
        background: "rgba(255, 255, 255, 0.95)",
        borderRadius: "16px",
        boxShadow: "0 8px 24px rgba(0, 0, 0, 0.08)",
      }}>
        <h3 style={{
          margin: "0 0 1rem 0",
          fontSize: "1rem",
          fontWeight: "600",
          color: "#333"
        }}>📝 Soru Navigasyonu</h3>
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
          {[
            { name: "📚 Sözel", subjects: ["Türkçe", "Sosyal Bilgiler", "Din Kültürü ve Ahlak Bilgisi"], color: "#667eea" },
            { name: "🔢 Sayısal", subjects: ["Matematik", "Fen Bilimleri"], color: "#f5576c" },
            { name: "🌍 İngilizce", subjects: ["İngilizce"], color: "#00f2fe" }
          ].map((section, sectionIndex) => {
            const sectionQuestions = questions
              .map((q, index) => ({ ...q, originalIndex: index }))
              .filter(q => section.subjects.includes(q.subject));
            
            return (
              <div key={sectionIndex} style={{
                background: `linear-gradient(135deg, ${section.color}15, ${section.color}25)`,
                borderRadius: "12px",
                padding: "1rem",
                border: `2px solid ${section.color}30`,
                minWidth: "200px"
              }}>
                <div style={{ 
                  fontSize: "0.9rem", 
                  fontWeight: "600", 
                  color: section.color,
                  marginBottom: "0.5rem" 
                }}>
                  {section.name} ({sectionQuestions.length})
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.25rem" }}>
                  {sectionQuestions.map((q) => {
                    const isAnswered = examState.answers[q.id] !== undefined;
                    const isCurrent = q.originalIndex === examState.currentQuestionIndex;
                    return (
                      <button
                        key={q.id}
                        onClick={() => setExamState(prev => ({ ...prev, currentQuestionIndex: q.originalIndex }))}
                        style={{
                          width: "24px",
                          height: "24px",
                          border: "none",
                          borderRadius: "4px",
                          fontSize: "0.7rem",
                          fontWeight: "600",
                          cursor: "pointer",
                          background: isCurrent ? section.color : isAnswered ? `${section.color}80` : "#f0f0f0",
                          color: isCurrent || isAnswered ? "white" : "#666",
                          transition: "all 0.2s ease"
                        }}
                        onMouseOver={(e) => {
                          if (!isCurrent) {
                            e.currentTarget.style.background = `${section.color}60`;
                            e.currentTarget.style.color = "white";
                          }
                        }}
                        onMouseOut={(e) => {
                          if (!isCurrent) {
                            e.currentTarget.style.background = isAnswered ? `${section.color}80` : "#f0f0f0";
                            e.currentTarget.style.color = isAnswered ? "white" : "#666";
                          }
                        }}
                      >
                        {q.originalIndex + 1}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Question */}
      <div style={{ marginBottom: "2rem" }}>
        <div style={{
          display: "flex",
          gap: "1rem",
          marginBottom: "1.5rem",
          fontSize: "0.9rem",
          flexWrap: "wrap"
        }}>
          <span style={{
            padding: "0.5rem 1rem",
            background: "linear-gradient(45deg, #e3f2fd, #bbdefb)",
            borderRadius: "20px",
            color: "#1976d2",
            fontWeight: "600"
          }}><strong>Subject:</strong> {currentQuestion.subject}</span>
          <span style={{
            padding: "0.5rem 1rem",
            background: "linear-gradient(45deg, #f3e5f5, #e1bee7)",
            borderRadius: "20px",
            color: "#7b1fa2",
            fontWeight: "600"
          }}><strong>Difficulty:</strong> {currentQuestion.difficulty_level}</span>
          <span style={{
            padding: "0.5rem 1rem",
            background: currentQuestion.stamp === 'LGS' 
              ? "linear-gradient(45deg, #e8f5e8, #c8e6c9)"
              : "linear-gradient(45deg, #fff3e0, #ffe0b2)",
            borderRadius: "20px",
            color: currentQuestion.stamp === 'LGS' ? "#388e3c" : "#f57c00",
            fontWeight: "600"
          }}><strong>Source:</strong> {currentQuestion.stamp === 'LGS' ? '📄 LGS' : '🥛 MILK'}</span>
          {currentQuestion.kazanim_code && (
            <span><strong>Kazanım:</strong> {currentQuestion.kazanim_code}</span>
          )}
        </div>
        
        <div style={{
          padding: "2rem",
          background: "rgba(255, 255, 255, 0.95)",
          borderRadius: "16px",
          marginBottom: "2rem",
          boxShadow: "0 8px 24px rgba(0, 0, 0, 0.08)",
          border: "1px solid rgba(255, 255, 255, 0.2)"
        }}>
          <h2 style={{ 
            margin: 0, 
            fontSize: "1.3rem", 
            lineHeight: "1.7",
            color: "#2c3e50",
            fontWeight: "600"
          }}>
            {currentQuestion.stem}
          </h2>
        </div>

        {/* Options */}
        <div>
          <h3 style={{ marginBottom: "1rem" }}>Choose your answer:</h3>
          {currentQuestion.options.map((option) => {
            const isSelected = selectedAnswer === option.key;
            
            return (
              <div
                key={option.key}
                onClick={() => handleSelectOption(option.key)}
                style={{
                  padding: "1.25rem",
                  marginBottom: "1rem",
                  border: `2px solid ${isSelected ? "#667eea" : "rgba(0, 0, 0, 0.08)"}`,
                  borderRadius: "12px",
                  cursor: "pointer",
                  background: isSelected 
                    ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                    : "rgba(255, 255, 255, 0.95)",
                  color: isSelected ? "white" : "#2c3e50",
                  transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                  boxShadow: isSelected 
                    ? "0 8px 24px rgba(102, 126, 234, 0.3)"
                    : "0 4px 12px rgba(0, 0, 0, 0.05)",
                  transform: isSelected ? "translateY(-2px)" : "translateY(0)"
                }}
                onMouseOver={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.boxShadow = "0 8px 20px rgba(0, 0, 0, 0.1)";
                    e.currentTarget.style.transform = "translateY(-2px)";
                  }
                }}
                onMouseOut={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.05)";
                    e.currentTarget.style.transform = "translateY(0)";
                  }
                }}
              >
                <div style={{ display: "flex", gap: "0.75rem", alignItems: "flex-start" }}>
                  <div style={{
                    width: "24px",
                    height: "24px",
                    borderRadius: "50%",
                    backgroundColor: isSelected ? "#007bff" : "#e9ecef",
                    color: isSelected ? "white" : "#666",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontWeight: "bold",
                    fontSize: "0.9rem",
                  }}>
                    {option.key}
                  </div>
                  <div style={{ flex: 1 }}>
                    {option.text}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Navigation */}
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        gap: "1rem",
        marginTop: "2rem",
      }}>
        <button
          onClick={handlePrevious}
          disabled={examState.currentQuestionIndex === 0}
          style={{
            padding: "0.75rem 1.5rem",
            backgroundColor: examState.currentQuestionIndex === 0 ? "#ccc" : "#6c757d",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: examState.currentQuestionIndex === 0 ? "not-allowed" : "pointer",
          }}
        >
          ← Previous
        </button>

        {examState.currentQuestionIndex === questions.length - 1 ? (
          <button
            onClick={handleSubmit}
            style={{
              padding: "0.75rem 1.5rem",
              backgroundColor: "#28a745",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              fontWeight: "bold",
            }}
          >
            Submit Exam
          </button>
        ) : (
          <button
            onClick={handleNext}
            style={{
              padding: "0.75rem 1.5rem",
              backgroundColor: "#007bff",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            Next →
          </button>
        )}
      </div>

      {/* Question Navigator */}
      <div style={{
        marginTop: "2rem",
        padding: "1rem",
        backgroundColor: "#f8f9fa",
        borderRadius: "6px",
      }}>
        <h4 style={{ marginBottom: "1rem" }}>Question Navigator:</h4>
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(40px, 1fr))",
          gap: "0.5rem",
        }}>
          {questions.map((q, idx) => {
            const isAnswered = examState.answers[q.id] !== undefined;
            const isCurrent = idx === examState.currentQuestionIndex;

            return (
              <button
                key={q.id}
                onClick={() =>
                  setExamState((prev) => ({
                    ...prev,
                    currentQuestionIndex: idx,
                  }))
                }
                style={{
                  padding: "0.5rem",
                  backgroundColor: isCurrent ? "#007bff" : isAnswered ? "#28a745" : "#f0f0f0",
                  color: isCurrent || isAnswered ? "white" : "black",
                  border: "1px solid #ddd",
                  borderRadius: "4px",
                  cursor: "pointer",
                  fontWeight: isCurrent ? "bold" : "normal",
                  fontSize: "0.9rem",
                }}
              >
                {idx + 1}
              </button>
            );
          })}
        </div>
      </div>
    </main>
  );
}