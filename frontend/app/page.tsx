const capabilities = [
  { title: "Data analysis", description: "Explore CSV and Excel datasets with natural-language questions." },
  { title: "Document intelligence", description: "Retrieve evidence from PDFs with source citations." },
  { title: "Visual insights", description: "Generate charts and explain analytical results." },
];

export default function Home() {
  return (
    <main className="shell">
      <nav className="nav">
        <div className="brand"><span className="brand-mark">A</span> Analyst Agent</div>
        <span className="status"><i /> Phase 1 · Foundation</span>
      </nav>

      <section className="hero">
        <p className="eyebrow">AI-POWERED ANALYTICS WORKSPACE</p>
        <h1>Turn your data into<br /><span>clear decisions.</span></h1>
        <p className="intro">
          Upload datasets, ask questions in natural language, and get reproducible
          analysis with visualizations and document-grounded answers.
        </p>
        <div className="hero-actions">
          <a className="primary" href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer">Explore API <span>↗</span></a>
          <a className="secondary" href="#capabilities">Explore capabilities</a>
        </div>
      </section>

      <section className="grid" id="capabilities">
        {capabilities.map((item, index) => (
          <article className="feature" key={item.title}>
            <span className="number">0{index + 1}</span>
            <h2>{item.title}</h2>
            <p>{item.description}</p>
          </article>
        ))}
      </section>

      <footer>
        <span>AI Data Analyst Agent</span>
        <span>Built with Next.js · FastAPI · Gemini · Qdrant</span>
      </footer>
    </main>
  );
}
