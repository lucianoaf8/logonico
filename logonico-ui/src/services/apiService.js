const base = '/api';
export default {
  getImages:    ()=>fetch(`${base}/images`).then(r=>r.json()),
  getStats:     ()=>fetch(`${base}/stats`).then(r=>r.json()),
  getLogs:      ()=>fetch(`${base}/logs`).then(r=>r.json()),
};
