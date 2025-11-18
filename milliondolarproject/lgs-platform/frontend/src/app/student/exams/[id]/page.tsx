"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

interface Question {
  id: number;
  stemText: string;
  difficulty: string;
  options: Array<{
    id: number;
    optionLabel: string;
    text: string;
  }>;
}

interface ExamQuestion {
  examQuestionId: number;
  question: Question;
  options: Array<{
    id: number;
    optionLabel: string;
    text: string;
  }>;
}

export default function ExamPage() {
  const params = useParams();
  const examId = params.id as string;

  const [currentQuestion, setCurrentQuestion] = useState<ExamQuestion | null>(null);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [loading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeSpent, setTimeSpent] = useState(0);

  useEffect(() => {
    // Start timer
    const timer = setInterval(() => {
      setTimeSpent((t) => t + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const handleSubmitAnswer = async () => {
    if (selectedOption === null) {
      alert("Please select an answer");
      return;
    }

    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/student/exams/${examId}/answer`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            exam_question_id: currentQuestion?.examQuestionId,
            selected_option_id: selectedOption,
            time_spent_seconds: timeSpent,
          }),
        }
      );

      if (!res.ok) throw new Error("Failed to submit answer");

      const result = await res.json();
      if (result.exam_completed) {
        alert("Exam completed!");
        // Redirect to results
      } else if (result.next_question) {
        setCurrentQuestion(result.next_question);
        setSelectedOption(null);
        setTimeSpent(0);
      }
    } catch (err) {
      setError(`Error: ${err instanceof Error ? err.message : "Unknown error"}`);
    }
  };

  const handleFinishExam = async () => {
    if (!confirm("Are you sure you want to finish the exam?")) return;

    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/student/exams/${examId}/finish`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!res.ok) throw new Error("Failed to finish exam");

      alert("Exam submitted!");
      // Redirect to results
    } catch (err) {
      setError(`Error: ${err instanceof Error ? err.message : "Unknown error"}`);
    }
  };

  if (loading) return <div>Loading exam...</div>;
  if (error) return <div style={{ color: "red" }}>{error}</div>;
  if (!currentQuestion) return <div>No questions available</div>;

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <main style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem" }}>
      <h1>Exam</h1>
      <div style={{ marginBottom: "1rem", padding: "1rem", backgroundColor: "#f5f5f5" }}>
        <p>Time: {formatTime(timeSpent)}</p>
        <p>Question {currentQuestion.examQuestionId}</p>
        <p>Difficulty: {currentQuestion.question.difficulty}</p>
      </div>

      <section>
        <h2>{currentQuestion.question.stemText}</h2>
        {currentQuestion.options.map((option) => (
          <div key={option.id} style={{ marginBottom: "1rem" }}>
            <label>
              <input
                type="radio"
                name="answer"
                value={option.id}
                checked={selectedOption === option.id}
                onChange={() => setSelectedOption(option.id)}
              />
              <strong>{option.optionLabel}</strong>: {option.text}
            </label>
          </div>
        ))}
      </section>

      <section style={{ marginTop: "2rem" }}>
        <button onClick={handleSubmitAnswer}>Submit Answer</button>
        <button
          onClick={handleFinishExam}
          style={{
            marginLeft: "1rem",
            backgroundColor: "#ff6b6b",
            color: "white",
            padding: "0.5rem 1rem",
            border: "none",
            cursor: "pointer",
          }}
        >
          Finish Exam
        </button>
      </section>
    </main>
  );
}
