"use client";

import { useEffect, useState } from "react";

interface QuestionOption {
  id: number;
  text: string;
  is_correct: boolean;
}

interface Question {
  id: number;
  stem: string;
  options: QuestionOption[];
  topic_id: number;
  topic_name: string;
  subject_id: number;
  subject_name: string;
}

interface ExamState {
  currentQuestionIndex: number;
  answers: Record<number, number>; // questionId -> selectedOptionId
  startTime: number;
  completed: boolean;
  score: number;
}

export default function ExamPage() {
  const [token, setToken] = useState<string | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [examState, setExamState] = useState<ExamState>({
    currentQuestionIndex: 0,
    answers: {},
    startTime: Date.now(),
    completed: false,
    score: 0,
  });

  useEffect(() => {
    const storedToken = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    setToken(storedToken);

    if (!storedToken) {
      setError("Not authenticated. Please log in.");
      setLoading(false);
      return;
    }

    fetchQuestions(storedToken);
  }, []);

  const fetchQuestions = async (token: string) => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/questions/exam/full`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      console.log("Questions fetched:", data);
      setQuestions(data);
      setLoading(false);
    } catch (err) {
      setError(`Failed to load questions: ${err instanceof Error ? err.message : "Unknown error"}`);
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <main style={{ maxWidth: "600px", margin: "50px auto", padding: "2rem" }}>
        <h1>Exam Not Available</h1>
        <p>Please log in to take an exam.</p>
        <a href="/student/dashboard">← Back to Dashboard</a>
      </main>
    );
  }

  if (loading) {
    return (
      <main style={{ maxWidth: "600px", margin: "50px auto", padding: "2rem" }}>
        <p>Loading exam...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main style={{ maxWidth: "600px", margin: "50px auto", padding: "2rem" }}>
        <div style={{ color: "red" }}>Error: {error}</div>
        <a href="/student/dashboard">← Back to Dashboard</a>
      </main>
    );
  }

  if (questions.length === 0) {
    return (
      <main style={{ maxWidth: "600px", margin: "50px auto", padding: "2rem" }}>
        <h1>No Questions Available</h1>
        <p>There are currently no questions to display.</p>
        <a href="/student/dashboard">← Back to Dashboard</a>
      </main>
    );
  }

  if (examState.completed) {
    const correctAnswers = Object.entries(examState.answers).filter(([qId, optionId]) => {
      const question = questions.find((q) => q.id === Number(qId));
      const option = question?.options.find((o) => o.id === optionId);
      return option?.is_correct;
    }).length;

    const score = Math.round((correctAnswers / questions.length) * 100);

    return (
      <main style={{ maxWidth: "600px", margin: "50px auto", padding: "2rem" }}>
        <h1>Exam Completed!</h1>
        <div style={{ marginTop: "2rem", padding: "2rem", backgroundColor: "#f5f5f5", borderRadius: "8px" }}>
          <h2>Results</h2>
          <p>
            <strong>Score: {score}%</strong>
          </p>
          <p>
            Correct Answers: {correctAnswers} / {questions.length}
          </p>
          <p style={{ marginTop: "1rem", fontSize: "0.9rem", color: "#666" }}>
            Time taken: {Math.round((Date.now() - examState.startTime) / 1000)} seconds
          </p>
        </div>

        <div style={{ marginTop: "2rem" }}>
          <button
            onClick={() => {
              setExamState({
                currentQuestionIndex: 0,
                answers: {},
                startTime: Date.now(),
                completed: false,
                score: 0,
              });
            }}
            style={{
              padding: "0.75rem 1.5rem",
              backgroundColor: "#007bff",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              marginRight: "1rem",
            }}
          >
            Retake Exam
          </button>
          <a href="/student/dashboard">← Back to Dashboard</a>
        </div>
      </main>
    );
  }

  const currentQuestion = questions[examState.currentQuestionIndex];
  const selectedOptionId = examState.answers[currentQuestion.id];
  const answeredCount = Object.keys(examState.answers).length;

  const handleSelectOption = (optionId: number) => {
    setExamState((prev) => ({
      ...prev,
      answers: {
        ...prev.answers,
        [currentQuestion.id]: optionId,
      },
    }));
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

  const handleSubmit = () => {
    if (confirm(`You have answered ${answeredCount} out of ${questions.length} questions. Submit exam?`)) {
      setExamState((prev) => ({
        ...prev,
        completed: true,
      }));
    }
  };

  return (
    <main style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "2rem",
          borderBottom: "1px solid #ddd",
          paddingBottom: "1rem",
        }}
      >
        <h1>Turkish Reading Comprehension Exam (Sözel Bölüm)</h1>
        <div style={{ fontSize: "0.9rem", color: "#666" }}>
          Question {examState.currentQuestionIndex + 1} of {questions.length}
        </div>
      </div>

      {/* Question Counter */}
      <div
        style={{
          marginBottom: "2rem",
          padding: "1rem",
          backgroundColor: "#f0f0f0",
          borderRadius: "4px",
        }}
      >
        <div style={{ marginBottom: "0.5rem" }}>
          <strong>Progress:</strong> {answeredCount} / {questions.length} answered
        </div>
        <div
          style={{
            width: "100%",
            height: "20px",
            backgroundColor: "#ddd",
            borderRadius: "4px",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              width: `${(answeredCount / questions.length) * 100}%`,
              height: "100%",
              backgroundColor: "#28a745",
              transition: "width 0.3s ease",
            }}
          />
        </div>
      </div>

      {/* Question */}
      <div
        style={{
          marginBottom: "2rem",
          padding: "1.5rem",
          backgroundColor: "#fff",
          border: "1px solid #ddd",
          borderRadius: "8px",
        }}
      >
        <div style={{ marginBottom: "0.5rem", fontSize: "0.85rem", color: "#666" }}>
          <strong>Subject:</strong> {currentQuestion.subject_name} | <strong>Topic:</strong> {currentQuestion.topic_name}
        </div>
        <h2 style={{ marginTop: "1rem", fontSize: "1.2rem", lineHeight: "1.6" }}>
          {currentQuestion.stem}
        </h2>
      </div>

      {/* Options */}
      <div style={{ marginBottom: "2rem" }}>
        <h3>Choose your answer:</h3>
        {currentQuestion.options.map((option, idx) => {
          const isSelected = selectedOptionId === option.id;
          const labels = ["A", "B", "C", "D"];

          return (
            <div
              key={option.id}
              onClick={() => handleSelectOption(option.id)}
              style={{
                padding: "1rem",
                marginBottom: "0.75rem",
                border: `2px solid ${isSelected ? "#007bff" : "#ddd"}`,
                borderRadius: "4px",
                backgroundColor: isSelected ? "#e7f3ff" : "#f9f9f9",
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
            >
              <div style={{ display: "flex", alignItems: "start" }}>
                <div
                  style={{
                    width: "30px",
                    height: "30px",
                    borderRadius: "50%",
                    backgroundColor: isSelected ? "#007bff" : "#ddd",
                    color: "white",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    marginRight: "1rem",
                    fontWeight: "bold",
                    flexShrink: 0,
                  }}
                >
                  {labels[idx]}
                </div>
                <div style={{ flex: 1 }}>{option.text}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Navigation */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: "1rem",
          marginTop: "2rem",
        }}
      >
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

      {/* Quick navigation */}
      <div style={{ marginTop: "3rem", paddingTop: "2rem", borderTop: "1px solid #ddd" }}>
        <h3>Quick Navigation</h3>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(40px, 1fr))",
            gap: "0.5rem",
          }}
        >
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
                  transition: "all 0.2s ease",
                }}
              >
                {idx + 1}
              </button>
            );
          })}
        </div>
      </div>

      <div style={{ marginTop: "2rem" }}>
        <a href="/student/dashboard">← Back to Dashboard</a>
      </div>
    </main>
  );
}
