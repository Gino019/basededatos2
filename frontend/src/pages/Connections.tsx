import { useEffect, useState } from 'react';
import { getConnections, createConnection, deleteConnection } from '../services/api';
import type { Connection, ConnectionCreate } from '../types';
import type { ToastType } from '../hooks/useToast';

interface Props {
  addToast: (msg: string, type?: ToastType) => void;
}

const defaultForm: ConnectionCreate = {
  name: '', type: 'postgres', host: 'localhost',
  port: 5432, database: '', username: '', password: ''
};

export default function Connections({ addToast }: Props) {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<ConnectionCreate>(defaultForm);
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setLoading(true);
    try { setConnections(await getConnections()); }
    catch { addToast('Could not load connections', 'error'); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleTypeChange = (t: ConnectionCreate['type']) => {
    setForm(prev => ({ ...prev, type: t, port: t === 'postgres' ? 5432 : 27017 }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await createConnection(form);
      addToast('Connection created successfully', 'success');
      setShowModal(false);
      setForm(defaultForm);
      load();
    } catch (err: unknown) {
      addToast((err as Error).message ?? 'Failed to create connection', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!window.confirm(`Delete connection "${name}"?`)) return;
    try {
      await deleteConnection(id);
      addToast(`Connection "${name}" deleted`, 'success');
      load();
    } catch { addToast('Failed to delete connection', 'error'); }
  };

  return (
    <div className="page-content">
      <div className="card">
        <div className="card-header">
          <h2>Database Connections</h2>
          <button id="btn-add-connection" className="btn btn-primary" onClick={() => setShowModal(true)}>
            + Add Connection
          </button>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: 40 }}><div className="spinner" style={{ margin: '0 auto' }} /></div>
        ) : connections.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">⬡</div>
            <h3>No connections yet</h3>
            <p>Add your first PostgreSQL or MongoDB connection to get started.</p>
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>Add Connection</button>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Host</th>
                  <th>Database</th>
                  <th>Username</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {connections.map(c => (
                  <tr key={c.id}>
                    <td><span className="cell-primary">{c.name}</span></td>
                    <td>
                      <span className={`badge ${c.type === 'postgres' ? 'badge-info' : 'badge-success'}`}>
                        {c.type === 'postgres' ? 'PostgreSQL' : 'MongoDB'}
                      </span>
                    </td>
                    <td>{c.host}:{c.port}</td>
                    <td>{c.database}</td>
                    <td>{c.username}</td>
                    <td>
                      <button
                        className="btn btn-danger btn-icon"
                        onClick={() => handleDelete(c.id, c.name)}
                        title="Delete connection"
                        id={`btn-delete-conn-${c.id}`}
                      >✕</button>
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
              <h2>New Connection</h2>
              <button className="modal-close" id="btn-close-conn-modal" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-grid">
                <div className="form-group">
                  <label htmlFor="conn-name">Connection Name</label>
                  <input id="conn-name" required value={form.name}
                    onChange={e => setForm(p => ({ ...p, name: e.target.value }))}
                    placeholder="e.g. Production DB" />
                </div>
                <div className="form-group">
                  <label htmlFor="conn-type">Database Type</label>
                  <select id="conn-type" value={form.type}
                    onChange={e => handleTypeChange(e.target.value as ConnectionCreate['type'])}>
                    <option value="postgres">PostgreSQL</option>
                    <option value="mongodb">MongoDB</option>
                  </select>
                </div>
                <div className="form-grid form-grid-2">
                  <div className="form-group">
                    <label htmlFor="conn-host">Host</label>
                    <input id="conn-host" required value={form.host}
                      onChange={e => setForm(p => ({ ...p, host: e.target.value }))} />
                  </div>
                  <div className="form-group">
                    <label htmlFor="conn-port">Port</label>
                    <input id="conn-port" type="number" required value={form.port}
                      onChange={e => setForm(p => ({ ...p, port: Number(e.target.value) }))} />
                  </div>
                </div>
                <div className="form-group">
                  <label htmlFor="conn-database">Database Name</label>
                  <input id="conn-database" required value={form.database}
                    onChange={e => setForm(p => ({ ...p, database: e.target.value }))}
                    placeholder="mydb" />
                </div>
                <div className="form-grid form-grid-2">
                  <div className="form-group">
                    <label htmlFor="conn-user">Username</label>
                    <input id="conn-user" required value={form.username}
                      onChange={e => setForm(p => ({ ...p, username: e.target.value }))} />
                  </div>
                  <div className="form-group">
                    <label htmlFor="conn-pass">Password</label>
                    <input id="conn-pass" type="password" required value={form.password}
                      onChange={e => setForm(p => ({ ...p, password: e.target.value }))} />
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" id="btn-submit-connection" className="btn btn-primary" disabled={saving}>
                  {saving ? <><span className="spinner" />Saving…</> : 'Save Connection'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
