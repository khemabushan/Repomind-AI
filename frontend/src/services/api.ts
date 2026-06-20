import axios from "axios";

const api = axios.create({ baseURL: "/api/v1", timeout: 30000 });

api.interceptors.response.use(
  r => r,
  err => {
    const msg = err.response?.data?.detail ?? err.message ?? "Unknown error";
    return Promise.reject(new Error(msg));
  }
);

export default api;

export const repoApi = {
  submit:      (url: string)                => api.post("/analyze", { url }),
  getJob:      (jobId: string)              => api.get(`/jobs/${jobId}`),
  getRepo:     (id: string)                 => api.get(`/repos/${id}`),
  listRepos:   ()                           => api.get("/repos"),
  deleteRepo:  (id: string)                 => api.delete(`/repos/${id}`),
  getAnalysis: (id: string)                 => api.get(`/repos/${id}/analysis`),
  getDocs:     (id: string)                 => api.get(`/repos/${id}/docs`),
  getDoc:      (id: string, type: string)   => api.get(`/repos/${id}/docs/${type}`),
  getComplexity: (id: string)               => api.get(`/repos/${id}/complexity`),
  getDiagrams: (id: string)                 => api.get(`/repos/${id}/diagrams`),
  getOnboarding: (id: string)               => api.get(`/repos/${id}/onboarding`),
};

export const chatApi = {
  createSession: (repoId: string) => api.post(`/repos/${repoId}/chat/sessions`),
  getHistory:    (sid: string)    => api.get(`/chat/sessions/${sid}/history`),
  sendMessage:   (sid: string, message: string) => api.post(`/chat/sessions/${sid}/message`, { message }),
};

export const compareApi = {
  start:  (url_a: string, url_b: string) => api.post("/compare", { url_a, url_b }),
  getResult: (id: string)                => api.get(`/compare/${id}`),
};
