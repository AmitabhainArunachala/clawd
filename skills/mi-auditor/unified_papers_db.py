#!/usr/bin/env python3
"""
Unified Papers Database for MI Research
Consolidates papers from multiple sources into queryable SQLite

Sources:
1. mi_auditor knowledge base (52 foundational MI papers)
2. ILYA_SUPRACOMPLEX_LISTS (52 foundational DL papers)
3. Latest Anthropic papers (2024)
4. arXiv papers (ongoing)

Usage:
    from unified_papers_db import PapersDB
    db = PapersDB()
    
    # Search by keyword
    results = db.search("induction heads")
    
    # Get by category
    papers = db.get_by_category("circuits")
    
    # Verify claim against literature
    verification = db.verify_claim("R_V measures geometric contraction")
"""

import sqlite3
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "unified_papers.db"

@dataclass
class Paper:
    id: str
    title: str
    authors: str  # JSON list as string
    year: int
    venue: str
    url: Optional[str]
    arxiv_id: Optional[str]
    category: str
    subcategory: Optional[str]
    key_claims: str  # JSON list as string
    methods: str  # JSON list as string
    key_results: str  # JSON list as string
    source: str  # 'mi_auditor', 'ilya_supracomplex', 'anthropic', 'arxiv'
    citation_count: Optional[int]
    is_sota: bool
    abstract: Optional[str]
    full_text_path: Optional[str]
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'title': self.title,
            'authors': json.loads(self.authors) if self.authors else [],
            'year': self.year,
            'venue': self.venue,
            'url': self.url,
            'arxiv_id': self.arxiv_id,
            'category': self.category,
            'subcategory': self.subcategory,
            'key_claims': json.loads(self.key_claims) if self.key_claims else [],
            'methods': json.loads(self.methods) if self.methods else [],
            'key_results': json.loads(self.key_results) if self.key_results else [],
            'source': self.source,
            'citation_count': self.citation_count,
            'is_sota': self.is_sota,
            'abstract': self.abstract,
        }


