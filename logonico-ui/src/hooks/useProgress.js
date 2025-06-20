// useProgress.js - Poll /api/progress for real-time pipeline progress
import { useEffect, useState } from 'react';
import apiService from '../services/apiService';

export default function useProgress(intervalMs = 2000) {
  const [progress, setProgress] = useState({ status: 'complete', success_rate: 100, completed: 0, total_tasks: 0 });

  useEffect(() => {
    let timer;

    const fetchProgress = async () => {
      try {
        const p = await apiService.getProgress();
        setProgress(p || {});
      } catch (err) {
        // eslint-disable-next-line no-console
        console.warn('Failed to fetch progress', err);
      }
    };

    // initial fetch
    fetchProgress();

    timer = setInterval(fetchProgress, intervalMs);
    return () => clearInterval(timer);
  }, [intervalMs]);

  return progress;
}
