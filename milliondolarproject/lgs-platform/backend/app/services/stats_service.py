from typing import Optional

class StatsService:
    @staticmethod
    def calculate_score(correct: int, total: int) -> float:
        if total == 0:
            return 0.0
        return (correct / total) * 100.0

    @staticmethod
    def record_attempt(stats_obj, score: Optional[float] = None):
        # Placeholder for recording an attempt against a Stats model instance
        stats_obj.attempts = getattr(stats_obj, 'attempts', 0) + 1
        if score is not None:
            stats_obj.score = score
        return stats_obj
