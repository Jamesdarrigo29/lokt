import { useCallback, useEffect, useState } from "react";
import { fetchPolicies, PolicyAttributes } from "../api/client";
import PolicyCard from "../components/PolicyCard";
import UploadPanel from "../components/UploadPanel";

export default function Dashboard() {
  const [policies, setPolicies] = useState<PolicyAttributes[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    setLoading(true);
    fetchPolicies()
      .then(setPolicies)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="dashboard">
      <UploadPanel onIngested={load} />

      <section>
        <h2>Ingested policies ({policies.length})</h2>

        {loading && (
          <p className="muted loading-state">
            <span className="spinner" aria-hidden="true" />
            Loading… this may take a minute
          </p>
        )}

        {!loading && policies.length === 0 && (
          <p className="muted">No policies ingested yet. Upload a PDF or paste a URL above to get started.</p>
        )}

        <div className="policy-grid">
          {policies.map((policy) => (
            <PolicyCard key={policy.id} policy={policy} />
          ))}
        </div>
      </section>
    </div>
  );
}
