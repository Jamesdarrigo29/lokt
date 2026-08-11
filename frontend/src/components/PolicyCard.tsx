import { PolicyAttributes } from "../api/client";

function Badge({ label, value }: { label: string; value: boolean | null }) {
  const state = value === null ? "unknown" : value ? "warn" : "ok";
  const text = value === null ? "unknown" : value ? "yes" : "no";
  return (
    <span className={`badge badge-${state}`}>
      {label}: {text}
    </span>
  );
}

export default function PolicyCard({ policy }: { policy: PolicyAttributes }) {
  return (
    <article className="policy-card">
      <header>
        <h3>{policy.company}</h3>
        {policy.effective_date && <span className="muted">Effective {policy.effective_date}</span>}
      </header>

      {policy.summary && <p className="summary">{policy.summary}</p>}

      <div className="badges">
        <Badge label="Shares with 3rd parties" value={policy.shares_with_third_parties} />
        <Badge label="Sells data" value={policy.sells_data} />
        <Badge label="Cookies/tracking" value={policy.uses_cookies_tracking} />
        <Badge label="Children's data" value={policy.children_data_collected} />
      </div>

      {policy.risk_flags && policy.risk_flags.length > 0 && (
        <div className="risk-flags">
          <h4>Risk flags</h4>
          <ul>
            {policy.risk_flags.map((flag, i) => (
              <li key={i}>{flag}</li>
            ))}
          </ul>
        </div>
      )}

      {policy.user_rights && policy.user_rights.length > 0 && (
        <div className="rights">
          <h4>Your rights</h4>
          <ul>
            {policy.user_rights.map((right, i) => (
              <li key={i}>{right}</li>
            ))}
          </ul>
        </div>
      )}

      <footer className="muted small">source: {policy.source}</footer>
    </article>
  );
}
