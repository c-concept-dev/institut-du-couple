#!/usr/bin/env node

/**
 * Generate Index HTML
 * 
 * Ce script lit megasearch.json et génère un index.html racine
 * avec recherche full-text, filtres et navigation interactive.
 * 
 * Usage: node generate-index-html.js
 */

const fs = require('fs');

const MEGASEARCH_FILE = './megasearch.json';
const OUTPUT_FILE = './index.html';

console.log('🚀 Génération de l\'index.html racine...\n');

// Charger megasearch.json
let megasearch;
try {
    const content = fs.readFileSync(MEGASEARCH_FILE, 'utf8');
    megasearch = JSON.parse(content);
    console.log(`✅ megasearch.json chargé`);
    console.log(`   📚 ${megasearch.meta.total_documents} documents`);
    console.log(`   📄 ${megasearch.meta.total_chunks} chunks\n`);
} catch (error) {
    console.error(`❌ Erreur: Impossible de lire ${MEGASEARCH_FILE}`);
    console.error(`   ${error.message}`);
    console.error('\n💡 Assurez-vous de générer megasearch.json d\'abord:');
    console.error('   node generate-megasearch.js\n');
    process.exit(1);
}

// Générer le HTML
const html = `<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Base de Connaissances - Institut du Couple</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --mer: #8FAFB1;
            --vert-sauge: #C8D0C3;
            --beige-sable: #D8CDBB;
            --sable: #E6D7C3;
            --blanc: #FFFFFF;
            --gris-texte: #333333;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Montserrat', 'Segoe UI', sans-serif;
            background: var(--blanc);
            color: var(--gris-texte);
            line-height: 1.6;
        }

        .header {
            background: linear-gradient(135deg, var(--mer) 0%, var(--vert-sauge) 100%);
            color: var(--blanc);
            padding: 40px 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        .header-content {
            max-width: 1200px;
            margin: 0 auto;
        }

        h1 {
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }

        .stats-bar {
            background: var(--sable);
            padding: 20px;
            border-bottom: 3px solid var(--vert-sauge);
        }

        .stats-content {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            text-align: center;
        }

        .stat-item {
            padding: 10px;
        }

        .stat-value {
            font-size: 2.5em;
            font-weight: 700;
            color: var(--mer);
        }

        .stat-label {
            font-size: 0.9em;
            color: var(--gris-texte);
            margin-top: 5px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        .search-section {
            background: var(--sable);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 40px;
            border-left: 5px solid var(--mer);
        }

        .search-box {
            position: relative;
            margin-bottom: 20px;
        }

        #searchInput {
            width: 100%;
            padding: 15px 50px 15px 20px;
            font-size: 18px;
            border: 2px solid var(--vert-sauge);
            border-radius: 10px;
            font-family: 'Montserrat', sans-serif;
            transition: border-color 0.3s;
        }

        #searchInput:focus {
            outline: none;
            border-color: var(--mer);
        }

        .search-icon {
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 24px;
            color: var(--mer);
        }

        .filters {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }

        .filter-group {
            flex: 1;
            min-width: 200px;
        }

        .filter-label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: var(--gris-texte);
        }

        select {
            width: 100%;
            padding: 10px;
            border: 2px solid var(--vert-sauge);
            border-radius: 8px;
            font-family: 'Montserrat', sans-serif;
            font-size: 14px;
            background: var(--blanc);
        }

        .results-info {
            text-align: center;
            padding: 20px;
            font-size: 1.1em;
            color: var(--gris-texte);
        }

        .documents-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }

        .document-card {
            background: var(--blanc);
            border: 2px solid var(--vert-sauge);
            border-radius: 12px;
            padding: 25px;
            transition: all 0.3s;
            cursor: pointer;
            border-left: 5px solid var(--mer);
        }

        .document-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }

        .doc-title {
            font-size: 1.3em;
            font-weight: 600;
            color: var(--mer);
            margin-bottom: 10px;
        }

        .doc-authors {
            font-size: 0.95em;
            color: #666;
            margin-bottom: 15px;
        }

        .doc-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 15px;
        }

        .tag {
            background: var(--vert-sauge);
            color: var(--gris-texte);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }

        .doc-stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid var(--vert-sauge);
        }

        .doc-stat {
            text-align: center;
            font-size: 0.85em;
        }

        .doc-stat-value {
            font-weight: 700;
            color: var(--mer);
            font-size: 1.2em;
        }

        .chunks-list {
            margin-top: 30px;
        }

        .chunk-card {
            background: var(--sable);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            border-left: 4px solid var(--mer);
            transition: all 0.3s;
        }

        .chunk-card:hover {
            transform: translateX(5px);
        }

        .chunk-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 10px;
        }

        .chunk-title {
            font-weight: 600;
            font-size: 1.1em;
            color: var(--gris-texte);
        }

        .chunk-type {
            background: var(--mer);
            color: var(--blanc);
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: 600;
        }

        .chunk-meta {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
        }

        .chunk-excerpt {
            font-size: 0.95em;
            color: var(--gris-texte);
            line-height: 1.6;
            margin-bottom: 10px;
        }

        .chunk-keywords {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
        }

        .keyword {
            background: var(--beige-sable);
            color: var(--gris-texte);
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
        }

        .pdf-link {
            display: inline-block;
            padding: 8px 15px;
            background: linear-gradient(135deg, var(--mer) 0%, var(--vert-sauge) 100%);
            color: var(--blanc);
            text-decoration: none;
            border-radius: 8px;
            font-size: 0.9em;
            font-weight: 600;
            margin-top: 10px;
            transition: transform 0.3s;
        }

        .pdf-link:hover {
            transform: scale(1.05);
        }

        .footer {
            text-align: center;
            padding: 40px 20px;
            background: var(--sable);
            border-top: 3px solid var(--vert-sauge);
            margin-top: 60px;
            font-size: 11px;
        }

        .no-results {
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }

        .no-results-icon {
            font-size: 4em;
            margin-bottom: 20px;
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 2em;
            }
            
            .documents-grid {
                grid-template-columns: 1fr;
            }
            
            .filters {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <h1>📚 Base de Connaissances</h1>
            <p class="subtitle">Institut du Couple - Ressources Thérapeutiques</p>
        </div>
    </div>

    <div class="stats-bar">
        <div class="stats-content">
            <div class="stat-item">
                <div class="stat-value">${megasearch.meta.total_documents}</div>
                <div class="stat-label">Documents</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${megasearch.meta.total_chapitres}</div>
                <div class="stat-label">Chapitres</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${megasearch.meta.total_chunks}</div>
                <div class="stat-label">Contenus</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${megasearch.meta.total_pages}</div>
                <div class="stat-label">Pages</div>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="search-section">
            <div class="search-box">
                <input 
                    type="text" 
                    id="searchInput" 
                    placeholder="Rechercher des concepts, exercices, auteurs..."
                    autocomplete="off"
                />
                <span class="search-icon">🔍</span>
            </div>

            <div class="filters">
                <div class="filter-group">
                    <label class="filter-label">Approche thérapeutique</label>
                    <select id="filterApproche">
                        <option value="">Toutes les approches</option>
                        ${Object.keys(megasearch.index_global.par_approche).map(app => 
                            `<option value="${app}">${app}</option>`
                        ).join('')}
                    </select>
                </div>

                <div class="filter-group">
                    <label class="filter-label">Type de contenu</label>
                    <select id="filterType">
                        <option value="">Tous les types</option>
                        <option value="concept">Concepts</option>
                        <option value="exercice">Exercices</option>
                        <option value="cas">Cas pratiques</option>
                        <option value="citation">Citations</option>
                        <option value="outil">Outils</option>
                    </select>
                </div>

                <div class="filter-group">
                    <label class="filter-label">Problématique</label>
                    <select id="filterProblematique">
                        <option value="">Toutes les problématiques</option>
                        ${Object.keys(megasearch.index_global.par_problematique).map(prob => 
                            `<option value="${prob}">${prob}</option>`
                        ).join('')}
                    </select>
                </div>
            </div>

            <div id="resultsInfo" class="results-info"></div>
        </div>

        <div id="documentsView" class="documents-grid"></div>
        <div id="chunksView" class="chunks-list"></div>
    </div>

    <div class="footer">
        Base de Connaissances © Marie-Christine Abatte Psychologue<br>
        Dernière mise à jour: ${new Date(megasearch.meta.last_update).toLocaleDateString('fr-FR')}
    </div>

    <script>
        // Données
        const megasearch = ${JSON.stringify(megasearch)};

        // État de l'interface
        let currentView = 'documents'; // 'documents' ou 'chunks'
        let filteredData = {
            documents: [...megasearch.documents],
            chunks: [...megasearch.chunks_complets]
        };

        // Elements DOM
        const searchInput = document.getElementById('searchInput');
        const filterApproche = document.getElementById('filterApproche');
        const filterType = document.getElementById('filterType');
        const filterProblematique = document.getElementById('filterProblematique');
        const resultsInfo = document.getElementById('resultsInfo');
        const documentsView = document.getElementById('documentsView');
        const chunksView = document.getElementById('chunksView');

        // Event listeners
        searchInput.addEventListener('input', debounce(handleSearch, 300));
        filterApproche.addEventListener('change', handleFilters);
        filterType.addEventListener('change', handleFilters);
        filterProblematique.addEventListener('change', handleFilters);

        // Initialisation
        displayDocuments();

        function debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }

        function handleSearch() {
            const query = searchInput.value.toLowerCase().trim();
            
            if (query.length === 0) {
                currentView = 'documents';
                filteredData.documents = [...megasearch.documents];
                displayDocuments();
            } else {
                currentView = 'chunks';
                filteredData.chunks = megasearch.chunks_complets.filter(chunk => {
                    return chunk.titre.toLowerCase().includes(query) ||
                           chunk.contenu_texte.toLowerCase().includes(query) ||
                           chunk.mots_cles.some(m => m.toLowerCase().includes(query)) ||
                           chunk.doc_titre.toLowerCase().includes(query);
                });
                applyFilters();
                displayChunks();
            }
        }

        function handleFilters() {
            applyFilters();
            if (currentView === 'documents') {
                displayDocuments();
            } else {
                displayChunks();
            }
        }

        function applyFilters() {
            const approche = filterApproche.value;
            const type = filterType.value;
            const problematique = filterProblematique.value;

            if (currentView === 'documents') {
                filteredData.documents = megasearch.documents.filter(doc => {
                    if (approche && !doc.approches.includes(approche)) return false;
                    return true;
                });
            } else {
                filteredData.chunks = filteredData.chunks.filter(chunk => {
                    if (approche && chunk.approche !== approche) return false;
                    if (type && chunk.type !== type) return false;
                    if (problematique && !chunk.problematiques.includes(problematique)) return false;
                    return true;
                });
            }
        }

        function displayDocuments() {
            documentsView.style.display = 'grid';
            chunksView.style.display = 'none';

            resultsInfo.textContent = \`\${filteredData.documents.length} document(s) trouvé(s)\`;

            if (filteredData.documents.length === 0) {
                documentsView.innerHTML = \`
                    <div class="no-results">
                        <div class="no-results-icon">📚</div>
                        <p>Aucun document trouvé</p>
                    </div>
                \`;
                return;
            }

            documentsView.innerHTML = filteredData.documents.map(doc => \`
                <div class="document-card" onclick="openDocument('\${doc.id}')">
                    <div class="doc-title">\${doc.titre}</div>
                    <div class="doc-authors">\${doc.auteurs.join(', ') || 'Auteur non spécifié'}</div>
                    <div class="doc-tags">
                        \${doc.approches.map(app => \`<span class="tag">\${app}</span>\`).join('')}
                        \${doc.langue ? \`<span class="tag">\${doc.langue.toUpperCase()}</span>\` : ''}
                    </div>
                    <div class="doc-stats">
                        <div class="doc-stat">
                            <div class="doc-stat-value">\${doc.stats.concepts}</div>
                            <div>Concepts</div>
                        </div>
                        <div class="doc-stat">
                            <div class="doc-stat-value">\${doc.stats.exercices}</div>
                            <div>Exercices</div>
                        </div>
                        <div class="doc-stat">
                            <div class="doc-stat-value">\${doc.stats.cas}</div>
                            <div>Cas</div>
                        </div>
                    </div>
                </div>
            \`).join('');
        }

        function displayChunks() {
            documentsView.style.display = 'none';
            chunksView.style.display = 'block';

            resultsInfo.textContent = \`\${filteredData.chunks.length} résultat(s) trouvé(s)\`;

            if (filteredData.chunks.length === 0) {
                chunksView.innerHTML = \`
                    <div class="no-results">
                        <div class="no-results-icon">🔍</div>
                        <p>Aucun résultat trouvé</p>
                    </div>
                \`;
                return;
            }

            chunksView.innerHTML = filteredData.chunks.map(chunk => \`
                <div class="chunk-card">
                    <div class="chunk-header">
                        <div class="chunk-title">\${chunk.titre}</div>
                        <span class="chunk-type">\${chunk.type}</span>
                    </div>
                    <div class="chunk-meta">
                        📚 \${chunk.doc_titre} • 📖 \${chunk.chapitre_titre} • 📄 Page \${chunk.pages[0]}
                    </div>
                    <div class="chunk-excerpt">
                        \${chunk.contenu_texte.substring(0, 200)}...
                    </div>
                    \${chunk.mots_cles.length > 0 ? \`
                        <div class="chunk-keywords">
                            \${chunk.mots_cles.map(kw => \`<span class="keyword">\${kw}</span>\`).join('')}
                        </div>
                    \` : ''}
                    <a href="\${chunk.pdf_direct_link}" class="pdf-link" target="_blank">
                        📄 Voir dans le PDF (page \${chunk.pages[0]})
                    </a>
                </div>
            \`).join('');
        }

        function openDocument(docId) {
            const doc = megasearch.documents.find(d => d.id === docId);
            if (doc) {
                window.location.href = \`\${doc.path}/index.html\`;
            }
        }
    </script>
</body>
</html>`;

// Sauvegarder le fichier
try {
    fs.writeFileSync(OUTPUT_FILE, html, 'utf8');
    console.log(`✅ Fichier généré: ${OUTPUT_FILE}\n`);
    
    const stats = fs.statSync(OUTPUT_FILE);
    const sizeKB = (stats.size / 1024).toFixed(2);
    console.log(`📊 Taille: ${sizeKB} KB`);
    console.log(`🎉 Génération terminée avec succès!\n`);
} catch (error) {
    console.error(`❌ Erreur lors de la sauvegarde:`, error.message);
    process.exit(1);
}
