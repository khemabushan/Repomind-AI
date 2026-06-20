import { useState, useEffect, useRef } from "react";
import { repoApi } from "@/services/api";
import type { Job } from "@/types";

export function useJobPoller(jobId: string | null, onComplete?: () => void) {
  const [job, setJob] = useState<Job | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval>>();

  useEffect(() => {
    if (!jobId) return;
    const poll = async () => {
      try {
        const res = await repoApi.getJob(jobId);
        const j: Job = res.data;
        setJob(j);
        if (j.status === "complete" || j.status === "failed") {
          clearInterval(intervalRef.current);
          onComplete?.();
        }
      } catch (_) {}
    };
    poll();
    intervalRef.current = setInterval(poll, 2500);
    return () => clearInterval(intervalRef.current);
  }, [jobId]);

  return job;
}
