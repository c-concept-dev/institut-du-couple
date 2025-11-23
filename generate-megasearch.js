#!/usr/bin/env node

/**
 * Generate MegaSearch.json
 * 
 * Ce script scanne récursivement le dossier "Base de connaissances/"
 * et agrège tous les fichiers knowledge_index.json en un seul
 * megasearch.json avec index global complet.
 * 
 * Usage: node generate-megasearch.js [chemin-base]
 */

const fs = require('fs');
const path = require('path');

// Configuration
const BASE_DIR = process.argv[2] || './Base de connaissances';
const OUTPUT_FILE = './megasearch.json';

// État global
const megasearch = {
    meta: {
        version: "1.0",
        last_update: new Date().toISOString(),
        total_documents: 0,
        total_chapitres: 0,
        total_chunks: 0,
        total_pages: 0
    },
    documents: [],
    chunks_complets: [],
    index_global: {
        par_approche: {},
        par_problematique: {},
        par_mot_cle: {},
        par_type: {
            concept: [],
            exercice: [],
            cas: [],
            citation: [],
            outil: []
        }
    }
};

console.log('🚀 Génération du megasearch.json...\n');
console.log(`📁 Dossier de base: ${BASE_DIR}\n`);

/**
 * Scanner récursivement un dossier pour trouver tous les knowledge_index.json
 */
function findKnowledgeFiles(dir) {
    const files = [];
    
    if (!fs.existsSync(dir)) {
        console.error(`❌ Erreur: Le dossier ${dir} n'existe pas`);
        return files;
    }

    function scan(currentDir) {
        const entries = fs.readdirSync(currentDir, { withFileTypes: true });
        
        for (const entry of entries) {
            const fullPath = path.join(currentDir, entry.name);
            
            if (entry.isDirectory()) {
                scan(fullPath);
            } else if (entry.name === 'knowledge_index.json') {
                files.push(fullPath);
            }
        }
    }
    
    scan(dir);
    return files;
}

/**
 * Charger et parser un fichier JSON
 */
function loadJSON(filepath) {
    try {
        const content = fs.readFileSync(filepath, 'utf8');
        return JSON.parse(content);
    } catch (error) {
        console.error(`❌ Erreur lors de la lecture de ${filepath}:`, error.message);
        return null;
    }
}

/**
 * Ajouter un document au megasearch
 */
function addDocumentToMegasearch(knowledgeData, filepath) {
    const doc = knowledgeData.document;
    const stats = knowledgeData.stats;
    const relativePath = path.relative(process.cwd(), path.dirname(filepath));
    
    // Ajouter aux documents
    const docEntry = {
        id: doc.id,
        titre: doc.titre,
        auteurs: doc.auteurs || [],
        approches: doc.approches || [],
        langue: doc.langue || 'fr',
        annee: doc.annee || null,
        editeur: doc.editeur || null,
        path: relativePath.replace(/\\/g, '/'),
        json_path: './knowledge_index.json',
        pdf_path: './source.pdf',
        stats: {
            chapitres: stats.chapitres || 0,
            concepts: stats.concepts || 0,
            exercices: stats.exercices || 0,
            cas: stats.cas || 0,
            citations: stats.citations || 0,
            total_chunks: stats.total_chunks || 0
        },
        pages_total: doc.pages_total || 0
    };
    
    megasearch.documents.push(docEntry);
    
    // Mise à jour des métadonnées globales
    megasearch.meta.total_documents++;
    megasearch.meta.total_chapitres += stats.chapitres || 0;
    megasearch.meta.total_chunks += stats.total_chunks || 0;
    megasearch.meta.total_pages += doc.pages_total || 0;
    
    // Indexer par approche
    for (const approche of doc.approches || []) {
        if (!megasearch.index_global.par_approche[approche]) {
            megasearch.index_global.par_approche[approche] = [];
        }
        megasearch.index_global.par_approche[approche].push(doc.id);
    }
    
    // Traiter tous les chunks
    for (const chapitre of knowledgeData.chapitres || []) {
        for (const chunk of chapitre.contenus || []) {
            // Ajouter le chunk complet
            const chunkComplet = {
                doc_id: doc.id,
                doc_titre: doc.titre,
                chapitre_id: chapitre.chapitre_id,
                chapitre_titre: chapitre.titre,
                chunk_id: chunk.chunk_id,
                type: chunk.type,
                titre: chunk.titre,
                pages: chunk.pages,
                approche: chunk.approche,
                problematiques: chunk.problematiques || [],
                mots_cles: chunk.mots_cles || [],
                contenu_texte: chunk.contenu?.texte || '',
                contenu_resume: chunk.contenu?.resume || '',
                questions_cliniques: chunk.contenu?.questions_cliniques || [],
                pdf_direct_link: `${relativePath.replace(/\\/g, '/')}/source.pdf#page=${chunk.pages[0]}`,
                metadata: chunk.metadata || {}
            };
            
            megasearch.chunks_complets.push(chunkComplet);
            
            // Indexer par type
            if (megasearch.index_global.par_type[chunk.type]) {
                megasearch.index_global.par_type[chunk.type].push({
                    doc_id: doc.id,
                    chunk_id: chunk.chunk_id,
                    titre: chunk.titre
                });
            }
            
            // Indexer par problématique
            for (const prob of chunk.problematiques || []) {
                if (!megasearch.index_global.par_problematique[prob]) {
                    megasearch.index_global.par_problematique[prob] = [];
                }
                megasearch.index_global.par_problematique[prob].push({
                    doc_id: doc.id,
                    chunk_id: chunk.chunk_id,
                    titre: chunk.titre
                });
            }
            
            // Indexer par mot-clé
            for (const motCle of chunk.mots_cles || []) {
                if (!megasearch.index_global.par_mot_cle[motCle]) {
                    megasearch.index_global.par_mot_cle[motCle] = [];
                }
                megasearch.index_global.par_mot_cle[motCle].push({
                    doc_id: doc.id,
                    chunk_id: chunk.chunk_id,
                    titre: chunk.titre
                });
            }
        }
    }
    
    console.log(`✅ ${doc.titre}`);
    console.log(`   📊 ${stats.total_chunks} chunks | ${stats.chapitres} chapitres | ${doc.pages_total} pages`);
}

