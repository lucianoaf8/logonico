const base = 'http://localhost:5000/api';

const apiService = {
  getImages:    ()=>fetch(`${base}/images`).then(r=>r.json()),
  getStats:     ()=>fetch(`${base}/stats`).then(r=>r.json()),
  getLogs:      ()=>fetch(`${base}/logs`).then(r=>r.json()),
};

export default apiService;