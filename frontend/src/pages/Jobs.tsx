import { useEffect, useState, useCallback } from 'react';
import { getJobs, createJob, runJob, getJob, getConnections, getRules } from '../services/api';
import type { MaskingJob, JobCreate, Connection, MaskingRule, JobStatus } from '../types';
import type { ToastType } from '../hooks/useToast';

interface Props { addToast: (msg: string, type?: ToastType) => void; }

const statusBadge: Record<JobStatus, string> = {
  pending:   'badge-pending',
  running:   'badge-warning',
  completed: 'badge-success',
  failed:    'badge-danger',
};

function formatDate(d: string | null) {
  if (!d) return '—';
  return new Date(d).toLocaleString();
}

export default function Jobs({ addToast }: Props) {
  const [jobs, setJobs] = useState<MaskingJob[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [rules, setRules] = useState<MaskingRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedConn, setSelectedConn] = useState('');
  const [selectedRules, setSelectedRules] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);
  const [running, setRunning] = useState<Set<string>>(new Set());

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [j, c, r] = await Promise.all([getJobs(), getConnections(), getRules()]);
      setJobs(j); setConnections(c); setRules(r);
    } catch { addToast('Could not load data', 'error'); }
    finally { setLoading(false); }
  }, [addToast]);

  useEffect(() => { load(); }, [load]);

  const getConnectionName = (id: string) =>
    connections.find(c => c.id === id)?.name ?? id.slice(0, 8) + '…';

  const toggleRule = (id: string) =>
    setSelectedRules(prev => prev.includes(id) ? prev.filter(r => r !== id) : [...prev, id]);

  const filteredRules = rules.filter(r => r.connection_id === selectedConn);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedConn)            { addToast('Select a connection', 'error'); return; }
    if (selectedRules.length < 1) { addToast('Select at least one rule', 'error'); return; }
    setSaving(true);
    try {
      await createJob({ connection_id: selectedConn, rule_ids: selectedRules } as JobCreate);
      addToast('Job created', 'success');
      setShowModal(false);
      setSelectedConn(''); setSelectedRules([]);
      load();
    } catch (err: unknown) {
      addToast((err as Error).message ?? 'Failed to create job', 'error');
    } finally { setSaving(false); }
  };

  const handleRun = async (job: MaskingJob) => {
    setRunning(prev => new Set(prev).add(job.id));
    try {
      await runJob(job.id);
      addToast('Job started in background', 'info');
      // Poll until status changes
      const poll = async () => {
        const updated = await getJob(job.id);
        setJobs(prev => prev.map(j => j.id === job.id ? updated : j));
        if (updated.status === 'running' || updated.status === 'pending') {
          setTimeout(poll, 2000);
        } else {
          setRunning(prev => { const s = new Set(prev); s.delete(job.id); return s; });
          if (updated.status === 'completed')
            addToast(`Job completed — ${updated.records_processed} records masked`, 'success');
          else if (updated.status === 'failed')
            addToast(`Job failed: ${updated.error_message}`, 'error');
        }
      };
      setTimeout(poll, 1500);
    } catch (err: unknown) {
      addToast((err as Error).message ?? 'Failed to run job', 'error');
      setRunning(prev => { const s = new Set(prev); s.delete(job.id); return s; });
    }
  };

  return (
    <div className="page-content">
      <div className="card">
        <div className="card-header">
          <h2>Masking Jobs</h2>
          <button id="btn-add-job" className="btn btn-primary" onClick={() => setShowModal(true)}>
            + New Job
          </button>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: 40 }}><div className="spinner" style={{ margin: '0 auto' }} /></div>
        ) : jobs.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">▶</div>
            <h3>No jobs yet</h3>
            <p>Create a job to apply masking rules to a database connection.</p>
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>Create Job</button>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Connection</th>
                  <th>Rules</th>
                  <th>Status</th>
                  <th>Records</th>
                  <th>Started</th>
                  <th>Completed</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {jobs.map(j => (
                  <tr key={j.id}>
                    <td><span className="cell-primary">{getConnectionName(j.connection_id)}</span></td>
                    <td>{j.rule_ids.length} rule{j.rule_ids.length !== 1 ? 's' : ''}</td>
                    <td>
                      <span className={`badge ${statusBadge[j.status]}`}>
                        {j.status}
                      </span>
                    </td>
                    <td>{j.records_processed.toLocaleString()}</td>
                    <td style={{ fontSize: 12 }}>{formatDate(j.started_at)}</td>
                    <td style={{ fontSize: 12 }}>{formatDate(j.completed_at)}</td>
                    <td>
                      {(j.status === 'pending' || j.status === 'failed') && (
                        <button
                          id={`btn-run-job-${j.id}`}
                          className="btn btn-success"
                          disabled={running.has(j.id)}
                          onClick={() => handleRun(j)}
                        >
                          {running.has(j.id) ? <><span className="spinner" /> Running…</> : '▶ Run'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Create Masking Job</h2>
              <button className="modal-close" id="btn-close-job-modal" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleCreate}>
              <div className="form-grid">
                <div className="form-group">
                  <label htmlFor="job-conn">Connection</label>
                  <select id="job-conn" value={selectedConn}
                    onChange={e => { setSelectedConn(e.target.value); setSelectedRules([]); }}>
                    <option value="">Select a connection…</option>
                    {connections.map(c => (
                      <option key={c.id} value={c.id}>{c.name} ({c.type})</option>
                    ))}
                  </select>
                </div>

                {selectedConn && (
                  <div className="form-group">
                    <label>Select Rules</label>
                    {filteredRules.length === 0 ? (
                      <p style={{ fontSize: 13, color: 'var(--text-muted)', padding: '8px 0' }}>
                        No rules for this connection. Create rules first.
                      </p>
                    ) : (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 200, overflowY: 'auto', padding: '4px 0' }}>
                        {filteredRules.map(r => (
                          <label key={r.id} style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer', fontSize: 14, color: 'var(--text-secondary)' }}>
                            <input
                              type="checkbox"
                              id={`check-rule-${r.id}`}
                              checked={selectedRules.includes(r.id)}
                              onChange={() => toggleRule(r.id)}
                              style={{ accentColor: 'var(--color-accent)', width: 16, height: 16 }}
                            />
                            <span>
                              <strong style={{ color: 'var(--text-primary)' }}>{r.name}</strong>
                              &nbsp;·&nbsp;{r.target_table}.{r.target_column}
                            </span>
                          </label>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" id="btn-submit-job" className="btn btn-primary" disabled={saving}>
                  {saving ? <><span className="spinner" />Creating…</> : 'Create Job'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
