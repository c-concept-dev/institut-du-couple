#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           MEGASEARCH GENERATOR - BEAST MODE v3.0 ULTRA                      ║
║           Institut du Couple - Base de Connaissances GPT                     ║
║           Clone Christophe - Expert Thérapie de Couple Mondial              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  CAPACITÉS GPT:                                                              ║
║  ✓ Génération de cours et formations complètes                              ║
║  ✓ Conseils thérapeutiques contextualisés                                   ║
║  ✓ Articles et contenus publiables                                          ║
║  ✓ Parcours pédagogiques structurés                                         ║
║  ✓ Exercices et protocoles adaptés                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

Ce script scanne tous les knowledge_index.json du repo et génère un megasearch.json
optimisé pour servir de base de connaissances à un GPT thérapeutique.

Supporte les formats:
- Claude Ultimate (structure complète avec sous-catégories, notes cliniques)
- Lightbook (structure simplifiée)

Auteur: Institut du Couple
Date: Novembre 2025
"""

import json
import os
import re
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    # Chemins à scanner pour les knowledge_index.json
    "scan_paths": [
        "Base de connaissances/Livres/*/knowledge_index.json",
        "Base de connaissances/**/knowledge_index.json",
        "Modules/*/knowledge_index.json",
        "Outils/*/knowledge_index.json",
    ],
    
    # Fichier de sortie
    "output_file": "megasearch.json",
    
    # Version du megasearch
    "version": "3.0-beast-ultra",
    
    # Types de contenu à indexer
    "content_types": [
        "concept_theorique",
        "framework",
        "outil_therapeutique", 
        "exercice_therapeutique",
        "cas_clinique",
        "citation_reference",
        "technique",
        "protocole",
        "echelle",
        "questionnaire"
    ],
    
    # Mapping des types pour normalisation
    "type_mapping": {
        "concept_theorique": "concept",
        "framework": "framework",
        "outil_therapeutique": "outil",
        "exercice_therapeutique": "exercice",
        "cas_clinique": "cas_clinique",
        "citation_reference": "citation",
        "technique": "technique",
        "protocole": "protocole",
        "echelle": "outil",
        "questionnaire": "outil"
    },
    
    # Catégories thématiques pour génération de contenu
    "thematic_categories": {
        "communication": ["dialogue", "écoute", "expression", "validation", "empathie", "CNV", "message-je"],
        "conflit": ["dispute", "désaccord", "tension", "escalade", "résolution", "médiation", "négociation"],
        "intimité": ["proximité", "sexualité", "tendresse", "connexion", "vulnérabilité", "désir"],
        "attachement": ["sécurité", "anxiété", "évitement", "lien", "figure d'attachement", "base secure"],
        "emotions": ["colère", "peur", "tristesse", "joie", "honte", "culpabilité", "régulation"],
        "famille": ["enfants", "parentalité", "belle-famille", "famille d'origine", "transgénérationnel"],
        "crise": ["séparation", "divorce", "infidélité", "trahison", "reconstruction", "deuil"],
        "developpement": ["croissance", "évolution", "maturité", "différenciation", "autonomie", "interdépendance"]
    },
    
    # Templates de génération pour le GPT
    "generation_templates": {
        "cours": {
            "structure": ["introduction", "objectifs", "concepts_cles", "exercices", "conclusion", "ressources"],
            "niveaux": ["debutant", "intermediaire", "avance", "expert"]
        },
        "article": {
            "structure": ["accroche", "problematique", "developpement", "exemples", "conclusion", "appel_action"],
            "formats": ["blog", "scientifique", "vulgarisation", "temoignage"]
        },
        "formation": {
            "structure": ["module", "sequence", "activite", "evaluation"],
            "durees": ["1h", "demi-journee", "journee", "cycle"]
        },
        "conseil": {
            "structure": ["diagnostic", "explication", "pistes", "exercice", "suivi"],
            "contextes": ["crise", "prevention", "amelioration", "maintenance"]
        }
    }
}

# ============================================================================
# CLASSES PRINCIPALES
# ============================================================================

class MegaSearchGenerator:
    """Générateur du megasearch.json - Version BEAST MODE ULTRA"""
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.documents = []
        self.chunks_complets = []
        self.index_global = {
            "par_approche": defaultdict(list),
            "par_auteur": defaultdict(list),
            "par_problematique": defaultdict(list),
            "par_mot_cle": defaultdict(list),
            "par_type": defaultdict(list),
            "par_categorie": defaultdict(list),
            "par_niveau_complexite": defaultdict(list),
            "par_contexte_therapeutique": defaultdict(list),
            "par_thematique": defaultdict(list)
        }
        # Structures pour génération de contenu
        self.generation_resources = {
            "concepts_par_theme": defaultdict(list),
            "exercices_par_objectif": defaultdict(list),
            "citations_par_auteur": defaultdict(list),
            "frameworks_applicables": [],
            "cas_cliniques_anonymises": [],
            "parcours_pedagogiques": defaultdict(list),
            "connexions_conceptuelles": defaultdict(list)
        }
        self.stats = {
            "total_documents": 0,
            "total_chapitres": 0,
            "total_sections": 0,
            "total_chunks": 0,
            "total_concepts": 0,
            "total_frameworks": 0,
            "total_outils": 0,
            "total_exercices": 0,
            "total_cas_cliniques": 0,
            "total_citations": 0,
            "total_pages": 0
        }
        
    def find_all_json_files(self) -> List[Path]:
        """Trouve tous les knowledge_index.json dans le repo"""
        all_files = set()
        
        for pattern in CONFIG["scan_paths"]:
            full_pattern = str(self.repo_root / pattern)
            files = glob.glob(full_pattern, recursive=True)
            all_files.update(files)
        
        # Recherche récursive de secours
        backup_search = glob.glob(
            str(self.repo_root / "**/knowledge_index.json"), 
            recursive=True
        )
        all_files.update(backup_search)
        
        # Filtrer les fichiers dans node_modules ou .git
        filtered = [
            Path(f) for f in all_files 
            if "node_modules" not in f and ".git" not in f
        ]
        
        print(f"📚 {len(filtered)} fichiers knowledge_index.json trouvés")
        return sorted(filtered)
    
    def detect_format(self, data: Dict) -> str:
        """Détecte le format du JSON (claude_ultimate ou lightbook)"""
        if "version" in data and "claude" in str(data.get("version", "")).lower():
            return "claude_ultimate"
        if data.get("extraction_mode") == "lightbook":
            return "lightbook"
        # Détection par structure
        if "structure_hierarchique" in data:
            chapitres = data.get("structure_hierarchique", {}).get("chapitres", [])
            if chapitres:
                first_chapter = chapitres[0]
                sections = first_chapter.get("sections", [])
                if sections:
                    first_section = sections[0]
                    contenus = first_section.get("contenus", [])
                    if contenus:
                        first_content = contenus[0]
                        # Claude Ultimate a des sous-catégories et notes cliniques
                        if "notes_cliniques" in first_content:
                            return "claude_ultimate"
        return "lightbook"
    
    def generate_document_id(self, titre: str, path: str) -> str:
        """Génère un ID unique pour le document"""
        # Utiliser le nom du dossier parent
        folder_name = Path(path).parent.name
        # Nettoyer et normaliser
        clean_id = re.sub(r'[^a-z0-9]+', '-', folder_name.lower())
        clean_id = clean_id.strip('-')
        return clean_id or f"doc-{hash(titre) % 10000}"
    
    def generate_chunk_id(self, doc_id: str, chapter_id: str, section_id: str, content_id: str) -> str:
        """Génère un ID unique pour un chunk"""
        return f"{doc_id}_{chapter_id}_{section_id}_{content_id}"
    
    def extract_metadata(self, data: Dict, file_path: Path) -> Dict:
        """Extrait les métadonnées du document"""
        doc_meta = data.get("document_metadata", {})
        
        metadata = {
            "id": doc_meta.get("id") or self.generate_document_id(
                doc_meta.get("titre", ""),
                str(file_path)
            ),
            "titre": doc_meta.get("titre", "Sans titre"),
            "auteurs": doc_meta.get("auteurs", []),
            "collaborateurs": doc_meta.get("collaborateurs", []),
            "prefacier": doc_meta.get("prefacier"),
            "editeur": doc_meta.get("editeur"),
            "annee_publication": doc_meta.get("annee_publication"),
            "approches_therapeutiques": doc_meta.get("approches_therapeutiques", []),
            "domaine_expertise": doc_meta.get("domaine_expertise"),
            "langue": doc_meta.get("langue", "fr"),
            "niveau_expertise": doc_meta.get("niveau_expertise"),
            "pages_total": doc_meta.get("pages_total", 0),
            "format_source": self.detect_format(data),
            "path": str(file_path.parent.relative_to(self.repo_root)),
            "json_path": str(file_path.relative_to(self.repo_root))
        }
        
        return metadata
    
    def extract_chunks_from_content(
        self, 
        content: Dict, 
        doc_id: str, 
        doc_titre: str,
        chapter_info: Dict,
        section_info: Dict,
        format_type: str,
        doc_metadata: Dict = None
    ) -> Dict:
        """Extrait un chunk complet depuis un contenu"""
        
        content_id = content.get("contenu_id", "unknown")
        content_type = content.get("type", "concept_theorique")
        normalized_type = CONFIG["type_mapping"].get(content_type, "concept")
        
        # Taxonomie (peut varier selon le format)
        taxonomie = content.get("taxonomie", {})
        
        # Détecter les thématiques automatiquement
        detected_themes = self._detect_themes(content, chapter_info, section_info)
        
        # Générer des tags de génération
        generation_tags = self._generate_content_tags(content, normalized_type)
        
        chunk = {
            # Identification
            "chunk_id": self.generate_chunk_id(
                doc_id, 
                chapter_info.get("chapitre_id", ""),
                section_info.get("section_id", ""),
                content_id
            ),
            "content_id": content_id,
            "document_id": doc_id,
            "document_titre": doc_titre,
            
            # Localisation
            "chapitre": {
                "id": chapter_info.get("chapitre_id"),
                "numero": chapter_info.get("numero"),
                "titre": chapter_info.get("titre"),
                "resume": chapter_info.get("resume_chapitre")
            },
            "section": {
                "id": section_info.get("section_id"),
                "titre": section_info.get("titre")
            },
            "pages": content.get("pages", []),
            
            # Contenu principal
            "type": normalized_type,
            "type_original": content_type,
            "titre": content.get("titre", ""),
            "description_courte": content.get("description_courte", ""),
            "description_detaillee": content.get("description_detaillee", ""),
            
            # Taxonomie et classification
            "taxonomie": {
                "categorie_principale": taxonomie.get("categorie_principale"),
                "sous_categorie": taxonomie.get("sous_categorie"),
                "niveau_complexite": taxonomie.get("niveau_complexite")
            },
            
            # Contexte thérapeutique
            "contexte_therapeutique": content.get("contexte_therapeutique", ""),
            "notes_cliniques": content.get("notes_cliniques", ""),
            
            # Indexation
            "mots_cles_experts": content.get("mots_cles_experts", []),
            "auteurs_references": content.get("auteurs_references", []),
            "references_internes": content.get("references_internes", []),
            
            # Citations
            "citations": content.get("citations", []),
            
            # ══════════════════════════════════════════════════════════════
            # NOUVEAUX CHAMPS POUR GÉNÉRATION DE CONTENU GPT
            # ══════════════════════════════════════════════════════════════
            
            # Thématiques détectées automatiquement
            "thematiques": detected_themes,
            
            # Tags pour génération
            "generation_tags": generation_tags,
            
            # Métadonnées source pour citation
            "source_citation": {
                "auteurs": doc_metadata.get("auteurs", []) if doc_metadata else [],
                "titre_livre": doc_titre,
                "pages": content.get("pages", []),
                "annee": doc_metadata.get("annee_publication") if doc_metadata else None
            },
            
            # Applicabilité pour génération
            "applicabilite": {
                "pour_cours": normalized_type in ["concept", "framework", "technique"],
                "pour_exercice": normalized_type in ["exercice", "outil", "protocole"],
                "pour_article": True,
                "pour_conseil": normalized_type in ["concept", "technique", "outil", "cas_clinique"],
                "pour_formation": True,
                "niveau_requis": taxonomie.get("niveau_complexite", "intermediaire")
            },
            
            # Connexions possibles (pour lier les concepts entre eux)
            "connexions": {
                "concepts_lies": content.get("references_internes", []),
                "prerequis": [],
                "approfondir": []
            },
            
            # Métadonnées de recherche
            "searchable_text": self._build_searchable_text(content, chapter_info, section_info)
        }
        
        return chunk
    
    def _build_searchable_text(self, content: Dict, chapter: Dict, section: Dict) -> str:
        """Construit un texte optimisé pour la recherche"""
        parts = [
            content.get("titre", ""),
            content.get("description_courte", ""),
            content.get("description_detaillee", ""),
            content.get("contexte_therapeutique", ""),
            content.get("notes_cliniques", ""),
            chapter.get("titre", ""),
            chapter.get("resume_chapitre", ""),
            section.get("titre", ""),
            " ".join(content.get("mots_cles_experts", [])),
        ]
        
        # Ajouter les citations
        for citation in content.get("citations", []):
            parts.append(citation.get("texte", ""))
        
        return " ".join(filter(None, parts)).lower()
    
    def process_document(self, file_path: Path) -> Optional[Dict]:
        """Traite un fichier knowledge_index.json"""
        print(f"  📖 Traitement: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"    ❌ Erreur JSON: {e}")
            return None
        except Exception as e:
            print(f"    ❌ Erreur lecture: {e}")
            return None
        
        # Extraire les métadonnées
        metadata = self.extract_metadata(data, file_path)
        doc_id = metadata["id"]
        format_type = metadata["format_source"]
        
        print(f"    📋 Format détecté: {format_type}")
        
        # Statistiques du document
        doc_stats = {
            "chapitres": 0,
            "sections": 0,
            "concepts": 0,
            "frameworks": 0,
            "outils": 0,
            "exercices": 0,
            "cas_cliniques": 0,
            "citations": 0,
            "chunks": 0
        }
        
        # Traiter les chapitres
        structure = data.get("structure_hierarchique", {})
        chapitres = structure.get("chapitres", [])
        
        for chapter in chapitres:
            doc_stats["chapitres"] += 1
            chapter_id = chapter.get("chapitre_id", "")
            
            sections = chapter.get("sections", [])
            for section in sections:
                doc_stats["sections"] += 1
                section_id = section.get("section_id", "")
                
                contenus = section.get("contenus", [])
                for content in contenus:
                    # Extraire le chunk complet
                    chunk = self.extract_chunks_from_content(
                        content=content,
                        doc_id=doc_id,
                        doc_titre=metadata["titre"],
                        chapter_info=chapter,
                        section_info=section,
                        format_type=format_type,
                        doc_metadata=metadata
                    )
                    
                    self.chunks_complets.append(chunk)
                    doc_stats["chunks"] += 1
                    
                    # Comptabiliser par type
                    content_type = content.get("type", "")
                    normalized = CONFIG["type_mapping"].get(content_type, "concept")
                    
                    if normalized == "concept":
                        doc_stats["concepts"] += 1
                    elif normalized == "framework":
                        doc_stats["frameworks"] += 1
                    elif normalized == "outil":
                        doc_stats["outils"] += 1
                    elif normalized == "exercice":
                        doc_stats["exercices"] += 1
                    elif normalized == "cas_clinique":
                        doc_stats["cas_cliniques"] += 1
                    
                    # Comptabiliser les citations
                    doc_stats["citations"] += len(content.get("citations", []))
                    
                    # Indexer le chunk
                    self._index_chunk(chunk, metadata)
        
        # Créer l'entrée document
        document = {
            **metadata,
            "stats": doc_stats
        }
        
        # Mettre à jour les stats globales
        self.stats["total_documents"] += 1
        self.stats["total_chapitres"] += doc_stats["chapitres"]
        self.stats["total_sections"] += doc_stats["sections"]
        self.stats["total_chunks"] += doc_stats["chunks"]
        self.stats["total_concepts"] += doc_stats["concepts"]
        self.stats["total_frameworks"] += doc_stats["frameworks"]
        self.stats["total_outils"] += doc_stats["outils"]
        self.stats["total_exercices"] += doc_stats["exercices"]
        self.stats["total_cas_cliniques"] += doc_stats["cas_cliniques"]
        self.stats["total_citations"] += doc_stats["citations"]
        self.stats["total_pages"] += metadata.get("pages_total", 0)
        
        print(f"    ✅ {doc_stats['chunks']} chunks extraits")
        
        return document
    
    def _index_chunk(self, chunk: Dict, doc_metadata: Dict):
        """Indexe un chunk dans tous les index"""
        chunk_id = chunk["chunk_id"]
        doc_id = chunk["document_id"]
        
        # Index par approche thérapeutique
        for approche in doc_metadata.get("approches_therapeutiques", []):
            if chunk_id not in self.index_global["par_approche"][approche]:
                self.index_global["par_approche"][approche].append(chunk_id)
        
        # Index par auteur
        for auteur in doc_metadata.get("auteurs", []):
            if chunk_id not in self.index_global["par_auteur"][auteur]:
                self.index_global["par_auteur"][auteur].append(chunk_id)
        
        # Index par mot-clé
        for mot_cle in chunk.get("mots_cles_experts", []):
            mot_cle_clean = mot_cle.lower().strip()
            if chunk_id not in self.index_global["par_mot_cle"][mot_cle_clean]:
                self.index_global["par_mot_cle"][mot_cle_clean].append(chunk_id)
        
        # Index par type
        chunk_type = chunk.get("type", "concept")
        if chunk_id not in self.index_global["par_type"][chunk_type]:
            self.index_global["par_type"][chunk_type].append(chunk_id)
        
        # Index par catégorie principale
        categorie = chunk.get("taxonomie", {}).get("categorie_principale")
        if categorie:
            if chunk_id not in self.index_global["par_categorie"][categorie]:
                self.index_global["par_categorie"][categorie].append(chunk_id)
        
        # Index par niveau de complexité
        niveau = chunk.get("taxonomie", {}).get("niveau_complexite")
        if niveau:
            if chunk_id not in self.index_global["par_niveau_complexite"][niveau]:
                self.index_global["par_niveau_complexite"][niveau].append(chunk_id)
        
        # Index par contexte thérapeutique (extraction de mots-clés)
        contexte = chunk.get("contexte_therapeutique", "")
        if contexte:
            # Extraire des mots-clés du contexte
            keywords = self._extract_context_keywords(contexte)
            for kw in keywords:
                if chunk_id not in self.index_global["par_contexte_therapeutique"][kw]:
                    self.index_global["par_contexte_therapeutique"][kw].append(chunk_id)
        
        # ══════════════════════════════════════════════════════════════
        # NOUVEAUX INDEX POUR GÉNÉRATION DE CONTENU
        # ══════════════════════════════════════════════════════════════
        
        # Index par thématique
        for theme in chunk.get("thematiques", []):
            if chunk_id not in self.index_global["par_thematique"][theme]:
                self.index_global["par_thematique"][theme].append(chunk_id)
        
        # Alimenter les ressources de génération
        self._enrich_generation_resources(chunk, doc_metadata)
    
    def _extract_context_keywords(self, text: str) -> List[str]:
        """Extrait des mots-clés thérapeutiques du contexte"""
        keywords = []
        
        # Liste de termes thérapeutiques à détecter
        therapeutic_terms = [
            "communication", "conflit", "émotion", "attachement", "intimité",
            "séparation", "divorce", "infidélité", "sexualité", "parentalité",
            "famille", "enfant", "trauma", "deuil", "dépression", "anxiété",
            "colère", "jalousie", "confiance", "engagement", "autonomie",
            "dépendance", "codépendance", "fusion", "différenciation",
            "dialogue", "écoute", "empathie", "validation", "reconnaissance",
            "blessure", "réparation", "pardon", "réconciliation"
        ]
        
        text_lower = text.lower()
        for term in therapeutic_terms:
            if term in text_lower:
                keywords.append(term)
        
        return keywords
    
    def _detect_themes(self, content: Dict, chapter: Dict, section: Dict) -> List[str]:
        """Détecte automatiquement les thématiques du contenu"""
        detected = []
        
        # Texte à analyser
        text_to_analyze = " ".join([
            content.get("titre", ""),
            content.get("description_courte", ""),
            content.get("description_detaillee", ""),
            content.get("contexte_therapeutique", ""),
            chapter.get("titre", ""),
            section.get("titre", ""),
            " ".join(content.get("mots_cles_experts", []))
        ]).lower()
        
        # Analyser par catégorie thématique
        for theme, keywords in CONFIG["thematic_categories"].items():
            for keyword in keywords:
                if keyword.lower() in text_to_analyze:
                    if theme not in detected:
                        detected.append(theme)
                    break
        
        return detected
    
    def _generate_content_tags(self, content: Dict, content_type: str) -> Dict:
        """Génère des tags pour faciliter la génération de contenu"""
        
        niveau = content.get("taxonomie", {}).get("niveau_complexite", "intermediaire")
        
        tags = {
            # Pour quel type de contenu ce chunk est-il utile?
            "usage_recommande": [],
            
            # Niveau de détail disponible
            "richesse_contenu": "faible",
            
            # Peut servir d'exemple?
            "exemple_possible": False,
            
            # Contient des données chiffrées?
            "contient_donnees": False,
            
            # Contient des citations utilisables?
            "citations_disponibles": len(content.get("citations", [])) > 0,
            
            # Niveau de complexité pour adaptation
            "niveau_vulgarisation": niveau
        }
        
        # Déterminer les usages recommandés
        if content_type == "concept":
            tags["usage_recommande"] = ["cours", "article", "formation"]
        elif content_type == "framework":
            tags["usage_recommande"] = ["cours", "formation", "conseil"]
        elif content_type in ["exercice", "outil"]:
            tags["usage_recommande"] = ["formation", "conseil", "atelier"]
        elif content_type == "cas_clinique":
            tags["usage_recommande"] = ["cours", "article", "formation"]
            tags["exemple_possible"] = True
        elif content_type == "citation":
            tags["usage_recommande"] = ["article", "cours"]
        
        # Évaluer la richesse du contenu
        desc_length = len(content.get("description_detaillee", ""))
        if desc_length > 500:
            tags["richesse_contenu"] = "elevee"
        elif desc_length > 200:
            tags["richesse_contenu"] = "moyenne"
        else:
            tags["richesse_contenu"] = "faible"
        
        # Détecter données chiffrées
        desc = content.get("description_detaillee", "")
        if any(char.isdigit() for char in desc) and ("%" in desc or "étude" in desc.lower()):
            tags["contient_donnees"] = True
        
        return tags
    
    def _enrich_generation_resources(self, chunk: Dict, doc_metadata: Dict):
        """Enrichit les ressources utilisables pour la génération de contenu"""
        chunk_id = chunk["chunk_id"]
        chunk_type = chunk.get("type", "concept")
        
        # Concepts par thème (pour cours et formations)
        for theme in chunk.get("thematiques", []):
            entry = {
                "chunk_id": chunk_id,
                "titre": chunk.get("titre"),
                "type": chunk_type,
                "niveau": chunk.get("taxonomie", {}).get("niveau_complexite"),
                "description_courte": chunk.get("description_courte")
            }
            self.generation_resources["concepts_par_theme"][theme].append(entry)
        
        # Exercices par objectif thérapeutique
        if chunk_type in ["exercice", "outil", "protocole"]:
            contexte = chunk.get("contexte_therapeutique", "")
            entry = {
                "chunk_id": chunk_id,
                "titre": chunk.get("titre"),
                "description": chunk.get("description_detaillee"),
                "contexte": contexte,
                "niveau": chunk.get("taxonomie", {}).get("niveau_complexite")
            }
            # Catégoriser par objectif
            if any(kw in contexte.lower() for kw in ["conflit", "dispute", "tension"]):
                self.generation_resources["exercices_par_objectif"]["resolution_conflit"].append(entry)
            if any(kw in contexte.lower() for kw in ["communication", "dialogue", "écoute"]):
                self.generation_resources["exercices_par_objectif"]["ameliorer_communication"].append(entry)
            if any(kw in contexte.lower() for kw in ["intimité", "connexion", "proximité"]):
                self.generation_resources["exercices_par_objectif"]["renforcer_intimite"].append(entry)
            if any(kw in contexte.lower() for kw in ["émotion", "régulation", "colère"]):
                self.generation_resources["exercices_par_objectif"]["gestion_emotions"].append(entry)
        
        # Citations par auteur (pour articles et cours)
        for citation in chunk.get("citations", []):
            for auteur in doc_metadata.get("auteurs", []):
                entry = {
                    "chunk_id": chunk_id,
                    "texte": citation.get("texte"),
                    "page": citation.get("page"),
                    "contexte": citation.get("contexte"),
                    "livre": doc_metadata.get("titre")
                }
                self.generation_resources["citations_par_auteur"][auteur].append(entry)
        
        # Frameworks applicables (pour formations structurées)
        if chunk_type == "framework":
            self.generation_resources["frameworks_applicables"].append({
                "chunk_id": chunk_id,
                "titre": chunk.get("titre"),
                "description": chunk.get("description_detaillee"),
                "approche": doc_metadata.get("approches_therapeutiques", []),
                "thematiques": chunk.get("thematiques", [])
            })
        
        # Cas cliniques anonymisés (pour exemples pédagogiques)
        if chunk_type == "cas_clinique":
            self.generation_resources["cas_cliniques_anonymises"].append({
                "chunk_id": chunk_id,
                "titre": chunk.get("titre"),
                "description": chunk.get("description_detaillee"),
                "thematiques": chunk.get("thematiques", []),
                "enseignements": chunk.get("notes_cliniques")
            })
        
        # Construire les parcours pédagogiques (regroupement par chapitre)
        chapitre = chunk.get("chapitre", {})
        if chapitre.get("id"):
            parcours_key = f"{chunk['document_id']}_{chapitre['id']}"
            self.generation_resources["parcours_pedagogiques"][parcours_key].append({
                "chunk_id": chunk_id,
                "titre": chunk.get("titre"),
                "type": chunk_type,
                "ordre": len(self.generation_resources["parcours_pedagogiques"][parcours_key])
            })
        
        # Connexions conceptuelles (pour enrichir les cours)
        for ref in chunk.get("references_internes", []):
            self.generation_resources["connexions_conceptuelles"][chunk_id].append(ref)

    def generate(self) -> Dict:
        """Génère le megasearch.json complet"""
        print("\n" + "="*70)
        print("🚀 MEGASEARCH GENERATOR - BEAST MODE v2.0")
        print("="*70 + "\n")
        
        # Trouver tous les fichiers
        json_files = self.find_all_json_files()
        
        if not json_files:
            print("⚠️ Aucun fichier knowledge_index.json trouvé!")
            return {}
        
        # Traiter chaque fichier
        print("\n📚 Traitement des documents...\n")
        for file_path in json_files:
            document = self.process_document(file_path)
            if document:
                self.documents.append(document)
        
        # Convertir les defaultdict en dict standard
        index_final = {}
        for key, value in self.index_global.items():
            if isinstance(value, defaultdict):
                index_final[key] = dict(value)
            else:
                index_final[key] = value
        
        # Convertir les ressources de génération
        generation_final = {}
        for key, value in self.generation_resources.items():
            if isinstance(value, defaultdict):
                generation_final[key] = dict(value)
            else:
                generation_final[key] = value
        
        # Construire le megasearch final
        megasearch = {
            "meta": {
                "version": CONFIG["version"],
                "last_update": datetime.now().isoformat() + "Z",
                "generator": "MegaSearch Generator - Beast Mode ULTRA",
                "description": "Base de connaissances GPT - Expert Thérapie de Couple",
                "capabilities": [
                    "generation_cours",
                    "generation_articles", 
                    "conseils_therapeutiques",
                    "formations_completes",
                    "exercices_adaptes",
                    "parcours_pedagogiques"
                ],
                **self.stats
            },
            
            # ══════════════════════════════════════════════════════════════
            # INSTRUCTIONS GPT - COMMENT UTILISER CETTE BASE
            # ══════════════════════════════════════════════════════════════
            "gpt_instructions": {
                "description": "Instructions pour le GPT sur l'utilisation de cette base de connaissances",
                
                "comment_generer_cours": {
                    "etapes": [
                        "1. Identifier la thématique dans index_global.par_thematique",
                        "2. Récupérer les chunks correspondants dans chunks_complets",
                        "3. Filtrer par niveau via index_global.par_niveau_complexite",
                        "4. Utiliser generation_resources.concepts_par_theme pour structurer",
                        "5. Ajouter exercices depuis generation_resources.exercices_par_objectif",
                        "6. Inclure citations depuis generation_resources.citations_par_auteur"
                    ],
                    "structure_recommandee": CONFIG["generation_templates"]["cours"]
                },
                
                "comment_generer_article": {
                    "etapes": [
                        "1. Chercher par mot-clé dans index_global.par_mot_cle",
                        "2. Sélectionner chunks avec generation_tags.richesse_contenu = 'elevee'",
                        "3. Utiliser les citations pour appuyer les propos",
                        "4. Adapter le niveau avec applicabilite.niveau_requis"
                    ],
                    "structure_recommandee": CONFIG["generation_templates"]["article"]
                },
                
                "comment_donner_conseil": {
                    "etapes": [
                        "1. Identifier la problématique dans index_global.par_contexte_therapeutique",
                        "2. Trouver concepts explicatifs via par_thematique",
                        "3. Proposer exercices depuis generation_resources.exercices_par_objectif",
                        "4. Utiliser cas_cliniques_anonymises pour exemples si pertinent"
                    ],
                    "structure_recommandee": CONFIG["generation_templates"]["conseil"]
                },
                
                "comment_creer_formation": {
                    "etapes": [
                        "1. Définir l'objectif et le niveau cible",
                        "2. Sélectionner un framework dans generation_resources.frameworks_applicables",
                        "3. Construire les modules avec parcours_pedagogiques",
                        "4. Intégrer exercices progressifs par niveau",
                        "5. Ajouter évaluations basées sur les concepts clés"
                    ],
                    "structure_recommandee": CONFIG["generation_templates"]["formation"]
                },
                
                "regles_citation": {
                    "obligatoire": "Toujours citer la source via chunk.source_citation",
                    "format": "({auteur}, {titre_livre}, p.{page})",
                    "exemple": "(Yvon Dallaire, Qui sont ces couples heureux?, p.45)"
                },
                
                "adaptation_niveau": {
                    "debutant": "Vulgariser, éviter jargon, exemples concrets",
                    "intermediaire": "Équilibre théorie/pratique, terminologie accessible",
                    "avance": "Concepts approfondis, nuances, références croisées",
                    "expert": "Niveau professionnel, protocoles détaillés, cas complexes"
                }
            },
            
            "documents": self.documents,
            "chunks_complets": self.chunks_complets,
            "index_global": index_final,
            "generation_resources": generation_final,
            
            # Templates de génération pour référence
            "templates_generation": CONFIG["generation_templates"],
            "categories_thematiques": CONFIG["thematic_categories"]
        }
        
        # Rapport final
        print("\n" + "="*70)
        print("📊 RAPPORT DE GÉNÉRATION")
        print("="*70)
        print(f"  📚 Documents traités:     {self.stats['total_documents']}")
        print(f"  📑 Chapitres:             {self.stats['total_chapitres']}")
        print(f"  📄 Sections:              {self.stats['total_sections']}")
        print(f"  🧩 Chunks totaux:         {self.stats['total_chunks']}")
        print(f"  💡 Concepts:              {self.stats['total_concepts']}")
        print(f"  🔧 Frameworks:            {self.stats['total_frameworks']}")
        print(f"  🛠️ Outils:                {self.stats['total_outils']}")
        print(f"  📝 Exercices:             {self.stats['total_exercices']}")
        print(f"  📋 Cas cliniques:         {self.stats['total_cas_cliniques']}")
        print(f"  💬 Citations:             {self.stats['total_citations']}")
        print(f"  📖 Pages totales:         {self.stats['total_pages']}")
        print("="*70 + "\n")
        
        return megasearch
    
    def save(self, megasearch: Dict, output_path: str = None):
        """Sauvegarde le megasearch.json"""
        if output_path is None:
            output_path = self.repo_root / CONFIG["output_file"]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(megasearch, f, ensure_ascii=False, indent=2)
        
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"💾 Fichier sauvegardé: {output_path}")
        print(f"📦 Taille: {file_size:.2f} MB")


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Génère le megasearch.json pour la base de connaissances GPT"
    )
    parser.add_argument(
        "--repo", 
        default=".",
        help="Chemin vers la racine du repo (défaut: répertoire courant)"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Chemin du fichier de sortie (défaut: megasearch.json à la racine)"
    )
    
    args = parser.parse_args()
    
    # Générer
    generator = MegaSearchGenerator(repo_root=args.repo)
    megasearch = generator.generate()
    
    # Sauvegarder
    if megasearch:
        generator.save(megasearch, args.output)
        print("\n✅ Génération terminée avec succès!")
    else:
        print("\n❌ Échec de la génération")
        exit(1)


if __name__ == "__main__":
    main()