/**
 * Sauvegarder le megasearch.json
 */
function saveMegasearch() {
    try {
        const json = JSON.stringify(megasearch, null, 2);
        fs.writeFileSync(OUTPUT_FILE, json, 'utf8');
        console.log(`\n✅ Fichier généré: ${OUTPUT_FILE}`);
        
        // Afficher les statistiques finales
        console.log('\n📊 Statistiques globales:');
        console.log(`   • Documents: ${megasearch.meta.total_documents}`);
        console.log(`   • Chapitres: ${megasearch.meta.total_chapitres}`);
        console.log(`   • Chunks: ${megasearch.meta.total_chunks}`);
        console.log(`   • Pages: ${megasearch.meta.total_pages}`);
        console.log(`   • Approches: ${Object.keys(megasearch.index_global.par_approche).length}`);
        console.log(`   • Problématiques: ${Object.keys(megasearch.index_global.par_problematique).length}`);
        console.log(`   • Mots-clés: ${Object.keys(megasearch.index_global.par_mot_cle).length}`);
        
        // Taille du fichier
        const stats = fs.statSync(OUTPUT_FILE);
        const sizeKB = (stats.size / 1024).toFixed(2);
        console.log(`   • Taille: ${sizeKB} KB`);
        
    } catch (error) {
        console.error(`❌ Erreur lors de la sauvegarde:`, error.message);
        process.exit(1);
    }
}

/**
 * Main
 */
function main() {
    console.log('📂 Recherche des fichiers knowledge_index.json...\n');
    
    const knowledgeFiles = findKnowledgeFiles(BASE_DIR);
    
    if (knowledgeFiles.length === 0) {
        console.log(`⚠️  Aucun fichier knowledge_index.json trouvé dans ${BASE_DIR}`);
        console.log('\n💡 Assurez-vous que:');
        console.log('   • Le dossier "Base de connaissances/" existe');
        console.log('   • Vous avez converti au moins un PDF avec le convertisseur');
        console.log('   • Les fichiers knowledge_index.json sont présents dans les sous-dossiers');
        process.exit(1);
    }
    
    console.log(`📚 ${knowledgeFiles.length} document(s) trouvé(s):\n`);
    
    // Traiter chaque fichier
    for (const filepath of knowledgeFiles) {
        const knowledgeData = loadJSON(filepath);
        if (knowledgeData) {
            addDocumentToMegasearch(knowledgeData, filepath);
        }
    }
    
    // Sauvegarder le résultat
    saveMegasearch();
    
    console.log('\n🎉 Génération terminée avec succès!\n');
}

// Exécution
main();