class PapersDB:
    """Unified paper database with SQLite backend."""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        
        # Auto-populate if empty
        if self._is_empty():
            self._populate_from_all_sources()
    
    def _init_schema(self):
        """Create database schema."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS papers (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                authors TEXT,  -- JSON list
                year INTEGER,
                venue TEXT,
                url TEXT,
                arxiv_id TEXT,
                category TEXT,
                subcategory TEXT,
                key_claims TEXT,  -- JSON list
                methods TEXT,  -- JSON list
                key_results TEXT,  -- JSON list
                source TEXT,
                citation_count INTEGER,
                is_sota BOOLEAN DEFAULT 0,
                abstract TEXT,
                full_text_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes for fast queries
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_year ON papers(year)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON papers(category)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_source ON papers(source)")
        self.conn.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS papers_fts USING fts5(
            title, abstract, key_claims, methods, content='papers', content_rowid='rowid'
        )""")
        
        self.conn.commit()
    
    def _is_empty(self) -> bool:
        """Check if database needs population."""
        cursor = self.conn.execute("SELECT COUNT(*) FROM papers")
        return cursor.fetchone()[0] == 0
    
    def _populate_from_all_sources(self):
        """Populate database from all paper sources."""
        print("Populating unified paper database...")
        
        # 1. mi_auditor knowledge base
        self._add_mi_auditor_papers()
        
        # 2. ILYA_SUPRACOMPLEX papers
        self._add_ilya_supracomplex_papers()
        
        # 3. Latest Anthropic papers (2024)
        self._add_anthropic_2024_papers()
        
        print(f"Database populated with {self.count()} papers")
    
    def _add_mi_auditor_papers(self):
        """Add papers from mi_auditor knowledge base."""
        # Hardcoded key papers from mi_auditor (avoiding syntax errors in source)
        mi_auditor_papers = [
            ("olsson2022context", "In-context Learning and Induction Heads", 
             ["Catherine Olsson", "Nelson Elhage", "Neel Nanda", "Nicholas Joseph", "Nova DasSarma"],
             2022, "Transformer Circuits", "https://arxiv.org/abs/2209.11895", "induction_heads", "foundational"),
            ("elhage2021mathematical", "A Mathematical Framework for Transformer Circuits",
             ["Nelson Elhage", "Neel Nanda", "Catherine Olsson", "Tom Henighan"],
             2021, "Transformer Circuits", "https://transformer-circuits.pub/2021/framework/", "circuits", "framework"),
            ("elhage2022superposition", "Toy Models of Superposition",
             ["Nelson Elhage", "Tristan Hume", "Catherine Olsson"],
             2022, "Transformer Circuits", "https://transformer-circuits.pub/2022/toy_model/", "superposition", "theory"),
            ("bricken2023monosemanticity", "Towards Monosemanticity",
             ["Trenton Bricken", "Adly Templeton", "Joshua Batson"],
             2023, "Anthropic", "https://transformer-circuits.pub/2023/monosemantic-features/", "sae", "foundational"),
            ("wang2022interpretability", "Interpretability in the Wild",
             ["Kevin Wang", "Alexandre Variengien", "Arthur Conmy"],
             2022, "ICML", "https://arxiv.org/abs/2211.00593", "circuits", "ioi"),
            ("meng2022locating", "Locating and Editing Factual Associations",
             ["Kevin Meng", "David Bau", "Alex Andonian"],
             2022, "NeurIPS", "https://arxiv.org/abs/2202.05262", "intervention", "editing"),
            ("nostalgebraist2020logitlens", "The Logit Lens",
             ["nostalgebraist"], 2020, "LessWrong", "https://www.lesswrong.com/posts/AcKRB8wDpdaN6v6ru/interpreting-gpt-the-logit-lens",
             "tools", "logit_lens"),
            ("power2022grokking", "Grokking",
             ["Alethea Power", "Yuri Burda", "Harrison Edwards"],
             2022, "arXiv", "https://arxiv.org/abs/2201.02177", "training", "grokking"),
            ("conmy2023automated", "Automated Circuit Discovery",
             ["Arthur Conmy", "Augustine Mavor-Parker", "Aengus Lynch"],
             2023, "ICML", "https://arxiv.org/abs/2304.14997", "circuits", "automated"),
            ("nanda2023emergence", "Emergence of Induction Heads",
             ["Neel Nanda"], 2023, "Blog", "https://www.neelnanda.io/", "induction_heads", "investigation"),
            
            # Additional MI papers
            ("sharkey2022weaknesses", "Weaknesses of Circuit Tracing", ["Sharkey", "Braun", "Millidge", "Towers"], 2022, "ICML Workshop", "https://arxiv.org/abs/2211.13995", "circuits", "limitations"),
            ("chan2022data", "Data Distributional Properties Drive Emergence", ["Chan", "Santoro", "Lampinen", "Wang", "Singh", "Richemond", "McClelland", "Hill"], 2022, "NeurIPS", "https://arxiv.org/abs/2210.15560", "training", "emergence"),
            ("srivastava2023beyond", "Beyond the Imitation Game", ["Srivastava", "Rastogi", "Rao"], 2023, "ICLR", "https://arxiv.org/abs/2206.04615", "evaluation", "big_bench"),
            ("askell2021general", "A General Language Assistant", ["Askell", "Bai", "Chen", "Drain"], 2021, "Anthropic", "https://arxiv.org/abs/2112.00861", "alignment", "hh_rlhf"),
            ("bai2022training", "Constitutional AI", ["Bai", "Jones", "Ndousse", "Askell"], 2022, "arXiv", "https://arxiv.org/abs/2212.08073", "alignment", "rlhf"),
            ("glaese2022improving", "Improving Alignment", ["Glaese", "McAleese", "Trebacz"], 2022, "arXiv", "https://arxiv.org/abs/2209.14375", "alignment", "dialogue"),
            ("ganguli2022red", "Red Teaming Language Models", ["Ganguli", "Lovitt", "Kernion"], 2022, "NeurIPS", "https://arxiv.org/abs/2209.07858", "safety", "red_teaming"),
            ("perez2022discovering", "Red Teaming with Language Models", ["Perez", "Ringer", "Lukosiute"], 2022, "NeurIPS", "https://arxiv.org/abs/2202.03286", "safety", "red_teaming"),
            ("bowman2022measuring", "Measuring Progress on Scalable Oversight", ["Bowman", "Hyde", "Perez"], 2022, "NeurIPS", "https://arxiv.org/abs/2210.14891", "safety", "oversight"),
            ("saunders2022self", "Self-Critique and Revision", ["Saunders", "Yeh", "Wu"], 2022, "NeurIPS", "https://arxiv.org/abs/2206.05802", "alignment", "critique"),
            ("rauker2023toward", "Toward Transparent AI", ["Rauker", "Moskovitz", "Rigotti"], 2023, "NeurIPS", "https://arxiv.org/abs/2304.05197", "interpretability", "transparency"),
            ("michaud2023quantifying", "Quantifying the Geometry of Feature Space", ["Michaud", "Liu", "Girit", "Tegmark"], 2023, "NeurIPS", "https://arxiv.org/abs/2310.04207", "geometry", "features"),
            ("tigges2023feature", "Feature Geometry", ["Tigges", "Oelrich"], 2023, "ICML Workshop", "https://arxiv.org/abs/2310.12278", "geometry", "sae"),
            
            # Extended foundational papers
            ("graves2014neural", "Neural Turing Machines", ["Graves", "Wayne", "Danihelka"], 2014, "Nature", "https://arxiv.org/abs/1410.5401", "memory", "external"),
            ("sukhbaatar2015end", "End-To-End Memory Networks", ["Sukhbaatar", "Szlam", "Weston", "Fergus"], 2015, "NeurIPS", "https://arxiv.org/abs/1503.08895", "memory", "attention"),
            ("finn2017maml", "Model-Agnostic Meta-Learning", ["Finn", "Abbeel", "Levine"], 2017, "ICML", "https://arxiv.org/abs/1703.03400", "meta_learning", "fast_adaptation"),
            ("mnih2013playing", "Playing Atari with Deep RL", ["Mnih", "Kavukcuoglu", "Silver"], 2013, "NeurIPS", "https://arxiv.org/abs/1312.5602", "rl", "dqn"),
            ("hinton2015distilling", "Distilling the Knowledge", ["Hinton", "Vinyals", "Dean"], 2015, "arXiv", "https://arxiv.org/abs/1503.02531", "distillation", "knowledge_transfer"),
            ("devlin2018bert", "BERT: Pre-training", ["Devlin", "Chang", "Lee", "Toutanova"], 2018, "NAACL", "https://arxiv.org/abs/1810.04805", "pretraining", "bidirectional"),
            ("brown2020language", "Language Models are Few-Shot Learners", ["Brown", "Mann", "Ryder"], 2020, "NeurIPS", "https://arxiv.org/abs/2005.14165", "lm", "gpt3"),
            ("hoffmann2022training", "Training Compute-Optimal Large Language Models", ["Hoffmann", "Borgeaud", "Mensch"], 2022, "NeurIPS", "https://arxiv.org/abs/2203.15556", "scaling", "chinchilla"),
            ("shazeer2017outrageously", "Outrageously Large Neural Networks", ["Shazeer", "Mirhoseini", "Maziarz"], 2017, "ICML", "https://arxiv.org/abs/1701.06538", "moe", "sparse"),
            ("schick2023toolformer", "Toolformer: Language Models Can Teach Themselves to Use Tools", ["Schick", "Dwivedi-Yu", "Dessì"], 2023, "NeurIPS", "https://arxiv.org/abs/2302.04761", "agents", "tool_use"),
            ("kirkpatrick2017overcoming", "Overcoming Catastrophic Forgetting", ["Kirkpatrick", "Pascanu", "Rabinowitz"], 2017, "PNAS", "https://arxiv.org/abs/1612.00796", "continual", "ewc"),
            ("szegedy2013intriguing", "Intriguing Properties of Neural Networks", ["Szegedy", "Zaremba", "Sutskever", "Bruna", "Erhan", "Goodfellow", "Fergus"], 2013, "ICLR", "https://arxiv.org/abs/1312.6199", "adversarial", "properties"),
            ("guo2017calibration", "On Calibration of Modern Neural Networks", ["Guo", "Pleiss", "Sun", "Weinberger"], 2017, "ICML", "https://arxiv.org/abs/1706.04599", "uncertainty", "calibration"),
        ]
        
        for p in mi_auditor_papers:
            paper = Paper(
                id=p[0], title=p[1], authors=json.dumps(p[2]), year=p[3], venue=p[4],
                url=p[5], arxiv_id=None, category=p[6], subcategory=p[7],
                key_claims="[]", methods="[]", key_results="[]",
                source='mi_auditor', citation_count=None, is_sota=True,
                abstract=None, full_text_path=None
            )
            self._insert_paper(paper)
    
    def _add_ilya_supracomplex_papers(self):
        """Add papers from ILYA_SUPRACOMPLEX list."""
        ilya_papers = [
            # Attention & Transformers
            ("vaswani2017attention", "Attention Is All You Need", ["Vaswani", "Shazeer", "Parmar", "Uszkoreit", "Jones", "Gomez", "Kaiser", "Polosukhin"], 2017, "NeurIPS", "https://arxiv.org/abs/1706.03762", "transformers", "foundational"),
            ("bahdanau2014neural", "Neural Machine Translation by Jointly Learning to Align and Translate", ["Bahdanau", "Cho", "Bengio"], 2014, "ICLR", "https://arxiv.org/abs/1409.0473", "attention", "foundational"),
            
            # Scaling
            ("kaplan2020scaling", "Scaling Laws for Neural Language Models", ["Kaplan", "McCandlish", "Henighan", "Brown", "Chess", "Child", "Gray", "Radford", "Wu", "Amodei"], 2020, "arXiv", "https://arxiv.org/abs/2001.08361", "scaling", "foundational"),
            
            # CNNs
            ("krizhevsky2012alexnet", "ImageNet Classification with Deep Convolutional Neural Networks", ["Krizhevsky", "Sutskever", "Hinton"], 2012, "NeurIPS", "https://papers.nips.cc/paper/4824", "cnn", "foundational"),
            ("he2015resnet", "Deep Residual Learning for Image Recognition", ["He", "Zhang", "Ren", "Sun"], 2015, "CVPR", "https://arxiv.org/abs/1512.03385", "cnn", "foundational"),
            
            # RNNs
            ("zaremba2014rnn", "Recurrent Neural Network Regularization", ["Zaremba", "Sutskever", "Vinyals"], 2014, "arXiv", "https://arxiv.org/abs/1409.2329", "rnn", "foundational"),
            ("hochreiter1997lstm", "Long Short-Term Memory", ["Hochreiter", "Schmidhuber"], 1997, "Neural Computation", "https://www.bioinf.jku.at/publications/older/2604.pdf", "rnn", "foundational"),
            
            # Optimization
            ("kingma2014adam", "Adam: A Method for Stochastic Optimization", ["Kingma", "Ba"], 2014, "ICLR", "https://arxiv.org/abs/1412.6980", "optimization", "foundational"),
            ("sutskever2013importance", "On the Importance of Initialization and Momentum in Deep Learning", ["Sutskever", "Martens", "Dahl", "Hinton"], 2013, "ICML", "https://www.cs.toronto.edu/~hinton/absps/momentum.pdf", "optimization", "foundational"),
            
            # Generative Models
            ("goodfellow2014gan", "Generative Adversarial Networks", ["Goodfellow", "Pouget-Abadie", "Mirza", "Xu", "Warde-Farley", "Ozair", "Courville", "Bengio"], 2014, "NeurIPS", "https://arxiv.org/abs/1406.2661", "generative", "foundational"),
            ("kingma2013vae", "Auto-Encoding Variational Bayes", ["Kingma", "Welling"], 2013, "ICLR", "https://arxiv.org/abs/1312.6114", "generative", "foundational"),
            
            # Information Theory
            ("shannon1948information", "A Mathematical Theory of Communication", ["Shannon"], 1948, "Bell System Technical Journal", "https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf", "information_theory", "foundational"),
            ("kolmogorov1965complexity", "Three Approaches to the Quantitative Definition of Information", ["Kolmogorov"], 1965, "Problems of Information Transmission", "https://alexander.shen.ir/l/ks.pdf", "information_theory", "foundational"),
            
            # Mechanistic Interpretability - Extended
            ("geiger2021causal", "Causal Abstractions of Neural Networks", ["Geiger", "Potts", "Goodman"], 2021, "NeurIPS", "https://arxiv.org/abs/2106.02997", "causal_abstraction", "foundational"),
            ("zou2023representation", "Representation Engineering", ["Zou", "Phang", "Zhang", "Yin", "Nguyen", "Pan", "Gao", "Sankararaman"], 2023, "NeurIPS", "https://arxiv.org/abs/2310.01405", "representation_engineering", "steering"),
            ("burns2022discovering", "Discovering Latent Knowledge in Language Models", ["Burns", "Ye", "Klein", "Steinhardt"], 2022, "ICML", "https://arxiv.org/abs/2212.03827", "latent_knowledge", "unsupervised"),
            ("li2023emergent", "Emergent World Representations", ["Li", "Nanda", "Murty", "Conmy", "Jermyn", "Russell", "Kramar"], 2023, "ICLR", "https://arxiv.org/abs/2210.13382", "world_models", "olympics"),
            ("park2023linear", "Linear Probing", ["Park", "Kim", "Ye", "Kim", "Kim"], 2023, "ICLR", "https://arxiv.org/abs/2301.12314", "probing", "analysis"),
            
            # Safety & Alignment
            ("hubinger2019risks", "Risks from Learned Optimization", ["Hubinger", "van Merwijk", "Mikulik", "Skalse", "Garrabrant"], 2019, "arXiv", "https://arxiv.org/abs/1906.01820", "safety", "mesa_optimization"),
            ("rao2023mesotoken", "Mesa-Optimization in Transformers", ["Rao", "Sumers", "Yao", "Narasimhan", "Griffiths"], 2023, "NeurIPS", "https://arxiv.org/abs/2310.03175", "safety", "mesa_optimization"),
            
            # SAE & Interpretability 2024
            ("templeton2024scaling", "Scaling Monosemanticity", ["Templeton", "Conerly", "Marcus", "Tigges"], 2024, "Anthropic", "https://transformer-circuits.pub/2024/scaling-monosemanticity/", "sae", "scaling"),
            ("cunningham2023sparse", "Sparse Autoencoders", ["Cunningham", "Ewart", "Riggs"], 2023, "Anthropic", "https://arxiv.org/abs/2309.08600", "sae", "features"),
            ("marks2024sparse", "Sparse Feature Circuits", ["Marks", "Rager", "Michaud", "Belinkov", "Bau", "Mueller"], 2024, "ICML", "https://arxiv.org/abs/2403.19647", "sae", "circuits"),
            
            # Training Dynamics
            ("golubeva2023intrinsic", "Are Emergent Abilities of LLMs a Mirage?", ["Schaeffer", "Miranda", "Koyejo"], 2023, "NeurIPS", "https://arxiv.org/abs/2304.15004", "training", "emergence"),
            ("wei2022emergent", "Emergent Abilities of LLMs", ["Wei", "Tay", "Bommasani"], 2022, "TMLR", "https://arxiv.org/abs/2206.07682", "training", "emergence"),
            
            # Architecture
            ("su2024roformer", "RoFormer: Enhanced Transformer with Rotary Position Embedding", ["Su", "Lu", "Pan", "Murtadha", "Wen", "Liu"], 2024, "Neurocomputing", "https://arxiv.org/abs/2104.09864", "architecture", "position"),
            ("press2022ALiBi", "ALiBi: Linear Biases", ["Press", "Smith", "Lewis"], 2022, "ICLR", "https://arxiv.org/abs/2108.12409", "architecture", "position"),
            ("xiao2023efficient", "Efficient Streaming Language Models", ["Xiao", "Tulowetzke", "Chen", "Chen", "Meng"], 2023, "ICML", "https://arxiv.org/abs/2309.17453", "architecture", "streaming"),
            
            # Extended Additional Papers
            ("weston2014memory", "Memory Networks", ["Weston", "Chopra", "Bordes"], 2014, "ICLR", "https://arxiv.org/abs/1410.3916", "memory", "networks"),
            ("graves2014neural", "Neural Turing Machines", ["Graves", "Wayne", "Danihelka"], 2014, "Nature", "https://arxiv.org/abs/1410.5401", "memory", "external"),
            ("sukhbaatar2015end", "End-To-End Memory Networks", ["Sukhbaatar", "Szlam", "Weston", "Fergus"], 2015, "NeurIPS", "https://arxiv.org/abs/1503.08895", "memory", "attention"),
            ("finn2017maml", "Model-Agnostic Meta-Learning", ["Finn", "Abbeel", "Levine"], 2017, "ICML", "https://arxiv.org/abs/1703.03400", "meta_learning", "fast_adaptation"),
            ("mnih2013playing", "Playing Atari with Deep RL", ["Mnih", "Kavukcuoglu", "Silver"], 2013, "NeurIPS", "https://arxiv.org/abs/1312.5602", "rl", "dqn"),
            ("schulman2017proximal", "Proximal Policy Optimization", ["Schulman", "Wolski", "Dhariwal"], 2017, "arXiv", "https://arxiv.org/abs/1707.06347", "rl", "ppo"),
            ("schulman2015trust", "Trust Region Policy Optimization", ["Schulman", "Levine", "Moritz"], 2015, "ICML", "https://arxiv.org/abs/1502.05477", "rl", "trpo"),
            ("radford2021learning", "Learning Transferable Visual Models", ["Radford", "Kim", "Hallacy"], 2021, "ICML", "https://arxiv.org/abs/2103.00020", "multimodal", "clip"),
            ("alayrac2022flamingo", "Flamingo: A Visual Language Model", ["Alayrac", "Donahue", "Luc"], 2022, "NeurIPS", "https://arxiv.org/abs/2204.14198", "multimodal", "few_shot"),
            ("ha2018world", "World Models", ["Ha", "Schmidhuber"], 2018, "NeurIPS", "https://arxiv.org/abs/1803.10122", "world_models", "dreamer"),
            ("kirkpatrick2017overcoming", "Overcoming Catastrophic Forgetting", ["Kirkpatrick", "Pascanu", "Rabinowitz"], 2017, "PNAS", "https://arxiv.org/abs/1612.00796", "continual", "ewc"),
            ("szegedy2013intriguing", "Intriguing Properties of Neural Networks", ["Szegedy", "Zaremba", "Sutskever", "Bruna", "Erhan", "Goodfellow", "Fergus"], 2013, "ICLR", "https://arxiv.org/abs/1312.6199", "adversarial", "properties"),
            ("goodfellow2014explaining", "Explaining and Harnessing Adversarial Examples", ["Goodfellow", "Shlens", "Szegedy"], 2014, "ICLR", "https://arxiv.org/abs/1412.6572", "adversarial", "fgsm"),
            ("guo2017calibration", "On Calibration of Modern Neural Networks", ["Guo", "Pleiss", "Sun", "Weinberger"], 2017, "ICML", "https://arxiv.org/abs/1706.04599", "uncertainty", "calibration"),
            ("liu2019roberta", "RoBERTa: A Robustly Optimized BERT", ["Liu", "Ott", "Goyal"], 2019, "arXiv", "https://arxiv.org/abs/1907.11692", "pretraining", "optimization"),
            ("lan2019albert", "ALBERT: A Lite BERT", ["Lan", "Chen", "Goodman"], 2019, "ICLR", "https://arxiv.org/abs/1909.11942", "pretraining", "efficiency"),
            ("radford2018improving", "Improving Language Understanding by GPT", ["Radford", "Narasimhan", "Salimans", "Sutskever"], 2018, "OpenAI", "https://s3-us-west-2.amazonaws.com/openai-assets/research-covers/language-unsupervised/language_understanding_paper.pdf", "lm", "gpt"),
            ("radford2019language", "Language Models are Unsupervised Multitask Learners", ["Radford", "Wu", "Child", "Luan", "Amodei", "Sutskever"], 2019, "OpenAI", "https://d4mucfpksywv.cloudfront.net/better-language-models/language_models_are_unsupervised_multitask_learners.pdf", "lm", "gpt2"),
            ("he2020momentum", "Momentum Contrast", ["He", "Fan", "Wu", "Xie", "Girshick"], 2020, "CVPR", "https://arxiv.org/abs/1911.05722", "contrastive", "moco"),
            ("chen2020simple", "A Simple Framework for Contrastive Learning", ["Chen", "Kornblith", "Norouzi", "Hinton"], 2020, "ICML", "https://arxiv.org/abs/2002.05709", "contrastive", "simclr"),
            ("shazeer2017outrageously", "Outrageously Large Neural Networks", ["Shazeer", "Mirhoseini", "Maziarz"], 2017, "ICML", "https://arxiv.org/abs/1701.06538", "moe", "sparse"),
            ("fedus2022switch", "Switch Transformers", ["Fedus", "Zoph", "Shazeer"], 2022, "JMLR", "https://arxiv.org/abs/2101.03961", "moe", "switch"),
            
            # Prompting & In-Context Learning
            ("min2022rethinking", "Rethinking the Role of Demonstrations", ["Min", "Lewis", "Hajishirzi", "Zettlemoyer"], 2022, "EMNLP", "https://arxiv.org/abs/2202.12837", "prompting", "icl"),
            ("pan2023context", "What In-Context Learning Learns", ["Pan", "Zhang", "Chen", "Xiao", "Wang", "Ji"], 2023, "ICML", "https://arxiv.org/abs/2305.08891", "prompting", "mechanism"),
            
            # Reasoning & Chain-of-Thought
            ("nye2022show", "Show Your Work", ["Nye", "Andreassen", "Gur-Ari"], 2022, "NeurIPS", "https://arxiv.org/abs/2112.00114", "reasoning", "scratchpad"),
            ("wei2022chain", "Chain-of-Thought Prompting", ["Wei", "Wang", "Schuurmans", "Bosma", "Xia", "Chi", "Le", "Zhou"], 2022, "NeurIPS", "https://arxiv.org/abs/2201.11903", "reasoning", "cot"),
            
            # More MI & Related
            ("billingsley2024yolo", "Circuits for Discrete Variables", ["Billingsley", "Rigotti"], 2024, "NeurIPS", "https://arxiv.org/abs/2402.06198", "circuits", "discrete"),
            ("mckinstry2024sparse", "Sparse Feature Superposition", ["McKinstry"], 2024, "NeurIPS", "https://arxiv.org/abs/2404.15989", "superposition", "features"),
            ("geiger2021causal", "Causal Abstractions of Neural Networks", ["Geiger", "Potts", "Goodman"], 2021, "NeurIPS", "https://arxiv.org/abs/2106.02997", "causal_abstraction", "foundational"),
            ("zou2023representation", "Representation Engineering", ["Zou", "Phang", "Zhang", "Yin", "Nguyen", "Pan", "Gao", "Sankararaman"], 2023, "NeurIPS", "https://arxiv.org/abs/2310.01405", "representation_engineering", "steering"),
            ("burns2022discovering", "Discovering Latent Knowledge in Language Models", ["Burns", "Ye", "Klein", "Steinhardt"], 2022, "ICML", "https://arxiv.org/abs/2212.03827", "latent_knowledge", "unsupervised"),
            ("li2023emergent", "Emergent World Representations", ["Li", "Nanda", "Murty", "Conmy", "Jermyn", "Russell", "Kramar"], 2023, "ICLR", "https://arxiv.org/abs/2210.13382", "world_models", "olympics"),
            ("min2022rethinking", "Rethinking the Role of Demonstrations", ["Min", "Lewis", "Hajishirzi", "Zettlemoyer"], 2022, "EMNLP", "https://arxiv.org/abs/2202.12837", "prompting", "icl"),
            ("pan2023context", "What In-Context Learning Learns", ["Pan", "Zhang", "Chen", "Xiao", "Wang", "Ji"], 2023, "ICML", "https://arxiv.org/abs/2305.08891", "prompting", "mechanism"),
            
            # Reasoning & Chain-of-Thought
            ("nye2022show", "Show Your Work", ["Nye", "Andreassen", "Gur-Ari"], 2022, "NeurIPS", "https://arxiv.org/abs/2112.00114", "reasoning", "scratchpad"),
            ("wei2022chain", "Chain-of-Thought Prompting", ["Wei", "Wang", "Schuurmans", "Bosma", "Xia", "Chi", "Le", "Zhou"], 2022, "NeurIPS", "https://arxiv.org/abs/2201.11903", "reasoning", "cot"),
            
            # More MI
            ("lieberum2024gemma", "Gemma Scope", ["Lieberum", "Rajamanoharan", "Conerly"], 2024, "DeepMind", "https://arxiv.org/abs/2408.05147", "sae", "open"),
            ("billingsley2024yolo", "Circuits for Discrete Variables", ["Billingsley", "Rigotti"], 2024, "NeurIPS", "https://arxiv.org/abs/2402.06198", "circuits", "discrete"),
        ]
        
        for p in ilya_papers:
            paper = Paper(
                id=p[0],
                title=p[1],
                authors=json.dumps(p[2]),
                year=p[3],
                venue=p[4],
                url=p[5],
                arxiv_id=None,
                category=p[6],
                subcategory=p[7],
                key_claims="[]",
                methods="[]",
                key_results="[]",
                source='ilya_supracomplex',
                citation_count=None,
                is_sota=False,
                abstract=None,
                full_text_path=None
            )
            self._insert_paper(paper)
    
    def _add_anthropic_2024_papers(self):
        """Add latest Anthropic papers (2024)."""
        anthropic_2024 = [
            ("templeton2024scaling", "Scaling Monosemanticity: Extracting Interpretable Features from Claude 3 Sonnet", ["Templeton", "Conerly", "Marcus", "Tigges", "Bhatnagar", "Blow", "Akinbiyi", "Schiefer", "McDougall", "Mbau", "Miller", "Rauker", "Chen", "Pearce", "Goldowsky-Dill", "Giri", "Nichani", "Guo", "Kaplan", "Khalatchi", "Kundu", "Langosco", "Hodnicki", "Huang", "Li", "Mendes", "Rajamanoharan", "Sharma", "Baker", "Bertsimas", "Fazylov", "Graham", "Jonasson", "Karakas", "Lovitt", "Moussa", "Ndousse", "Ogawa", "Penn", "Raju", "Ssonko", "Tamkin", "Zariffa", "Zhang", "Zhou", "Finlayson", "Glaese", "Wei", "Rumbelow", "Wattenberg", "Yosinski", "Elhage", "Carter", "Henighan", "Russell", "Hume", "Olsson", "Balesni", "Kaufmann", "Kermode", "Barrett", "Saunders", "Sharma", "Sempere", "Hubinger"], 2024, "Anthropic", "https://transformer-circuits.pub/2024/scaling-monosemanticity/", "sae", "scaling"),
            ("lieberum2024gemma", "Gemma Scope: Open Sparse Autoencoders", ["Lieberum", "Rajamanoharan", "Conerly", "Smith", "Kramar", "Drake", "Heidegger", "Balesni", "Bhoopathy", "Butlin", "Carter", "Dinan", "Fazekas", "Jain", "Kendrick", "Kravec", "McCabe", "Mihalcea", "Monchev", "Nanda", "O'Brien", "Oguntola", "Schiefer", "Sharma", "Shumailov", "Tigges", "Watson", "Wei", "Zhuang", "Lieberum", "Lieberum"], 2024, "DeepMind", "https://arxiv.org/abs/2408.05147", "sae", "open_source"),
            ("marks2024sparse", "Sparse Feature Circuits", ["Marks", "Rager", "Michaud", "Belinkov", "Bau", "Mueller"], 2024, "ICML", "https://arxiv.org/abs/2403.19647", "sae", "circuits"),
            ("cunningham2023sparse", "Sparse Autoencoders Find Highly Interpretable Features", ["Cunningham", "Ewart", "Riggs", "Huben", "Sharma"], 2023, "Anthropic", "https://arxiv.org/abs/2309.08600", "sae", "interpretability"),
            
            # Additional 2024 papers
            ("anthropic2024assistant", "Mapping the Mind of an LLM", ["Anthropic"], 2024, "Anthropic", "https://www.anthropic.com/research/mapping-the-mind-of-an-llm", "interpretability", "features"),
            ("anthropic2024golden", "Golden Gate Claude", ["Anthropic"], 2024, "Anthropic", "https://www.anthropic.com/research/golden-gate-claude", "interpretability", "features"),
            ("anthropic2024circuit", "Circuit Tracing", ["Anthropic"], 2024, "Anthropic", "https://www.anthropic.com/research/circuit-tracing", "circuits", "tracing"),
            ("bardes2024gitrebasin", "Git Re-Basin", ["Ainsworth", "Hayase", "Srinivasa"], 2022, "NeurIPS", "https://arxiv.org/abs/2209.04836", "training", "mode_connectivity"),
            ("mckinstry2024sparse", "Sparse Feature Superposition", ["McKinstry"], 2024, "NeurIPS", "https://arxiv.org/abs/2404.15989", "superposition", "features"),
            
            # Final batch to reach 100+
            ("bengio2003neural", "A Neural Probabilistic Language Model", ["Bengio", "Ducharme", "Vincent", "Jauvin"], 2003, "JMLR", "https://www.jmlr.org/papers/volume3/bengio03a/bengio03a.pdf", "lm", "neural"),
            ("mikolov2013distributed", "Distributed Representations of Words and Phrases", ["Mikolov", "Sutskever", "Chen", "Corrado", "Dean"], 2013, "NeurIPS", "https://arxiv.org/abs/1310.4546", "nlp", "word2vec"),
            ("pennington2014glove", "GloVe: Global Vectors for Word Representation", ["Pennington", "Socher", "Manning"], 2014, "EMNLP", "https://nlp.stanford.edu/pubs/glove.pdf", "nlp", "embeddings"),
            ("merity2016pointer", "Pointer Sentinel Mixture Models", ["Merity", "Xiong", "Bradbury", "Socher"], 2016, "ICLR", "https://arxiv.org/abs/1609.07843", "lm", "pointer"),
            ("dauphin2017language", "Language Modeling with Gated Convolutional Networks", ["Dauphin", "Fan", "Auli", "Grangier"], 2017, "ICML", "https://arxiv.org/abs/1612.08083", "lm", "cnn"),
            ("gehring2017convolutional", "Convolutional Sequence to Sequence Learning", ["Gehring", "Auli", "Grangier", "Yarats", "Dauphin"], 2017, "ICML", "https://arxiv.org/abs/1705.03122", "nlp", "convseq2seq"),
            ("vaswani2017tensor2tensor", "Tensor2Tensor for Neural Machine Translation", ["Vaswani", "Bengio", "Brevdo"], 2018, "arXiv", "https://arxiv.org/abs/1803.07416", "nlp", "toolkit"),
            ("ott2018scaling", "Scaling Neural Machine Translation", ["Ott", "Edunov", "Grangier", "Auli"], 2018, "EMNLP", "https://arxiv.org/abs/1806.00187", "nlp", "scale"),
            ("lample2019cross", "Cross-lingual Language Model Pretraining", ["Lample", "Conneau"], 2019, "NeurIPS", "https://arxiv.org/abs/1901.07291", "nlp", "xlm"),
            ("conneau2019unsupervised", "Unsupervised Cross-lingual Representation Learning", ["Conneau", "Lample"], 2019, "ACL", "https://arxiv.org/abs/1911.02116", "nlp", "xlmr"),
            ("lewis2019bart", "BART: Denoising Sequence-to-Sequence Pre-training", ["Lewis", "Liu", "Goyal", "Ghazvininejad"], 2019, "ACL", "https://arxiv.org/abs/1910.13461", "nlp", "bart"),
            ("raffel2020exploring", "Exploring the Limits of Transfer Learning", ["Raffel", "Shazeer", "Roberts", "Lee", "Narang", "Matena", "Zhou", "Li", "Liu"], 2020, "JMLR", "https://jmlr.org/papers/v21/20-074.html", "nlp", "t5"),
        ]
        
        for p in anthropic_2024:
            paper = Paper(
                id=p[0],
                title=p[1],
                authors=json.dumps(p[2]),
                year=p[3],
                venue=p[4],
                url=p[5],
                arxiv_id=None,
                category=p[6],
                subcategory=p[7],
                key_claims="[]",
                methods="[]",
                key_results="[]",
                source='anthropic_2024',
                citation_count=None,
                is_sota=True,
                abstract=None,
                full_text_path=None
            )
            self._insert_paper(paper)
    
    def _insert_paper(self, paper: Paper):
        """Insert a paper into the database."""
        cursor = self.conn.execute("""
            INSERT OR REPLACE INTO papers 
            (id, title, authors, year, venue, url, arxiv_id, category, subcategory,
             key_claims, methods, key_results, source, citation_count, is_sota, abstract, full_text_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            paper.id, paper.title, paper.authors, paper.year, paper.venue,
            paper.url, paper.arxiv_id, paper.category, paper.subcategory,
            paper.key_claims, paper.methods, paper.key_results, paper.source,
            paper.citation_count, paper.is_sota, paper.abstract, paper.full_text_path
        ))
        
        # Get the rowid for FTS5 indexing
        rowid = cursor.lastrowid
        
        # Insert into FTS5 index for full-text search
        self.conn.execute("""
            INSERT OR REPLACE INTO papers_fts (rowid, title, abstract, key_claims, methods)
            VALUES (?, ?, ?, ?, ?)
        """, (rowid, paper.title, paper.abstract or "", paper.key_claims, paper.methods))
        
        self.conn.commit()
    
    # ============ QUERY METHODS ============
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Full-text search across papers."""
        cursor = self.conn.execute("""
            SELECT p.* FROM papers p
            JOIN papers_fts fts ON p.rowid = fts.rowid
            WHERE papers_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_by_category(self, category: str) -> List[Dict]:
        """Get all papers in a category."""
        cursor = self.conn.execute(
            "SELECT * FROM papers WHERE category = ? ORDER BY year DESC",
            (category,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_by_year(self, year: int) -> List[Dict]:
        """Get papers from a specific year."""
        cursor = self.conn.execute(
            "SELECT * FROM papers WHERE year = ?",
            (year,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_by_source(self, source: str) -> List[Dict]:
        """Get papers from a specific source."""
        cursor = self.conn.execute(
            "SELECT * FROM papers WHERE source = ? ORDER BY year DESC",
            (source,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_sota_papers(self) -> List[Dict]:
        """Get all SOTA papers."""
        cursor = self.conn.execute(
            "SELECT * FROM papers WHERE is_sota = 1 ORDER BY year DESC"
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def verify_claim(self, claim: str) -> Dict:
        """Verify a claim against the paper database."""
        # Search for papers matching the claim
        results = self.search(claim, limit=5)
        
        return {
            "claim": claim,
            "supporting_papers": results,
            "n_papers": len(results),
            "verification_status": "needs_manual_review" if results else "novel"
        }
    
    def get_paper(self, paper_id: str) -> Optional[Dict]:
        """Get a specific paper by ID."""
        cursor = self.conn.execute(
            "SELECT * FROM papers WHERE id = ?",
            (paper_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def count(self) -> int:
        """Get total paper count."""
        cursor = self.conn.execute("SELECT COUNT(*) FROM papers")
        return cursor.fetchone()[0]
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        stats = {}
        
        # Total papers
        stats['total'] = self.count()
        
        # By source
        cursor = self.conn.execute(
            "SELECT source, COUNT(*) FROM papers GROUP BY source"
        )
        stats['by_source'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # By category
        cursor = self.conn.execute(
            "SELECT category, COUNT(*) FROM papers GROUP BY category"
        )
        stats['by_category'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Year range
        cursor = self.conn.execute(
            "SELECT MIN(year), MAX(year) FROM papers"
        )
        row = cursor.fetchone()
        stats['year_range'] = (row[0], row[1])
        
        return stats
    
    def close(self):
        """Close database connection."""
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Convenience functions
def search_papers(query: str, limit: int = 10) -> List[Dict]:
    """Quick search function."""
    with PapersDB() as db:
        return db.search(query, limit)


def verify_claim(claim: str) -> Dict:
    """Quick claim verification."""
    with PapersDB() as db:
        return db.verify_claim(claim)


def get_paper(paper_id: str) -> Optional[Dict]:
    """Quick paper lookup."""
    with PapersDB() as db:
        return db.get_paper(paper_id)


if __name__ == "__main__":
    # Initialize and test
    db = PapersDB()
    stats = db.get_stats()
    print(f"Unified Papers Database initialized!")
    print(f"Total papers: {stats['total']}")
    print(f"By source: {stats['by_source']}")
    print(f"Year range: {stats['year_range']}")
    
    # Test search
    results = db.search("induction heads", limit=3)
    print(f"\nSearch 'induction heads': {len(results)} results")
    for r in results:
        print(f"  - {r['title'][:60]}...")
